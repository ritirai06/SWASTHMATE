# app.py - New Flask Setup for OCR + Diagnosis + Recommendations

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os, uuid, time
from pathlib import Path
from PIL import Image
import io

# === Import OCR and NLP modules ===
from ocr import extract_text_from_file
from nlp import extract_measurements, extract_disease_mentions, fuzzy_match_diseases, extract_specialization
from diagn import summarize_diagnosis
from recom_engine import symptoms_recommendations

# === Initialize Flask ===
app = Flask(__name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# === Helpers ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_recommendations(disease):
    return symptoms_recommendations.get(disease, ["No recommendations found."])

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'report' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    file = request.files['report']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(file_path)

    # OCR
    extracted_text = extract_text_from_file(file_path)
    if not extracted_text:
        return jsonify({'status': 'error', 'message': 'No text extracted'}), 400

    # NLP + DIAGNOSIS
    measurements = extract_measurements(extracted_text)
    diseases = extract_disease_mentions(extracted_text)
    fuzzy_matches = fuzzy_match_diseases(extracted_text, [d['text'] for d in diseases])
    specialization = extract_specialization(extracted_text)
    diagnosis_summary = summarize_diagnosis(diseases)

    relevant_diseases = set([d['text'] for d in diseases if not d['negated']] + fuzzy_matches)
    recommendations = {d: get_recommendations(d) for d in relevant_diseases}

    return jsonify({
        'status': 'success',
        'diagnosis': list(relevant_diseases),
        'recommendations': recommendations,
        'summary': diagnosis_summary,
        'specialist': specialization,
        'measurements': measurements
    })

if __name__ == '__main__':
    app.run(debug=True)
