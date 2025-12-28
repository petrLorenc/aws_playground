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
# Create FastAPI application
#------------------------------------------------------------------------------
echo "Creating FastAPI application..."
APP_DIR="/opt/app"
mkdir -p $APP_DIR
cd $APP_DIR

# Create main.py with a basic FastAPI server
cat > $APP_DIR/main.py <<'EOF'
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import socket

app = FastAPI(title="FastAPI Server", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!", "status": "running"}


@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "hostname": socket.gethostname()}
    )


@app.get("/info")
async def info():
    return {
        "app": "FastAPI Server",
        "version": "1.0.0",
        "python_version": os.popen("python --version").read().strip(),
        "hostname": socket.gethostname()
    }
EOF

# Create requirements.txt
cat > $APP_DIR/requirements.txt <<'EOF'
fastapi==0.115.6
uvicorn[standard]==0.34.0
EOF

# Create Dockerfile
cat > $APP_DIR/Dockerfile <<'EOF'
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

#------------------------------------------------------------------------------
# Build and run the Docker container
#------------------------------------------------------------------------------
echo "Building Docker image..."
docker build -t fastapi-server $APP_DIR

echo "Running FastAPI container..."
docker run -d \
  --name fastapi-server \
  --restart always \
  -p 80:8000 \
  fastapi-server

echo "FastAPI server started successfully on port 80"
echo "User data script completed!"