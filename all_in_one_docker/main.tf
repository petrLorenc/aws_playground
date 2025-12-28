# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

#------------------------------------------------------------------------------
# VPC
#------------------------------------------------------------------------------
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${local.name_prefix}-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_prefix}-igw"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = {
    Name = "${local.name_prefix}-public-subnet"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${local.name_prefix}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

#------------------------------------------------------------------------------
# Security Group
#------------------------------------------------------------------------------
resource "aws_security_group" "app" {
  name        = "${local.name_prefix}-app-sg"
  description = "Security group for Docker Compose application"
  vpc_id      = aws_vpc.main.id

  # HTTP
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-app-sg"
  }
}

#------------------------------------------------------------------------------
# IAM Role for EC2
#------------------------------------------------------------------------------
resource "aws_iam_role" "ec2" {
  name = "${local.name_prefix}-ec2-role"

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
}

# SSM access for management (no SSH needed)
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# CloudWatch Logs policy
resource "aws_iam_role_policy" "cloudwatch_logs" {
  name = "${local.name_prefix}-cloudwatch-logs"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "${aws_cloudwatch_log_group.app.arn}:*"
      }
    ]
  })
}

# Secrets Manager read access
resource "aws_iam_role_policy" "secrets_manager" {
  name = "${local.name_prefix}-secrets-manager"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.app.arn
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${local.name_prefix}-ec2-profile"
  role = aws_iam_role.ec2.name
}

#------------------------------------------------------------------------------
# CloudWatch Log Group
#------------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "app" {
  name              = "/docker/${local.name_prefix}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${local.name_prefix}-logs"
  }
}

#------------------------------------------------------------------------------
# Secrets Manager
#------------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "app" {
  name                    = "${local.name_prefix}-secrets-${random_id.suffix.hex}"
  description             = "Application secrets for ${local.name_prefix}"
  recovery_window_in_days = 7

  tags = {
    Name = "${local.name_prefix}-secrets"
  }
}

# Initial secret version with placeholder values
resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DB_PASSWORD = random_password.db.result
    DB_USER     = "appuser"
    DB_NAME     = "appdb"
  })
}

resource "random_password" "db" {
  length  = 32
  special = false
}

#------------------------------------------------------------------------------
# EC2 Instance
#------------------------------------------------------------------------------
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  root_block_device {
    volume_size           = var.root_volume_size
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    docker_compose_version = var.docker_compose_version
    aws_region             = var.aws_region
    log_group_name         = aws_cloudwatch_log_group.app.name
    secret_arn             = aws_secretsmanager_secret.app.arn
  }))

  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    http_endpoint               = "enabled"
  }

  tags = {
    Name = "${local.name_prefix}-instance"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}

#------------------------------------------------------------------------------
# Route53 Record (Optional)
#------------------------------------------------------------------------------
resource "aws_route53_record" "app" {
  count   = var.create_route53_record && var.route53_zone_id != "" ? 1 : 0
  zone_id = var.route53_zone_id
  name    = var.domain_name
  type    = "A"
  ttl     = 300
  records = [aws_instance.app.public_ip]
}

#------------------------------------------------------------------------------
# CloudWatch Alarm for Instance Health
#------------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "instance_health" {
  alarm_name          = "${local.name_prefix}-instance-health"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "EC2 instance health check failed"

  dimensions = {
    InstanceId = aws_instance.app.id
  }

  tags = {
    Name = "${local.name_prefix}-health-alarm"
  }
}
