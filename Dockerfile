# Optimal Dockerfile: Fast build + Fast runtime
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download CLASSLA models (fast - just downloads files)
RUN python -c "import classla; classla.download('sl')"

# Copy application code
COPY comprehensive_gdpr_anonymizer.py .
COPY docker_api.py .
COPY startup.py .

# Create volume for model caching
VOLUME /root/classla_resources

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Use optimized startup with caching
CMD ["python", "startup.py"] 