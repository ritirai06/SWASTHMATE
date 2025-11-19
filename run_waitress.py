# run_waitress.py - Production server runner using Waitress
from waitress import serve
from app import app   # Import Flask app from app.py

if __name__ == "__main__":
    print("🚀 Starting Swasthmate on Waitress server...")
    serve(app, host="0.0.0.0", port=8080)