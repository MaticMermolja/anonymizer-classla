# GDPR Anonymizer Docker Setup

A minimal Docker container that provides a REST API for GDPR-compliant data anonymization using CLASSLA NER, Google Phone Numbers, Microsoft Presidio patterns, and regional patterns.

## 🚀 **Quick Start**

### **1. Build and Run with Docker Compose (Recommended)**

```bash
# Build and start the container
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### **2. Build and Run with Docker**

```bash
# Build the image
docker build -t gdpr-anonymizer .

# Run the container
docker run -p 8000:8000 gdpr-anonymizer
```

## 📋 **API Endpoints**

### **Health Check**
```bash
GET /health
```
Returns service status and version information.

### **Service Information**
```bash
GET /info
```
Returns detailed information about anonymizer capabilities.

### **Single Text Anonymization**
```bash
POST /anonymize
```

**Request Body:**
```json
{
  "text": "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678",
  "language": "sl",
  "use_descriptive_masks": true,
  "preserve_types": []
}
```

**Response:**
```json
{
  "original_text": "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678",
  "anonymized_text": "Dr. <MASKED_PER> <MASKED_PER> (<MASKED_EMAIL>) iz <MASKED_LOC>, tel: <MASKED_PHONE>",
  "total_entities_masked": 5,
  "privacy_risk": "high",
  "detection_methods": {
    "classla_ner": 3,
    "presidio_patterns": 1,
    "google_phonenumbers": 1,
    "regional_patterns": 0
  },
  "processing_time_seconds": 0.123,
  "masked_entities": [
    {
      "original": "ana.horvat@gmail.com",
      "type": "EMAIL",
      "mask": "<MASKED_EMAIL>",
      "detection_method": "presidio_pattern",
      "confidence": "high"
    }
  ]
}
```

### **Batch Anonymization**
```bash
POST /anonymize/batch
```

**Request Body:**
```json
{
  "texts": [
    "Janez Novak (janez@email.com) živi v Ljubljani",
    "Ana Horvat iz Zagreba, tel: +385 1 234 5678"
  ],
  "language": "sl",
  "use_descriptive_masks": true
}
```

## 🎯 **Usage Examples**

### **cURL Examples**

#### **Single Text with Descriptive Masking**
```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678",
    "use_descriptive_masks": true
  }'
```

#### **Single Text with Asterisk Masking**
```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678",
    "use_descriptive_masks": false
  }'
```

#### **Preserve Specific Entity Types**
```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane",
    "use_descriptive_masks": true,
    "preserve_types": ["LOC"]
  }'
```

#### **Batch Processing**
```bash
curl -X POST http://localhost:8000/anonymize/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Janez Novak (janez@email.com) živi v Ljubljani",
      "Ana Horvat iz Zagreba, tel: +385 1 234 5678"
    ],
    "use_descriptive_masks": true
  }'
```

### **Python Examples**

#### **Single Text Anonymization**
```python
import requests

url = "http://localhost:8000/anonymize"
payload = {
    "text": "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678",
    "use_descriptive_masks": True
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Original: {result['original_text']}")
print(f"Anonymized: {result['anonymized_text']}")
print(f"Privacy Risk: {result['privacy_risk']}")
```

#### **Batch Processing**
```python
import requests

url = "http://localhost:8000/anonymize/batch"
payload = {
    "texts": [
        "Janez Novak (janez@email.com) živi v Ljubljani",
        "Ana Horvat iz Zagreba, tel: +385 1 234 5678"
    ],
    "use_descriptive_masks": True
}

response = requests.post(url, json=payload)
result = response.json()

for i, text_result in enumerate(result['results']):
    print(f"Text {i}: {text_result['anonymized_text']}")
```

## 🔧 **Configuration Options**

### **Request Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | required | Text to anonymize |
| `language` | string | "sl" | Language code (sl, hr, sr, bg) |
| `use_descriptive_masks` | boolean | false | Use descriptive tags instead of asterisks |
| `preserve_types` | array | [] | Entity types to preserve (not mask) |

### **Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `original_text` | string | Original input text |
| `anonymized_text` | string | Anonymized text |
| `total_entities_masked` | integer | Number of entities masked |
| `privacy_risk` | string | Privacy risk level (low/medium/high) |
| `detection_methods` | object | Count of entities by detection method |
| `processing_time_seconds` | float | Processing time in seconds |
| `masked_entities` | array | Details of masked entities |

## 🏷️ **Masking Types**

### **Descriptive Masking Tags**
- `<MASKED_PER>` - Person names
- `<MASKED_LOC>` - Locations
- `<MASKED_ORG>` - Organizations
- `<MASKED_EMAIL>` - Email addresses
- `<MASKED_PHONE>` - Phone numbers
- `<MASKED_CREDIT_CARD>` - Credit card numbers
- `<MASKED_IP_ADDRESS>` - IP addresses
- `<MASKED_DATE>` - Dates
- `<MASKED_URL>` - URLs
- `<MASKED_IBAN>` - IBAN numbers
- `<MASKED_PERSONAL_ID>` - Personal ID numbers
- `<MASKED_TAX_NUMBER>` - Tax numbers
- `<MASKED_BANK_ACCOUNT>` - Bank account numbers

### **Asterisk Masking**
Traditional asterisk masking where each character is replaced with `*`.

## 🐳 **Docker Configuration**

### **Environment Variables**
- `PYTHONUNBUFFERED=1` - Ensures Python output is not buffered
- `PYTHONDONTWRITEBYTECODE=1` - Prevents Python from writing .pyc files

### **Volumes**
- `classla_models` - Persists CLASSLA models between container restarts

### **Ports**
- `8000` - API server port

### **Health Check**
The container includes a health check that verifies the API is responding:
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start period: 60 seconds

## 📊 **Performance**

- **Processing speed**: ~3,000 characters/second
- **Memory usage**: ~2-4GB RAM
- **Startup time**: ~40-60 seconds (first run includes model download)
- **Subsequent runs**: ~10-20 seconds (uses cached models)

## 🧪 **Testing**

Run the test script to verify the API:

```bash
# Install requests if needed
pip install requests

# Run tests
python test_docker_api.py
```

## 🔍 **Monitoring**

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Service Information**
```bash
curl http://localhost:8000/info
```

## 🛠️ **Troubleshooting**

### **Container Won't Start**
1. Check Docker logs: `docker-compose logs`
2. Ensure port 8000 is available
3. Verify sufficient memory (at least 4GB recommended)

### **Slow Performance**
1. First run downloads models (~100-200MB)
2. Subsequent runs use cached models
3. Consider using GPU if available

### **API Errors**
1. Check request format and required fields
2. Verify text is not empty
3. Check container logs for detailed error messages

## 📈 **Scaling**

### **Multiple Instances**
```bash
# Scale to multiple instances
docker-compose up --scale gdpr-anonymizer=3
```

### **Load Balancer**
Use a load balancer (nginx, HAProxy) to distribute requests across multiple instances.

## 🔒 **Security Considerations**

- The API runs on HTTP by default
- For production, use HTTPS with proper SSL certificates
- Consider adding authentication/authorization
- Implement rate limiting for API endpoints
- Monitor and log API usage

## 📄 **License**

This project uses CLASSLA which is licensed under the Apache License 2.0. 