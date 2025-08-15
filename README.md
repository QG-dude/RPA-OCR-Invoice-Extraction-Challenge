# RPA Invoice Extraction Challenge

This project automates the RPA Challenge (invoice extraction) using Selenium, OCR (Tesseract), and Python — fully containerized with Docker.

https://rpachallengeocr.azurewebsites.net/


## Project Structure

```
RPA-OCR-Invoice-Extraction-Challenge
├── docker-compose.yml              # Docker orchestration for all services
├── README.md                       
├── rpa-ocr-challenge/              # Service that automates the RPA invoice challenge
│   ├── Dockerfile
│   ├── invoiceExtractionChallenge.py
│   └── requirements.txt
└── tesseract-ocr/                  # Custom OCR microservice
    ├── app/
    ├── Dockerfile
    └── requirements.txt
```


## Installation

```
# Clone the GitHub repository to your local machine
git clone https://github.com/QG-dude/RPA-OCR-Invoice-Extraction-Challenge.git

# Navigate into the project directory
cd RPA-OCR-Invoice-Extraction-Challenge

# Start Selenium and OCR services
docker compose up -d selenium-chrome tesseract-ocr

# Open the VNC interface
# Linux/macOS
xdg-open "http://localhost:7900/?autoconnect=1&resize=scale&password=secret" > /dev/null 2>&1 & disown
# or
open "http://localhost:7900/?autoconnect=1&resize=scale&password=secret" > /dev/null 2>&1 & disown
# or
sensible-browser "http://localhost:7900/?autoconnect=1&resize=scale&password=secret" > /dev/null 2>&1 & disown
# Windows
Start-Process "http://localhost:7900/?autoconnect=1&resize=scale&password=secret"

# Launch the main automation service
docker compose up -d rpa-ocr-challenge
```


## Demo

https://github.com/user-attachments/assets/08a9e415-1b7a-45ec-a33d-686df79052b0
