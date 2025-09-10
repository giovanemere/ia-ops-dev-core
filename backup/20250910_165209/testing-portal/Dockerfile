FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./
COPY *.json ./
COPY *.sh ./

# Make scripts executable
RUN chmod +x *.sh

# Create directories
RUN mkdir -p test-results logs

# Create user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port for mock services
EXPOSE 18860 18861 18862

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:18860/health || exit 1

# Default command
CMD ["python", "simple_mock.py"]
