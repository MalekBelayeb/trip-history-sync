import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from current working directory

class Config:
    DEBUG = os.getenv("FLASK_ENV") == "development"
    PORT = int(os.getenv("PORT", 5000))
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")
