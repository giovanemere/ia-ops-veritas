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
COPY veritas_unified_service.py .
COPY config.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Create directories
RUN mkdir -p data logs

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -m appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8869

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8869/health || exit 1

CMD ["python", "veritas_unified_service.py"]
