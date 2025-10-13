from waitress import serve
from app1 import app   # yaha app1.py se Flask app import kar rahe hain

if _name_ == "_main_":
    print("🚀 Starting Medco Analyzer on Waitress server...")
    serve(app, host="0.0.0.0", port=8080)