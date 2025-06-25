# app.py - Medical Report Analysis System (cleaned version)
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import time
import os
from typing import Dict, Any, Optional
import json  # Needed for saving results
from config import Config
from ocr import ocr_processor
from nlp import nlp_processor

app = Flask(__name__)
Config.init_app(app)

# Error Handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"status": "error", "message": "Bad request"}), 400

@app.errorhandler(500)
def server_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# Helper Functions
def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_unique_filename(filename: str) -> str:
    return f"{int(time.time())}_{uuid.uuid4().hex[:8]}_{secure_filename(filename)}"

def validate_report_content(text: str) -> Optional[Dict]:
    """Validate that extracted text contains medical content"""
    if len(text.strip()) < 50:
        return {"status": "error", "message": "Report too short or unreadable"}
    medical_keywords = ['report', 'patient', 'diagnosis', 'findings', 'test', 'result']
    if not any(keyword in text.lower() for keyword in medical_keywords):
        return {"status": "error", "message": "Document doesn't appear to be a medical report"}
    return None

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint for uploading and processing medical reports"""
    if 'report' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files['report']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": f"Invalid file type. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        }), 400

    try:
        # Save the uploaded file with unique filename
        filename = generate_unique_filename(file.filename)
        file_path = Config.UPLOAD_FOLDER / filename
        file.save(file_path)
        print(f"DEBUG: File saved to {file_path}")
        
        # Process the document
        extracted_text = ocr_processor.process_document(file_path)
        print(f"DEBUG: Extracted text length: {len(extracted_text)}")  # Debug 7
        
        if not extracted_text.strip():
            return jsonify({"error": "OCR failed to extract text"}), 400
        # Add early validation
        if len(extracted_text.strip()) < 20:  # More stringent check
            return jsonify({
        "status": "error",
        "message": "Insufficient text extracted",
        "debug": {
            "text_sample": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            "length": len(extracted_text)
        }
    }), 400
        # Validate report content
        if validation := validate_report_content(extracted_text):
            return jsonify(validation), 400

        # Analyze with NLP
        analysis = nlp_processor.process_text(extracted_text)
        
        # Generate structured response
        response = {
            "status": "success",
            "report_id": str(uuid.uuid4()),
            "filename": filename,
            "analysis": analysis,
            "metadata": {
                "processing_time": time.time(),
                "text_length": len(extracted_text),
                "pages": extracted_text.count('\n\n') + 1
            }
        }

        # Save results for future reference (in a real app, store in database)
        results_path = Config.UPLOAD_FOLDER / f"{filename}.results.json"
        with open(results_path, 'w') as f:
            json.dump(response, f)

        return jsonify(response)

    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to process document",
            "error": str(e)
        }), 500

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Endpoint for direct text analysis (no OCR)"""
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text or len(text) < 50:
        return jsonify({"status": "error", "message": "Text too short"}), 400

    try:
        analysis = nlp_processor.process_text(text)
        return jsonify({
            "status": "success",
            "analysis": analysis,
            "metadata": {
                "processing_time": time.time(),
                "text_length": len(text)
            }
        })
    except Exception as e:
        app.logger.error(f"Error analyzing text: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to analyze text",
            "error": str(e)
        }), 500

@app.route('/api/debug/ocr', methods=['POST'])
def debug_ocr():
    if 'report' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['report']
    temp_path = f"/tmp/debug_{file.filename}"
    file.save(temp_path)
    
    try:
        raw_text = ocr_processor.process_document(temp_path)
        return jsonify({
            "raw_text": raw_text,
            "length": len(raw_text),
            "preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
        })
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
            
            
@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Mock patient profile endpoint"""
    return jsonify({
        "status": "success",
        "profile": {
            "patient_id": "PAT-789012",
            "name": "Jane Doe",
            "age": 35,
            "gender": "Female",
            "last_visit": "2023-05-15",
            "conditions": ["Hypertension", "Type 2 Diabetes"]
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # Add this to app.py temporarily
    print("=== OCR OUTPUT ===")
    print(extracted_text[:1000])
    print("\n=== NLP RESULTS ===")
    print(analysis)