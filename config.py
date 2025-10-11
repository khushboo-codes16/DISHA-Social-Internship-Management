import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/disha_db')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'