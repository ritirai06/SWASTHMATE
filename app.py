# app.py - Swasthmate Medical Report Analysis System
from dotenv import load_dotenv
import os
import json
import time
import uuid
import re
import requests
from pathlib import Path
from typing import Dict, Optional
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from text_analyzer import analyze_medical_text, clean_ocr_text, build_summary
from medical_nlp import MedicalNLP
from recommendations import symptoms_recommendations
from flask_cors import CORS
import google.generativeai as genai
import cohere
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
try:
    from analysis_engine import EnhancedAnalysisEngine  # <== enhanced analysis
except ImportError:
    # Fallback if analysis_engine doesn't exist
    class EnhancedAnalysisEngine:
        def generate_comprehensive_summary(self, *args, **kwargs):
            return {"summary": "Analysis engine not available"}
        def generate_priority_recommendations(self, *args, **kwargs):
            return []
        def check_drug_interactions(self, *args, **kwargs):
            return []
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
    analysis_engine = EnhancedAnalysisEngine()  # Enhanced analysis engine

    @classmethod
    def init_app(cls, app):
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH

Config.init_app(app)

# === Gemini Configuration ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")  # Or gemini-1.5-pro if you need higher quality


# === Cohere Configuration ===
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = None
if COHERE_API_KEY:
    co = cohere.Client(COHERE_API_KEY)

# === Azure OCR client (Form Recognizer) ===
azure_client = None
if Config.AZURE_ENDPOINT and Config.AZURE_KEY:
    try:
        azure_client = DocumentAnalysisClient(
            endpoint=Config.AZURE_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_KEY)
        )
        print("[✅] Azure OCR client initialized successfully")
    except Exception as e:
        print(f"[⚠️] Failed to initialize Azure OCR client: {str(e)}")
        azure_client = None

# === OCR.Space fallback configuration ===
OCRSPACE_API_KEY = os.getenv("OCRSPACE_API_KEY")
ocrspace_available = bool(OCRSPACE_API_KEY and OCRSPACE_API_KEY != "YOUR_OCRSPACE_API_KEY")

# === Check if PyPDF2 is available for PDF extraction ===
def check_pypdf2_available():
    """Check if PyPDF2 is installed and available"""
    try:
        import PyPDF2
        return True
    except ImportError:
        return False

pypdf2_available = check_pypdf2_available()

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
    """Extract text using Azure Form Recognizer"""
    if not azure_client:
        raise ValueError("Azure OCR client not initialized. Please set AZURE_ENDPOINT and AZURE_KEY environment variables.")
    
    print(f"[🔍] Extracting text from: {file_path}")
    with open(file_path, "rb") as f:
        poller = azure_client.begin_analyze_document("prebuilt-read", document=f)
    result = poller.result()

    text = ""
    for page in result.pages:
        for line in page.lines:
            text += line.content + "\n"
    
    extracted = text.strip()
    print(f"[✅] Extracted {len(extracted)} characters from document")
    return extracted

def extract_text_ocrspace(file_path):
    """Extract text using OCR.Space API (fallback for images)"""
    try:
        from ocrengine import extract_text as ocrspace_extract
        print(f"[🔍] Using OCR.Space fallback for: {file_path}")
        text = ocrspace_extract(file_path, api_key=OCRSPACE_API_KEY)
        if text:
            print(f"[✅] OCR.Space extracted {len(text)} characters")
        return text
    except Exception as e:
        print(f"[❌] OCR.Space extraction failed: {str(e)}")
        return ""

def extract_text_with_fallback(file_path):
    """Unified OCR extraction with fallback mechanism"""
    # Try Azure OCR first (best for PDFs and documents)
    if azure_client:
        try:
            return extract_text_azure(file_path)
        except Exception as e:
            print(f"[⚠️] Azure OCR failed: {str(e)}")
            print("[🔄] Attempting fallback OCR method...")
    
    # Fallback to OCR.Space for images
    if ocrspace_available:
        file_ext = Path(file_path).suffix.lower()
        # OCR.Space works better with images than PDFs
        if file_ext in ['.png', '.jpg', '.jpeg', '.tiff']:
            text = extract_text_ocrspace(file_path)
            if text and text.strip():
                return text
    
    # If all else fails, try PyPDF2 for PDFs
    if Path(file_path).suffix.lower() == '.pdf':
        try:
            import PyPDF2
            print(f"[🔍] Attempting PDF text extraction with PyPDF2: {file_path}")
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                total_pages = len(pdf_reader.pages)
                print(f"[📄] PDF has {total_pages} page(s)")
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += page_text + "\n"
                            print(f"[✅] Page {page_num}: Extracted {len(page_text)} characters")
                        else:
                            print(f"[⚠️] Page {page_num}: No text found (might be image-based)")
                    except Exception as page_error:
                        print(f"[⚠️] Page {page_num}: Extraction error - {str(page_error)}")
                        continue
            extracted = text.strip()
            if extracted:
                print(f"[✅] PyPDF2 extracted {len(extracted)} characters from {total_pages} page(s)")
                return extracted
            else:
                print("[⚠️] PyPDF2 extracted empty text - PDF appears to be image-based (scanned document)")
                print("[💡] For scanned PDFs, Azure OCR is required. PyPDF2 only works with text-based PDFs.")
                # Don't raise error here - let it fall through to show all options
        except ImportError:
            print("[⚠️] PyPDF2 not available. Install with: pip install PyPDF2")
        except Exception as e:
            print(f"[❌] PyPDF2 extraction failed: {str(e)}")
            import traceback
            print(f"[❌] PyPDF2 traceback: {traceback.format_exc()}")
    
    # No OCR method available or all methods failed
    file_ext = Path(file_path).suffix.lower()
    if file_ext == '.pdf':
        raise ValueError(
            "PDF text extraction failed. Possible reasons:\n"
            "1. PDF is image-based (scanned) - requires Azure OCR\n"
            "2. PDF is encrypted or corrupted\n"
            "3. No OCR service configured\n\n"
            "Solutions:\n"
            "- For scanned PDFs: Configure Azure OCR (AZURE_ENDPOINT and AZURE_KEY)\n"
            "- For text-based PDFs: PyPDF2 is installed but couldn't extract text\n"
            "- Check if PDF is password-protected or corrupted"
        )
    else:
        raise ValueError(
            "No OCR service available for image files. Please configure one of:\n"
            "- Azure OCR: Set AZURE_ENDPOINT and AZURE_KEY environment variables\n"
            "- OCR.Space: Set OCRSPACE_API_KEY environment variable"
        )

# === Routes ===
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('prescription-reader.html')

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
        print(f"\n[📤] Upload started: {filename}")
        print(f"[🆔] Report ID: {report_id}")
        
        # Try OCR extraction - the function will attempt all available methods
        print("[🔍] Starting OCR extraction...")
        print(f"[📁] File path: {saved_path}")
        print(f"[📄] File exists: {os.path.exists(saved_path)}")
        print(f"[📏] File size: {os.path.getsize(saved_path) if os.path.exists(saved_path) else 0} bytes")
        
        try:
            extracted_text = extract_text_with_fallback(saved_path)
        except ValueError as e:
            # Handle case where no OCR service is available or extraction failed
            file_ext = Path(saved_path).suffix.lower()
            error_message = str(e)
            print(f"[❌] OCR extraction failed: {error_message}")
            print(f"[📋] File extension: {file_ext}")
            print(f"[🔧] Azure OCR available: {azure_client is not None}")
            print(f"[🔧] OCR.Space available: {ocrspace_available}")
            print(f"[🔧] PyPDF2 available: {pypdf2_available}")
            
            return jsonify({
                "status": "error", 
                "message": error_message,
                "report_id": report_id,
                "filename": filename,
                "debug_info": {
                    "file_extension": file_ext,
                    "azure_ocr_configured": azure_client is not None,
                    "ocrspace_configured": ocrspace_available,
                    "pypdf2_installed": pypdf2_available
                }
            }), 500
        print(f"[✅] OCR Extraction Complete - Text length: {len(extracted_text)} characters")
        print(f"[📄] OCR Text preview (first 200 chars): {extracted_text[:200]}...")
        
        if not extracted_text or not extracted_text.strip():
            print("[❌] No text extracted from document")
            return jsonify({"status": "error", "message": "No text extracted from the document"}), 400

        # Check if NLP engine is available
        if not Config.nlp_engine:
            print("[❌] NLP engine not initialized")
            return jsonify({
                "status": "error",
                "message": "NLP engine not initialized"
            }), 500
        
        print("[🧠] Starting NLP processing...")
        analysis = Config.nlp_engine.process_text(extracted_text)
        print(f"[✅] NLP Processing Complete")
        print(f"[📊] Analysis results:")
        print(f"   - Diseases found: {len(analysis.get('diseases', []))}")
        print(f"   - Medications found: {len(analysis.get('medications', []))}")
        print(f"   - Diseases: {analysis.get('diseases', [])}")
        print(f"   - Medications: {analysis.get('medications', [])}")
        
        diseases = analysis.get("diseases", [])

        disease_names = [d.lower() for d in diseases]
        normalized_recommendations = {k.lower(): v for k, v in symptoms_recommendations.items()}
        recommendations = list({rec for d in disease_names for rec in normalized_recommendations.get(d, [])})
        print(f"[💡] Recommendations generated: {len(recommendations)}")

        print("[🔬] Starting enhanced analysis...")
        # Analyze measurements with normal ranges
        measurements_analysis = Config.analysis_engine.analyze_measurements(analysis.get("measurements", {}))
        print(f"[📊] Measurements Analysis Complete")
        print(f"   - Total tests: {measurements_analysis.get('total_tests', 0)}")
        print(f"   - Abnormal tests: {measurements_analysis.get('abnormal_count', 0)}")
        
        # Suggest diseases from abnormal measurements
        suggested_diseases_from_measurements = Config.analysis_engine.suggest_diseases_from_measurements(
            measurements_analysis.get("abnormal_tests", [])
        )
        print(f"[🦠] Suggested diseases from measurements: {suggested_diseases_from_measurements}")
        
        # Merge suggested diseases with detected diseases
        existing_diseases = analysis.get("diseases", [])
        all_diseases = list(set(existing_diseases + suggested_diseases_from_measurements))
        analysis["diseases"] = all_diseases
        
        # Add measurements_analysis to analysis object for priority recommendations
        analysis["measurements_analysis"] = measurements_analysis
        
        # Enhanced analysis
        enhanced_analysis = Config.analysis_engine.generate_comprehensive_summary(analysis)
        priority_recommendations = Config.analysis_engine.generate_priority_recommendations(analysis)
        drug_interactions = Config.analysis_engine.check_drug_interactions(analysis.get("medications", []))
        print(f"[✅] Enhanced Analysis Complete")
        print(f"   - Priority recommendations: {len(priority_recommendations)}")
        print(f"   - Drug interactions: {len(drug_interactions)}")

        result_data = {
            "status": "success",
            "report_id": report_id,
            "filename": filename,
            "extracted_text": extracted_text,
            "analysis": analysis,
            "recommendations": recommendations,
            "enhanced_analysis": enhanced_analysis,
            "priority_recommendations": priority_recommendations,
            "drug_interactions": drug_interactions,
            "measurements_analysis": measurements_analysis
        }

        result_json_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{report_id}.results.json")
        with open(result_json_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2)
        
        print(f"[💾] Results saved to: {result_json_path}")
        print(f"[✅] Upload processing complete - Returning response\n")
        
        return jsonify(result_data)

    except ValueError as e:
        # Handle specific value errors (like missing Azure client)
        print(f"[❌] Value error in upload: {str(e)}")
        app.logger.error(f"Value error in upload: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        # Log the full error for debugging
        print(f"[❌] Error processing upload: {str(e)}")
        import traceback
        print(f"[❌] Traceback: {traceback.format_exc()}")
        app.logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": f"Failed to process file: {str(e)}"
        }), 500

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
        
        extracted_text = extract_text_with_fallback(file_path)
        
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
        
        # Enhanced analysis
        enhanced_analysis = Config.analysis_engine.generate_comprehensive_summary(analysis)
        priority_recommendations = Config.analysis_engine.generate_priority_recommendations(analysis)
        drug_interactions = Config.analysis_engine.check_drug_interactions(analysis.get("medications", []))
        
        response = {
            "status": "success",
            "report_id": str(uuid.uuid4()),
            "filename": filename,
            "analysis": analysis,
            "enhanced_analysis": enhanced_analysis,
            "priority_recommendations": priority_recommendations,
            "drug_interactions": drug_interactions,
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
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"debug_{file.filename}")
    file.save(temp_path)
    
    try:
        raw_text = extract_text_with_fallback(temp_path)
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

    text = extract_text_with_fallback(file_path)
    result = analyze_medical_text(text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)

    return render_template('report-analysis.html', result=result)

@app.route('/Analysis')
@app.route('/analysis')
def analysis_page():
    """Route to display analysis page"""
    return render_template('report-analysis.html')

@app.route('/api/get-report/<report_id>', methods=['GET'])
def get_report(report_id):
    """API endpoint to retrieve saved report data by report_id"""
    try:
        result_json_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{report_id}.results.json")
        
        if not os.path.exists(result_json_path):
            return jsonify({
                "status": "error",
                "message": f"Report with ID {report_id} not found"
            }), 404
        
        with open(result_json_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        
        return jsonify({
            "status": "success",
            **report_data
        })
    except Exception as e:
        print(f"[❌] Error loading report {report_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to load report: {str(e)}"
        }), 500

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Alternative upload endpoint"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    if not image.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    os.makedirs('temp', exist_ok=True)
    image_path = os.path.join('temp', image.filename)
    image.save(image_path)

    try:
        # Extract text using OCR with fallback
        try:
            text = extract_text_with_fallback(image_path)
        except ValueError as e:
            # Handle case where no OCR service is available
            file_ext = Path(image_path).suffix.lower()
            print(f"[❌] OCR extraction failed: {str(e)}")
            error_msg = 'OCR service not available. Please configure one of:\n'
            if file_ext == '.pdf':
                error_msg += '- Azure OCR: Set AZURE_ENDPOINT and AZURE_KEY environment variables\n'
                error_msg += '- Or install PyPDF2: pip install PyPDF2'
            else:
                error_msg += '- Azure OCR: Set AZURE_ENDPOINT and AZURE_KEY environment variables\n'
                error_msg += '- OCR.Space: Set OCRSPACE_API_KEY environment variable'
            return jsonify({'error': error_msg}), 500
        if not text or not text.strip():
            return jsonify({'error': 'No text extracted from the image'}), 400

        # Clean the OCR text
        clean_text = clean_ocr_text(text)
        if not clean_text or not clean_text.strip():
            return jsonify({'error': 'Failed to clean extracted text'}), 400
        
        # Check if AWS credentials are available
        if not Config.AWS_ACCESS_KEY or not Config.AWS_SECRET_KEY:
            return jsonify({
                'error': 'NLP service not available. Please configure AWS_ACCESS_KEY and AWS_SECRET_KEY environment variables.'
            }), 500
        
        # Analyze medical text (returns a list of entities)
        nlp_results = analyze_medical_text(clean_text, Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY)
        if not nlp_results:
            return jsonify({'error': 'Failed to analyze medical text'}), 500
        
        # Build summary (expects list of entities)
        summary = build_summary(clean_text, nlp_results)
        
        # Enhanced analysis - convert list to dict format if needed
        # Note: analysis_engine expects dict format, but analyze_medical_text returns list
        # Create a compatible format
        nlp_dict = {
            'entities': nlp_results,
            'diseases': [e['Text'] for e in nlp_results if e.get('Type') == 'MEDICAL_CONDITION'],
            'medications': [e['Text'] for e in nlp_results if e.get('Type') == 'MEDICATION']
        }
        
        enhanced_analysis = Config.analysis_engine.generate_comprehensive_summary(nlp_dict)
        priority_recommendations = Config.analysis_engine.generate_priority_recommendations(nlp_dict)
        drug_interactions = Config.analysis_engine.check_drug_interactions(nlp_dict.get("medications", []))

        return jsonify({
            'text': clean_text,
            'nlp_results': nlp_results,
            'summary': summary,
            'enhanced_analysis': enhanced_analysis,
            'priority_recommendations': priority_recommendations,
            'drug_interactions': drug_interactions
        })

    except ValueError as e:
        # Handle specific value errors (like missing Azure client)
        app.logger.error(f"Value error in upload_image: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f"Error processing image upload: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Failed to process image: {str(e)}'
        }), 500

    finally:
        # Clean up temporary file
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                app.logger.warning(f"Failed to remove temp file: {str(e)}")

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

    # Support both "hindi" and "hi-IN" format
    if language == "hindi" or language == "hi-in" or language.startswith("hi"):
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
    if gemini_model:
        try:
            gemini_response = gemini_model.generate_content(prompt)
            clean_response = gemini_response.text.replace("*", "")
            return jsonify({"answer": clean_response.strip()})
        except Exception as e:
            app.logger.error(f"Gemini API failed: {str(e)}")
    else:
        app.logger.warning("Gemini API not configured. Please set GEMINI_API_KEY environment variable.")

    # Fallback: Cohere
    if not co:
        return jsonify({
            "answer": "⚠️ AI services are not configured. Please set GEMINI_API_KEY or COHERE_API_KEY environment variables."
        }), 500
    
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
def medical_assistant_page():
    return render_template('medical-assistant.html')

@app.route('/signin')
@app.route('/login')
def signin():
    return render_template('login.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/contact', methods=['POST'])
def contact_api():
    """Handle contact form submissions and send email"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        query = data.get('query', '').strip()
        
        if not name or not email or not query:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Email validation
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Send email using Web3Forms API
        
        web3forms_data = {
            'access_key': '6457272e-2663-488d-9f32-7341f9518b21',
            'name': name,
            'email': email,
            'message': query,
            'subject': f'Contact Form Submission from {name}',
            'from_name': 'Swasthmate Contact Form',
            # Configure to send to anshyadav1330@gmail.com
            'to': 'anshyadav1330@gmail.com'
        }
        
        try:
            response = requests.post('https://api.web3forms.com/submit', data=web3forms_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    app.logger.info(f"Contact form submitted successfully from {email}")
                    return jsonify({
                        'success': True,
                        'message': 'Your message has been sent successfully!'
                    }), 200
                else:
                    app.logger.error(f"Web3Forms API error: {result.get('message', 'Unknown error')}")
                    return jsonify({
                        'error': 'Failed to send email. Please try again later.'
                    }), 500
            else:
                app.logger.error(f"Web3Forms API returned status {response.status_code}")
                return jsonify({
                    'error': 'Failed to send email. Please try again later.'
                }), 500
                
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error connecting to Web3Forms API: {str(e)}")
            return jsonify({
                'error': 'Failed to send email. Please try again later.'
            }), 500
        
    except Exception as e:
        app.logger.error(f"Error processing contact form: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred. Please try again later.'
        }), 500

# === Run the App ===
if __name__ == "__main__":
    app.run(debug=True)
