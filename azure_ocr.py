# azure_ocr.py - Azure Form Recognizer OCR service
import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

# ✅ Azure Credentials (Form Recognizer / Document Intelligence) - Load from environment
subscription_key = os.getenv("AZURE_OCR_KEY")
endpoint = os.getenv("AZURE_OCR_ENDPOINT")

# ✅ Initialize Azure Form Recognizer Client (only if credentials are available)
client = None
if subscription_key and endpoint:
    client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))


class MedicalOCR:
    def __init__(self):
        # This class is a placeholder for future OCR functionality
        # Currently, OCR is handled by extract_text_azure() function
        pass

    def extract_text_from_file(self, file_path):
        """Extract text using Azure Form Recognizer prebuilt-read model"""
        if not os.path.exists(file_path):
            print(f"[❌] File not found: {file_path}")
            return ""

        if not client:
            print("[❌] Azure OCR client not initialized. Please set AZURE_OCR_KEY and AZURE_OCR_ENDPOINT environment variables.")
            return ""
        
        try:
            with open(file_path, "rb") as f:
                poller = client.begin_analyze_document("prebuilt-read", document=f)
            result = poller.result()

            text = ""
            for page in result.pages:
                for line in page.lines:
                    text += line.content + "\n"

            if text.strip():
                print("[📄] OCR Extraction Successful.")
                return text.strip()
            else:
                print("[⚠️] No text extracted.")
                return ""

        except Exception as e:
            print(f"[❌] OCR Processing Error: {e}")
            return ""

    def process_document(self, file_path):
        print(f"[🔍] Running Azure OCR on: {file_path}")
        return self.extract_text_from_file(file_path)
