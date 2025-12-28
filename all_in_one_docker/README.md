# All in one server - Docker Compose setup

This directory contains Terraform code to set up a basic AWS infrastructure for running a Docker Compose application on an EC2 instance. The setup includes VPC, subnets, security groups, IAM roles, and an EC2 instance configured to run Docker Compose.

- No Load Balancer
- No Auto Scaling

## Components

- VPC with only public subnet
- Security Groups for EC2 instance (allowing HTTP/HTTPS traffic, no ssh - using SSM instead)

```
                         ┌─────────────┐
                         │  Route 53   │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │ Elastic IP (removed)  │
                         └──────┬──────┘
                                │
Internet ──────────────► Security Group ──► EC2 Instance
                                              │
                                    ┌─────────┴─────────┐
                                    │  Docker Network   │
                                    ├───────────────────┤
                                    │ Nginx/Traefik     │ ← :80/:443
                                    │      ↓            │
                                    │ Frontend          │ ← Internal
                                    │      ↓            │
                                    │ Backend           │ ← Internal (Simplified to this container only)
                                    │      ↓            │
                                    │ Database          │ ← Internal
                                    └───────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
             ┌─────────────┐          ┌──────────────┐          ┌──────────────┐
             │ CloudWatch  │          │   Secrets    │          │     S3       │
             │    Logs     │          │   Manager    │          │   Backups    │
             └─────────────┘          └──────────────┘          └──────────────┘
```

- IAM role for EC2 with permissions to write logs to CloudWatch and read secrets from Secrets Manager, SSM access for management (no need for ssh keys)
- EC2 instance with user data to install Docker, Docker Compose, and run the application
- Cloudwatch Log Group for application logs
- Optional - Elastic IP for the EC2 instance, Route53 record to point a domain to the instance

## Docker Compose Application
The Docker Compose application consists of three services:
- Frontend: A web server serving the frontend application in React
- Backend: A FastAPI Python application serving as the backend API
- Database: A PostgreSQL database for data storage
- Reverse proxy + SSL + request limiting: Using Traefik/Nginx/Caddy to handle SSL termination and routing (it will be in development mode without HTTPS for now)