import os
import re
import tempfile
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from config import Config

class MedicalOCR:
    def __init__(self):
        self.model = ocr_predictor(pretrained=True)
        self.temp_files = []

    def __del__(self):
        for file in self.temp_files:
            if os.path.exists(file):
                os.remove(file)

    def _preprocess_image(self, image_path):
        """Enhances medical document images for better OCR"""
        try:
            img = Image.open(image_path)
            
            # Convert to grayscale if not already
            if img.mode != 'L':
                img = img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Apply adaptive thresholding
            img_np = np.array(img)
            img_processed = cv2.adaptiveThreshold(
                img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2)
            
            # Save to temporary file
            temp_path = os.path.join(tempfile.gettempdir(), f"preproc_{os.path.basename(image_path)}")
            Image.fromarray(img_processed).save(temp_path)
            self.temp_files.append(temp_path)
            return temp_path
            
        except Exception as e:
            print(f"Preprocessing failed: {e}")
            return image_path

    def _postprocess_text(self, text):
        """Corrects common OCR errors in medical reports"""
        for pattern, replacement in Config.MEDICAL_TERM_CORRECTIONS.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def process_document(self, file_path):
        """Main OCR processing pipeline"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            ext = os.path.splitext(file_path)[1].lower()
            
            # Preprocess image files
            if ext in ('.png', '.jpg', '.jpeg', '.heic'):
                processed_path = self._preprocess_image(file_path)
                doc = DocumentFile.from_images([processed_path])
            elif ext == '.pdf':
                doc = DocumentFile.from_pdf(file_path)
            else:
                raise ValueError("Unsupported file format")

            # Perform OCR
            result = self.model(doc)
            text = self._extract_text(result)
            print("Extracted Text:", text)
            return self._postprocess_text(text)

        except Exception as e:
            print(f"OCR Processing Error: {str(e)}")
            raise
        
    def _extract_text(self, result):
        if not result.pages:
            return ""

        full_text = []
        confidence_scores = []

        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join(word.value for word in line.words)
                    full_text.append(line_text)
                    confidence_scores.extend(word.confidence for word in line.words)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        if avg_confidence < 0.7:  # Threshold for low confidence
            print(f"WARNING: Low OCR confidence ({avg_confidence:.2f})")

        return "\n".join(full_text)
    
# Singleton instance
ocr_processor = MedicalOCR()
