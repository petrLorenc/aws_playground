# =============================================================================
# CHATBOT SERVICE INFRASTRUCTURE
# A 3-tier VPC architecture for learning AWS and Terraform
# =============================================================================

provider "aws" {
  profile = "pluralsight-dev"
  region  = var.aws_region
}

# -----------------------------------------------------------------------------
# VARIABLES
# -----------------------------------------------------------------------------

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for tagging"
  type        = string
  default     = "chatbot"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Using data source to get the latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# =============================================================================
# VPC - Virtual Private Cloud
# Logically isolated network where all resources live
# =============================================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true  # Required for VPC endpoints
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# =============================================================================
# SUBNETS
# Segments of the VPC - each subnet lives in one Availability Zone
# Remember: AWS reserves 5 IPs per subnet (network, router, DNS, future, broadcast)
# =============================================================================

# PUBLIC SUBNET - Has route to Internet Gateway
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"  # 251 usable IPs
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true  # Instances get public IP automatically

  tags = {
    Name = "${var.project_name}-public-subnet"
    Tier = "Public"
  }
}

# PRIVATE SUBNET (Backend) - NAT Gateway for outbound internet (OpenAI API)
resource "aws_subnet" "private_backend" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-private-backend-subnet"
    Tier = "Private"
  }
}

# PRIVATE SUBNET (Database/Isolated) - No internet access at all
resource "aws_subnet" "private_database" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-private-database-subnet"
    Tier = "Isolated"
  }
}

# =============================================================================
# INTERNET GATEWAY
# Allows public subnet to communicate with the internet
# =============================================================================

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# =============================================================================
# NAT GATEWAY
# Allows private subnet to make outbound internet calls (e.g., OpenAI API)
# Requires an Elastic IP
# =============================================================================

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-nat-eip"
  }

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id  # NAT Gateway lives in PUBLIC subnet

  tags = {
    Name = "${var.project_name}-nat-gw"
  }

  depends_on = [aws_internet_gateway.main]
}

# =============================================================================
# ROUTE TABLES
# Define where network traffic is directed
# =============================================================================

# PUBLIC ROUTE TABLE - Routes to Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# PRIVATE ROUTE TABLE (Backend) - Routes to NAT Gateway for internet access
resource "aws_route_table" "private_backend" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-private-backend-rt"
  }
}

resource "aws_route_table_association" "private_backend" {
  subnet_id      = aws_subnet.private_backend.id
  route_table_id = aws_route_table.private_backend.id
}

# DATABASE ROUTE TABLE - No internet route, only local + Gateway Endpoints
resource "aws_route_table" "private_database" {
  vpc_id = aws_vpc.main.id
  # No route to 0.0.0.0/0 - completely isolated from internet
  # Gateway Endpoints will add routes automatically via route_table_ids

  tags = {
    Name = "${var.project_name}-private-database-rt"
  }
}

resource "aws_route_table_association" "private_database" {
  subnet_id      = aws_subnet.private_database.id
  route_table_id = aws_route_table.private_database.id
}

# =============================================================================
# VPC ENDPOINTS
# Private connectivity to AWS services without using internet
# =============================================================================

# GATEWAY ENDPOINTS (Free, use route tables)
# Only available for S3 and DynamoDB

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"

  # Associate with route tables - adds prefix list route automatically
  route_table_ids = [
    aws_route_table.private_backend.id,
    aws_route_table.private_database.id
  ]

  tags = {
    Name = "${var.project_name}-s3-endpoint"
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.private_backend.id,
    aws_route_table.private_database.id
  ]

  tags = {
    Name = "${var.project_name}-dynamodb-endpoint"
  }
}

# INTERFACE ENDPOINTS (PrivateLink - costs money but avoids NAT Gateway fees)
# Creates ENI in your subnet with private IP

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_backend.id]
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true  # Allows using default service DNS names

  tags = {
    Name = "${var.project_name}-secretsmanager-endpoint"
  }
}

resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_backend.id]
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name = "${var.project_name}-cloudwatch-logs-endpoint"
  }
}

# =============================================================================
# SECURITY GROUPS (Stateful - return traffic automatically allowed)
# Virtual firewalls at the EC2/ENI level
# =============================================================================

# FRONTEND SECURITY GROUP
resource "aws_security_group" "frontend" {
  name        = "${var.project_name}-frontend-sg"
  description = "Security group for frontend servers"
  vpc_id      = aws_vpc.main.id

  # Inbound: Allow HTTP/HTTPS from internet
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound: Restricted to only what's needed (principle of least privilege)
  # Option 1: Reference backend Security Group (preferred - more dynamic)
  egress {
    description     = "To backend API"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }
  # Trade-off: The frontend needs 443 for outbound HTTPS (yum updates, API calls) - it is not reachable in this setting 
  # Need to allow explicitly
  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Option 2: You could also use CIDR (less flexible, but works)
  # egress {
  #   description = "To backend subnet"
  #   from_port   = 8080
  #   to_port     = 8080
  #   protocol    = "tcp"
  #   cidr_blocks = ["10.0.2.0/24"]  # aws_subnet.private_backend.cidr_block
  # }
  # Option 3: Allow all outbound (less secure)
  # egress {
  #   description = "All outbound"
  #   from_port   = 0
  #   to_port     = 0
  #   protocol    = "-1"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  # DNS resolution (needed for hostname lookups)
  egress {
    description = "DNS UDP"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = [var.vpc_cidr]  # VPC DNS server
  }

  egress {
    description = "DNS TCP"
    from_port   = 53
    to_port     = 53
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name = "${var.project_name}-frontend-sg"
  }
}

# BACKEND SECURITY GROUP
resource "aws_security_group" "backend" {
  name        = "${var.project_name}-backend-sg"
  description = "Security group for backend servers"
  vpc_id      = aws_vpc.main.id

  # Inbound: Only from frontend security group (reference SG by ID!)
  ingress {
    description     = "Application traffic from frontend"
    from_port       = 8080  # Application port
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend.id]
  }

  # Outbound: HTTPS for OpenAI API and AWS endpoints
  egress {
    description = "HTTPS outbound (OpenAI API, AWS services)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-backend-sg"
  }
}

# DATABASE/PREPROCESSING SECURITY GROUP
resource "aws_security_group" "database" {
  name        = "${var.project_name}-database-sg"
  description = "Security group for database/preprocessing servers"
  vpc_id      = aws_vpc.main.id

  # Inbound: Only from backend security group
  ingress {
    description     = "Access from backend"
    from_port       = 5432  # Example: PostgreSQL port
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  # Outbound: Only to S3/DynamoDB via Gateway Endpoints (uses prefix lists)
  egress {
    description     = "S3 access via Gateway Endpoint"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [aws_vpc_endpoint.s3.prefix_list_id]
  }

  egress {
    description     = "DynamoDB access via Gateway Endpoint"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [aws_vpc_endpoint.dynamodb.prefix_list_id]
  }

  tags = {
    Name = "${var.project_name}-database-sg"
  }
}

# VPC ENDPOINTS SECURITY GROUP
resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.project_name}-vpc-endpoints-sg"
  description = "Security group for VPC Interface Endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name = "${var.project_name}-vpc-endpoints-sg"
  }
}

# =============================================================================
# NETWORK ACLs (Stateless - must allow return traffic explicitly)
# Subnet-level firewalls - first matching rule wins
# For simple setups, Security Groups alone are often enough. NACLs add complexity due to:
# 
#  * Stateless (must allow ephemeral ports 1024-65535)
#  * Rule number ordering matters
#  * Harder to debug
#
#
# Internet → NACL (subnet boundary) → Security Group (instance) → EC2
#              ↑                           ↑
#         First line of defense      Second line of defense
#
# Security Groups = "Who can talk to this instance?"
# NACLs = "What traffic is allowed into/out of this subnet?"
# =============================================================================

# PUBLIC SUBNET NACL
resource "aws_network_acl" "public" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = [aws_subnet.public.id]

  # Inbound Rules
  ingress {
    rule_no    = 100
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }

  ingress {
    rule_no    = 110
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Ephemeral ports for return traffic (stateless!)
  ingress {
    rule_no    = 120
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Outbound Rules
  egress {
    rule_no    = 100
    protocol   = "-1"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "${var.project_name}-public-nacl"
  }
}

# PRIVATE BACKEND SUBNET NACL
resource "aws_network_acl" "private_backend" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = [aws_subnet.private_backend.id]

  # Inbound: From public subnet
  ingress {
    rule_no    = 100
    protocol   = "tcp"
    action     = "allow"
    cidr_block = aws_subnet.public.cidr_block # reference to 10.0.1.0/24
    from_port  = 8080
    to_port    = 8080
  }

  # Ephemeral ports for return traffic
  ingress {
    rule_no    = 110
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Outbound: HTTPS
  egress {
    rule_no    = 100
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Ephemeral ports for outbound connections
  egress {
    rule_no    = 110
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  tags = {
    Name = "${var.project_name}-private-backend-nacl"
  }
}

# DATABASE SUBNET NACL (Most restrictive)
resource "aws_network_acl" "private_database" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = [aws_subnet.private_database.id]

  # Inbound: Only from backend subnet
  ingress {
    rule_no    = 100
    protocol   = "tcp"
    action     = "allow"
    cidr_block = aws_subnet.private_backend.cidr_block
    from_port  = 5432
    to_port    = 5432
  }

  # EC2 (10.0.3.x) ──────────────────────────────► S3 (via Gateway Endpoint)
  #       Source Port: 52847 (random ephemeral)
  #       Dest Port: 443
  # 
  #              ◄────────────────────────────── S3 Response
  #       Dest Port: 52847 (the same random port!)
  #       Source Port: 443
  # 
  # When your EC2 makes an outbound connection:
  #   Destination port: 443 (HTTPS to S3)
  #   Source port: Random port from 1024-65535 (chosen by the OS)
  # 
  # The response comes back:
  #   Destination port: That same random port (e.g., 52847)
  #   Source port: 443
  #
  # Ephemeral for return traffic from S3/DynamoDB
  ingress {
    rule_no    = 110
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0" # Can't predict source IP
    from_port  = 1024 # Can't predict which port will be used
    to_port    = 65535
  }

  # Outbound: HTTPS for Gateway Endpoints
  egress {
    rule_no    = 100
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Ephemeral ports
  egress {
    rule_no    = 110
    protocol   = "tcp"
    action     = "allow"
    cidr_block = aws_subnet.private_backend.cidr_block
    from_port  = 1024
    to_port    = 65535
  }

  tags = {
    Name = "${var.project_name}-private-database-nacl"
  }
}

# =============================================================================
# IAM ROLES & INSTANCE PROFILES
# No long-term credentials - EC2 uses STS temporary credentials
# =============================================================================

# BACKEND EC2 ROLE
resource "aws_iam_role" "backend" {
  name = "${var.project_name}-backend-role"

  # Trust policy: Who can assume this role - in this case, EC2 instances
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com" # could be also another users, lambda, etc.
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-backend-role"
  }
}

# Backend permissions policy - what this role can do
resource "aws_iam_role_policy" "backend" {
  name = "${var.project_name}-backend-policy"
  role = aws_iam_role.backend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "SecretsManagerRead"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*"  # In production, restrict to specific secret ARN
      },
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Instance profile - attaches role to EC2
#  - attach roles to EC2 instances for secure access to AWS services
#   without hardcoding credentials - for example, an EC2 instance 
#   can assume a role to access S3 buckets or Secret Manager securely
resource "aws_iam_instance_profile" "backend" {
  name = "${var.project_name}-backend-profile"
  role = aws_iam_role.backend.name
}

# PREPROCESSING EC2 ROLE
resource "aws_iam_role" "preprocessing" {
  name = "${var.project_name}-preprocessing-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-preprocessing-role"
  }
}

resource "aws_iam_role_policy" "preprocessing" {
  name = "${var.project_name}-preprocessing-policy"
  role = aws_iam_role.preprocessing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3Access"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = "*"  # In production, restrict to specific bucket
      },
      {
        Sid    = "DynamoDBAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = "*"  # In production, restrict to specific table
      },
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "preprocessing" {
  name = "${var.project_name}-preprocessing-profile"
  role = aws_iam_role.preprocessing.name
}

# =============================================================================
# EC2 INSTANCES
# Actual compute resources - using instance profiles for IAM roles
# =============================================================================

# FRONTEND INSTANCE (Public Subnet)
resource "aws_instance" "frontend" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.frontend.id]
  associate_public_ip_address = true
  # No instance profile = No AWS permissions = Smaller attack surface
   
  tags = {
    Name = "${var.project_name}-frontend"
    Tier = "Frontend"
  }
}

# BACKEND INSTANCE (Private Backend Subnet)
resource "aws_instance" "backend" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.private_backend.id
  vpc_security_group_ids = [aws_security_group.backend.id]
  iam_instance_profile   = aws_iam_instance_profile.backend.name

  tags = {
    Name = "${var.project_name}-backend"
    Tier = "Backend"
  }
}

# PREPROCESSING INSTANCE (Database/Isolated Subnet)
resource "aws_instance" "preprocessing" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.private_database.id
  vpc_security_group_ids = [aws_security_group.database.id]
  iam_instance_profile   = aws_iam_instance_profile.preprocessing.name

  tags = {
    Name = "${var.project_name}-preprocessing"
    Tier = "Database"
  }
}

# =============================================================================
# OUTPUTS
# Useful information after terraform apply
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "frontend_public_ip" {
  description = "Frontend instance public IP"
  value       = aws_instance.frontend.public_ip
}

output "nat_gateway_ip" {
  description = "NAT Gateway public IP (outbound IP for private subnet)"
  value       = aws_eip.nat.public_ip
}