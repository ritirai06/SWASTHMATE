import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# ✅ Azure Credentials (Form Recognizer / Document Intelligence)
subscription_key = "2l74byUhR3RCo5o7n14Iw9japtU4RPm1uPZUVqMRC1ikjrnWWTpJJQQJ99BHACGhslBXJ3w3AAALACOGoXzk"
endpoint = "https://formocr500.cognitiveservices.azure.com/"

# ✅ Initialize Azure Form Recognizer Client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(subscription_key))


class MedicalOCR:
    def __init__(self):
        pass

    def extract_text_from_file(self, file_path):
        """Extract text using Azure Form Recognizer prebuilt-read model"""
        if not os.path.exists(file_path):
            print(f"[❌] File not found: {file_path}")
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
