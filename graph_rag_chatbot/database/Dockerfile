# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM chatbot-base AS builder

WORKDIR /app

# Copy dependency files only
COPY pyproject.toml uv.lock* ./
COPY interfaces/pyproject.toml ./interfaces/
COPY database/pyproject.toml ./database/

# Sync dependencies for database package
RUN uv sync --package database

# Copy actual source code
COPY interfaces/src/ ./interfaces/src/
COPY database/src/ ./database/src/

# TODO: it is not working withhout this again... investigate later
RUN uv sync --package database 

CMD ["uv", "run", "uvicorn", "database.main:app", "--host", "0.0.0.0", "--port", "5555"]
