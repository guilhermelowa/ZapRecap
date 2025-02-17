# Use an official Python runtime as a parent image
FROM python:3.9-slim AS backend-builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

# Copy entire project
COPY . /app

# Install frontend dependencies
WORKDIR /app/client
RUN npm install

# Build frontend
RUN npm run build

# Copy frontend build to backend static
RUN mkdir -p /app/fastapi-backend/static && \
    cp -r dist/* /app/fastapi-backend/static/

# Backend final stage
FROM python:3.9-slim

# Set working directory
WORKDIR /app/fastapi-backend

# Install backend dependencies
COPY fastapi-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application and static files
COPY fastapi-backend/ .
COPY --from=backend-builder /app/fastapi-backend/static ./static

# Expose port
EXPOSE 8000

# Use gunicorn as specified in Procfile
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_config.py"]