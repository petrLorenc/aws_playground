# Shared base image with Python and uv
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Conditionally add certificates if certs folder exists
# The trailing slash on certs/ and the * pattern prevents failure if empty/missing
COPY certs* /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
