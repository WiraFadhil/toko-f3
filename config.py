import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL', '')
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

# AI Customer Service
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY', '')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
# prioritas pemakaian provider, koma-terpisah (coba dulu -> terakhir)
AI_PROVIDER_ORDER = os.getenv('AI_PROVIDER_ORDER', 'groq,cerebras,mistral,gemini')
AI_REQUEST_TIMEOUT = int(os.getenv('AI_REQUEST_TIMEOUT', '20'))
# jumlah maksimal provider yang dicoba dalam satu permintaan (amankan batas waktu serverless)
AI_MAX_PROVIDERS = int(os.getenv('AI_MAX_PROVIDERS', '2'))
