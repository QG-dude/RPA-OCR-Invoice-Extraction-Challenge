from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
# Initialize Flask app
app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr():
    # Check if an image file was uploaded
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    try:
        # Open the image and perform OCR using Tesseract
        image = Image.open(image_file.stream)
        text = pytesseract.image_to_string(image, lang='eng')
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': 'OCR failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)