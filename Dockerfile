FROM python:3.12-slim

# Install system dependencies (optional, but makes pip install more robust)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Leverage Docker layer caching: first copy only requirements
COPY requirements.txt .

# Upgrade pip and install Python dependencies (with no cache)
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Use unbuffered output for better logging (esp. in production)
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]