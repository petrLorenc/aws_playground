# Chatbot Service Architecture

Basic setting with public and private subnets for a chatbot service.

## Subnets

### Public Subnet
- Has a route to an Internet Gateway (IGW)
- EC2 for frontend application servers
- Communicates with backend services in private subnet

### Private Subnet (Backend)
- No direct internet access
- NAT Gateway for outbound internet access (OpenAI API calls)
- EC2 for backend services

### Private Subnet (Database/Isolated)
- No route to IGW or NAT Gateway
- Gateway Endpoint for S3 access (cost-effective, no data transfer fees)
- Gateway Endpoint for DynamoDB (chat history storage)
- EC2 for preprocessing data from S3

## IAM Roles (Instance Profiles)

- **Backend EC2 Role**
    - Secrets Manager read access (OpenAI API key)
    - CloudWatch Logs write access
    - No long-term credentials (uses STS temporary credentials)

- **Preprocessing EC2 Role**
    - S3 read/write access for data processing
    - DynamoDB access for chat history
    - CloudWatch Logs write access

## VPC Endpoints

- **Gateway Endpoints** (free, use route tables)
    - S3 Gateway Endpoint
    - DynamoDB Gateway Endpoint

- **Interface Endpoints** (PrivateLink, avoid NAT costs for AWS APIs)
    - Secrets Manager Endpoint
    - CloudWatch Logs Endpoint

## Security Groups (Stateful, EC2-level)

- **Frontend SG**
    - Inbound: 80/443 from 0.0.0.0/0
    - Outbound: All traffic to Backend SG

- **Backend SG**
    - Inbound: Application port from Frontend SG only
    - Outbound: 443 to NAT Gateway (OpenAI API)
    - Outbound: 443 to Interface Endpoints

- **Database SG**
    - Inbound: DB port from Backend SG only
    - Outbound: S3/DynamoDB via Gateway Endpoints (prefix lists)

## NACLs (Stateless, Subnet-level)

- **Public Subnet NACL**
    - Inbound: Allow 80, 443, ephemeral ports
    - Outbound: Allow all to private subnet CIDR

- **Private Subnet NACL**
    - Inbound: Allow from public subnet CIDR
    - Outbound: Allow 443 (HTTPS)

- **Database Subnet NACL**
    - Inbound: Allow from private subnet CIDR only
    - Outbound: Deny all (except S3/DynamoDB prefix lists)

## Route Tables

- **Public Route Table**
    - 0.0.0.0/0 → Internet Gateway
    - Local route for VPC CIDR

- **Private Route Table**
    - 0.0.0.0/0 → NAT Gateway
    - S3/DynamoDB prefix lists → Gateway Endpoints
    - Local route for VPC CIDR

- **Database Route Table**
    - S3/DynamoDB prefix lists → Gateway Endpoints
    - Local route for VPC CIDR
    - No route to IGW or NAT