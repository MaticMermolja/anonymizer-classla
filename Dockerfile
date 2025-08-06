# Use Python 3.11 slim image for minimal size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for CLASSLA and PyTorch
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the anonymizer code
COPY comprehensive_gdpr_anonymizer.py .

# Create a simple API server
COPY docker_api.py .

# Copy CLASSLA models (pre-downloaded locally)
COPY classla_resources /data/classla_resources

# Copy startup script
COPY startup.py .

# Set environment variables for better performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV CLASSLA_RESOURCES_DIR=/data/classla_resources
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4

# Expose port
EXPOSE 8000

# Run the API server
CMD ["python", "startup.py"] 