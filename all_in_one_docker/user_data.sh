#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting user data script..."

#------------------------------------------------------------------------------
# Install Docker
#------------------------------------------------------------------------------
echo "Installing Docker..."
dnf update -y
dnf install -y docker

systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
usermod -aG docker ec2-user

#------------------------------------------------------------------------------
# Install Docker Compose
#------------------------------------------------------------------------------
echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/${docker_compose_version}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create symlink for convenience
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

#------------------------------------------------------------------------------
# Install CloudWatch Agent
#------------------------------------------------------------------------------
echo "Installing CloudWatch Agent..."
dnf install -y amazon-cloudwatch-agent

# Configure CloudWatch agent for Docker logs
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<EOF
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/lib/docker/containers/*/*.log",
            "log_group_name": "${log_group_name}",
            "log_stream_name": "{instance_id}/docker-containers",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/user-data.log",
            "log_group_name": "${log_group_name}",
            "log_stream_name": "{instance_id}/user-data",
            "retention_in_days": 30
          }
        ]
      }
    }
  }
}
EOF

systemctl start amazon-cloudwatch-agent
systemctl enable amazon-cloudwatch-agent

#------------------------------------------------------------------------------
# Install AWS CLI v2
#------------------------------------------------------------------------------
echo "Installing AWS CLI v2..."
dnf install -y unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

#------------------------------------------------------------------------------
# Create application directory
#------------------------------------------------------------------------------
APP_DIR="/opt/app"
mkdir -p $APP_DIR
cd $APP_DIR

#------------------------------------------------------------------------------
# Fetch secrets from Secrets Manager
#------------------------------------------------------------------------------
echo "Fetching secrets from Secrets Manager..."
aws secretsmanager get-secret-value \
  --secret-id "${secret_arn}" \
  --region "${aws_region}" \
  --query 'SecretString' \
  --output text > /tmp/secrets.json

# Parse secrets and create .env file
DB_PASSWORD=$(cat /tmp/secrets.json | python3 -c "import sys, json; print(json.load(sys.stdin)['DB_PASSWORD'])")
DB_USER=$(cat /tmp/secrets.json | python3 -c "import sys, json; print(json.load(sys.stdin)['DB_USER'])")
DB_NAME=$(cat /tmp/secrets.json | python3 -c "import sys, json; print(json.load(sys.stdin)['DB_NAME'])")

cat > $APP_DIR/.env <<EOF
DB_PASSWORD=$DB_PASSWORD
DB_USER=$DB_USER
DB_NAME=$DB_NAME
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@database:5432/$DB_NAME
EOF

rm /tmp/secrets.json
chmod 600 $APP_DIR/.env

#------------------------------------------------------------------------------
# Create Docker Compose file
#------------------------------------------------------------------------------
cat > $APP_DIR/docker-compose.yml <<'COMPOSE'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
    networks:
      - frontend-network
    depends_on:
      - frontend
      - backend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    image: nginx:alpine
    container_name: frontend
    restart: unless-stopped
    expose:
      - "80"
    networks:
      - frontend-network
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    image: python:3.11-slim
    container_name: backend
    restart: unless-stopped
    expose:
      - "8000"
    environment:
      - DATABASE_URL=$${DATABASE_URL}
    networks:
      - frontend-network
      - backend-network
    depends_on:
      - database
    command: ["python", "-m", "http.server", "8000"]
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  database:
    image: postgres:15-alpine
    container_name: database
    restart: unless-stopped
    expose:
      - "5432"
    environment:
      - POSTGRES_USER=$${DB_USER}
      - POSTGRES_PASSWORD=$${DB_PASSWORD}
      - POSTGRES_DB=$${DB_NAME}
    networks:
      - backend-network
    volumes:
      - db-data:/var/lib/postgresql/data
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge

volumes:
  db-data:
COMPOSE

#------------------------------------------------------------------------------
# Create Nginx configuration
#------------------------------------------------------------------------------
mkdir -p $APP_DIR/nginx/certs

cat > $APP_DIR/nginx/nginx.conf <<'NGINX'
events {
    worker_connections 1024;
}

http {
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=global:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
    
    # Rate limit response
    limit_req_status 429;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    upstream frontend {
        server frontend:80;
    }

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name _;

        # Global rate limit
        limit_req zone=global burst=50 nodelay;

        # API routes - stricter limit
        location /api/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            return 200 'OK';
            add_header Content-Type text/plain;
        }
    }
}
NGINX

#------------------------------------------------------------------------------
# Set permissions
#------------------------------------------------------------------------------
chown -R ec2-user:ec2-user $APP_DIR

#------------------------------------------------------------------------------
# Start Docker Compose
#------------------------------------------------------------------------------
echo "Starting Docker Compose..."
cd $APP_DIR
docker-compose up -d

echo "User data script completed successfully!"
