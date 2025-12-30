# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM chatbot-base AS builder

WORKDIR /app

# Copy dependency files only
COPY pyproject.toml uv.lock* ./
COPY interfaces/pyproject.toml ./interfaces/
COPY backend/pyproject.toml ./backend/

# Sync dependencies for backend package
RUN uv sync --package backend 

# Copy actual source code
COPY interfaces/src/ /app/interfaces/src/
COPY backend/src/ /app/backend/src/

# TODO: it is not working withhout this again... investigate later
RUN uv sync --package backend 

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
