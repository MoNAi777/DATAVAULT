FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Create storage directories
RUN mkdir -p storage/photos storage/videos storage/audio storage/documents

CMD ["python", "telegram_bot_simple.py"] 