# app1.py - Integrated Medical Report Analysis System
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid, time, os, json
from typing import Dict, Optional
from nlpengine import analyze_medical_text
from nlp import MedicalNLP
from recom_engine import symptoms_recommendations
from flask_cors import CORS
import google.generativeai as genai
import cohere
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
# --- top of app1.py ---
from nlpengine import analyze_medical_text, clean_ocr_text, build_summary  # <== new imports
load_dotenv()

# Flask App
app = Flask(__name__)
CORS(app)

# === Configuration Class ===
class Config:
    UPLOAD_FOLDER = Path('uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Load keys securely from environment
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    AZURE_KEY = os.getenv("AZURE_KEY")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    nlp_engine = MedicalNLP()

    @classmethod
    def init_app(cls, app):
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH

Config.init_app(app)

# === Gemini Configuration ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")  # Or gemini-1.5-pro if you need higher quality


# === Cohere Configuration ===
COHERE_API_KEY =os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

# === Azure OCR client (Form Recognizer) ===
azure_client = DocumentAnalysisClient(
    endpoint=Config.AZURE_ENDPOINT,
    credential=AzureKeyCredential(Config.AZURE_KEY)
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

def extract_text_azure(file_path):
    with open(file_path, "rb") as f:
        poller = azure_client.begin_analyze_document("prebuilt-read", document=f)
    result = poller.result()

    text = ""
    for page in result.pages:
        for line in page.lines:
            text += line.content + "\n"

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
        extracted_text = extract_text_azure(saved_path)
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
        filename = generate_unique_filename(file.filename)
        file_path = Config.UPLOAD_FOLDER / filename
        file.save(file_path)
        
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
            
        if validation := validate_report_content(extracted_text):
            return jsonify(validation), 400

        analysis = analyze_medical_text(extracted_text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)
        
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
    """Web route for analyzing uploaded file"""
    file = request.files['report']
    filename = generate_unique_filename(file.filename)
    file_path = Config.UPLOAD_FOLDER / filename
    file.save(file_path)

    text = extract_text_azure(file_path)
    result = analyze_medical_text(text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)

    return render_template('analysis.html', result=result)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Alternative upload endpoint"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    os.makedirs('temp', exist_ok=True)
    image_path = os.path.join('temp', image.filename)
    image.save(image_path)

    try:
        # --- inside /upload_image route in app1.py ---
        text = extract_text_azure(image_path)
        if not text.strip():
            return jsonify({'error': 'No text extracted'}), 400

        clean_text = clean_ocr_text(text)
        nlp_results = analyze_medical_text(clean_text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)
        summary = build_summary(clean_text, nlp_results)

        return jsonify({
            'text': clean_text,
            'nlp_results': nlp_results,
            'summary': summary
        })


    except Exception as e:
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

# === Route: Ask Medical Assistant ===
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "").strip()
    language = data.get("language", "english").lower()

    if not query:
        return jsonify({"answer": "❗ Please ask a medical question."})

    if language == "hindi":
        prompt = (
            "आप एक पेशेवर AI मेडिकल असिस्टेंट हैं। उपयोगकर्ता के प्रश्न का उत्तर केवल हिंदी में दें। उत्तर को निम्नलिखित संरचना में दें:\n\n"
            "🌟 **स्थिति का सारांश** – बीमारी का संक्षिप्त विवरण\n"
            "💡 **कारण** – अधिकतम 3 बिंदु\n"
            "🔍 **लक्षण** – अधिकतम 3 बिंदु\n"
            "🩺 **उपचार** – सामान्य घरेलू उपाय और OTC दवाएं (जैसे पैरासिटामोल, ORS)\n"
            "⚠️ **डॉक्टर से कब मिलें** – 2–3 चेतावनी संकेत\n\n"
            f"प्रश्न: {query}"
        )
    else:
        prompt = (
            "You are a professional AI medical assistant. Respond in English only. Use the structure below:\n\n"
            "🌟 **Overview** – 1–2 lines summarizing the condition\n"
            "💡 **Causes** – Max 3 short bullet points\n"
            "🔍 **Symptoms** – Max 3 short bullet points\n"
            "🩺 **Treatment** – Include safe OTC medications like paracetamol or ORS\n"
            "⚠️ **When to See a Doctor** – Max 3 warning signs\n\n"
            f"User's question: {query}"
        )

    # Try Gemini first
    try:
        gemini_response = gemini_model.generate_content(prompt)
        clean_response = gemini_response.text.replace("*", "")
        return jsonify({"answer": clean_response.strip()})
    except Exception as e:
        print("❌ Gemini API failed:", str(e))

    # Fallback: Cohere
    try:
        cohere_response = co.chat(
            model="command-r-plus-08-2024",
            message=prompt,
            temperature=0.7,
            max_tokens=1200
        )
        clean_response = cohere_response.text.replace("*", "")
        return jsonify({"answer": clean_response.strip()})
    except Exception as e:
        print("❌ Cohere API failed:", str(e))

    return jsonify({"answer": "⚠️ Sorry, we couldn't generate a response at the moment."})

@app.route('/MedAssist')
def analysis_page():
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
