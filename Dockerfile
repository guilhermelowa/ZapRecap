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

# Copy only necessary frontend files
COPY client/package*.json /app/client/
WORKDIR /app/client
RUN npm install

# Copy frontend source
COPY client/ /app/client/
RUN npm run build

# Copy backend files
WORKDIR /app
COPY fastapi-backend/requirements.txt /app/fastapi-backend/
RUN pip install --no-cache-dir -r /app/fastapi-backend/requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app/fastapi-backend

# Copy backend requirements and install
COPY fastapi-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY fastapi-backend/ .

# Copy built frontend static files
COPY --from=backend-builder /app/client/dist /app/fastapi-backend/static

# Expose port
EXPOSE 8000

# Use gunicorn as specified in Procfile
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_config.py"]