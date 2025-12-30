# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM chatbot-base AS builder

WORKDIR /app

# Copy dependency files only
COPY pyproject.toml uv.lock* ./
COPY interfaces/pyproject.toml ./interfaces/
COPY frontend/pyproject.toml ./frontend/

# Sync dependencies for frontend package
RUN uv sync --package frontend

# Copy actual source code
COPY interfaces/src/ ./interfaces/src/
COPY frontend/src/ ./frontend/src/

# TODO: it is not working withhout this again... investigate later
RUN uv sync --package frontend 

CMD ["uv", "run", "python", "/app/frontend/src/frontend/main.py"]
