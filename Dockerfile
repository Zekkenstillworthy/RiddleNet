# Dockerfile for testing RiddleNet with Gunicorn (Linux environment)
# Use this to test Gunicorn compatibility on Windows via Docker

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=false

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs static/uploads instance

# Create a basic .env file for testing
RUN echo "SECRET_KEY=test-secret-key-for-docker" > .env && \
    echo "FLASK_ENV=production" >> .env && \
    echo "FLASK_DEBUG=false" >> .env && \
    echo "DATABASE_URL=sqlite:///test.db" >> .env

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
