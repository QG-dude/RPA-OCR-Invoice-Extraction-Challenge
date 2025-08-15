FROM python:3.11-slim

# Install system dependencies required for Tesseract and image processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies file into the image
COPY requirements.txt .

# Install Python packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code into the container
COPY app/ /app
WORKDIR /app

# Define the command to run the Flask microservice
CMD ["python", "main.py"]