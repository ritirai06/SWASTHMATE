# app.py - Integrated Medical Report Analysis System

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid, time, os, json, re
from typing import Dict, Optional
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from nlpengine import analyze_medical_text
from ocr import MedicalOCR
from nlp import MedicalNLP
from recom_engine import symptoms_recommendations

# Flask App
app = Flask(__name__)

# === Configuration Class ===
class Config:
    UPLOAD_FOLDER = Path('uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    AZURE_ENDPOINT = "https://myocrfree.cognitiveservices.azure.com/"
    AZURE_KEY = "47TcrLf4fZahZqwfhE1yCRFLow9SrdIa8Nz6Y8Zx0dWoesZjKfAWJQQJ99BFACLArgHXJ3w3AAAFACOGpjDp"

     # AWS Medical NLP configuration
    AWS_ACCESS_KEY = 'AKIAXKPUZ7JSCHEQLHEB'
    AWS_SECRET_KEY = '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'

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    ocr_engine = MedicalOCR()
    nlp_engine = MedicalNLP()

    @classmethod
    def init_app(cls, app):
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH

Config.init_app(app)

# Azure OCR client
azure_client = ComputerVisionClient(
    Config.AZURE_ENDPOINT,
    CognitiveServicesCredentials(Config.AZURE_KEY)
)

# === Utility Functions ===

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_unique_filename(filename: str) -> str:
    return f"{int(time.time())}_{uuid.uuid4().hex[:8]}_{secure_filename(filename)}"

def validate_report_content(text: str) -> Optional[Dict]:
    if len(text.strip()) < 50:
        return {"status": "error", "message": "Report too short or unreadable"}
    medical_keywords = ['report', 'patient', 'diagnosis', 'findings', 'test', 'result']
    if not any(keyword in text.lower() for keyword in medical_keywords):
        return {"status": "error", "message": "Document doesn't appear to be a medical report"}
    return None

def extract_text_azure(image_path):
    with open(image_path, "rb") as image_stream:
        read_response = azure_client.read_in_stream(image_stream, raw=True)
    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    while True:
        result = azure_client.get_read_result(operation_id)
        if result.status.lower() not in ["notstarted", "running"]:
            break
        time.sleep(1)

    text = ""
    if result.status == "succeeded":
        for page in result.analyze_result.read_results:
            for line in page.lines:
                text += line.text + "\n"
    return text.strip()

# === Routes ===

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route("/upload", methods=["POST"])
def upload_file_report():
    if "report" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files["report"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    report_id = str(uuid.uuid4())
    saved_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{report_id}_{filename}")
    file.save(saved_path)

    try:
        extracted_text = Config.ocr_engine.process_document(saved_path)
        if not extracted_text.strip():
            return jsonify({"status": "error", "message": "No text extracted"}), 400

        analysis = Config.nlp_engine.process_text(extracted_text)
        diseases = analysis.get("diseases", [])
        specialization = analysis.get("specialization", "")
        measurements = analysis.get("measurements", {})

        disease_names = [d.lower() for d in diseases]
        normalized_recommendations = {k.lower(): v for k, v in symptoms_recommendations.items()}
        recommendations = list({rec for d in disease_names for rec in normalized_recommendations.get(d, [])})

        result_data = {
            "status": "success",
            "report_id": report_id,
            "filename": filename,
            "extracted_text": extracted_text,
            "analysis": analysis,
            "recommendations": recommendations
        }

        result_json_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{report_id}.results.json")
        with open(result_json_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2)

        return jsonify(result_data)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return text.strip()

# === API Endpoints ===

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
        
        # Process the document using Azure OCR
        extracted_text = extract_text_azure(file_path)
        
        if not extracted_text.strip():
            return jsonify({"error": "OCR failed to extract text"}), 400
            
        if len(extracted_text.strip()) < 20:
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
        analysis = analyze_medical_text(extracted_text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)
        
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

        # Save results for future reference
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
        analysis = analyze_medical_text(text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)
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
    """Debug endpoint for OCR testing"""
    if 'report' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['report']
    temp_path = f"/tmp/debug_{file.filename}"
    file.save(temp_path)
    
    try:
        raw_text = extract_text_azure(temp_path)
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
    
@app.route('/analyze', methods=['POST'])
def analyze():
    # Get file and process it
    file = request.files['report']
    text = extract_text_from_file(file)
    result = analyze_text_with_nlp(text)

    # Pass result to frontend via session/localStorage or template
    return render_template('analysis.html', result=result)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Alternative upload endpoint from main.py"""
    print("📥 Received request at /upload_image")

    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    os.makedirs('temp', exist_ok=True)
    image_path = os.path.join('temp', image.filename)
    image.save(image_path)

    try:
        text = extract_text_azure(image_path)
        print(f"📝 OCR Extracted Text:\n{text}")

        if not text.strip():
            return jsonify({'error': 'No text extracted'}), 400

        nlp_results = analyze_medical_text(text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)
        return jsonify({'text': text, 'nlp_results': nlp_results})

    except Exception as e:
        import traceback
        print("❌ Exception occurred:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

# === Error Handlers ===
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"status": "error", "message": "Bad request"}), 400

@app.errorhandler(500)
def server_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500



@app.route('/MedAssist')
def analysis():
    return render_template('MedAssist.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# === Run the App ===
if __name__ == "__main__":
    app.run(debug=True)
