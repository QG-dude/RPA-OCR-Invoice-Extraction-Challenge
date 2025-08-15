FROM python:3.11-slim

# Copy Python dependencies file into the image
COPY requirements.txt .

# Install Python packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY invoiceExtractionChallenge.py .

CMD ["python", "invoiceExtractionChallenge.py"]