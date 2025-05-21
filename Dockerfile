FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy just requirements first to leverage Docker cache
COPY requirements.txt .
# Use pip to install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command to run when the container starts
CMD ["uvicorn", "src.instabids.api.main:app", "--host", "0.0.0.0", "--port", "8000"]