import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('b1261c377004b4300d6b8ee7093305732671b06d1e97b6a4', 'dev-secret-' + os.urandom(16).hex())
    UPLOAD_FOLDER = Path('static/uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'heic'}
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB
    MEDICAL_TERM_CORRECTIONS = {
        r'\bbreaststem\b': 'breast tissue',
        r'\bniggles\b': 'nipples',
        r'\bBIMOS\b': 'BI-RADS',
        r'\bmicro calcification\b': 'microcalcification'
    }
    
    @classmethod
    def init_app(cls, app):
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        app.config.from_object(cls)