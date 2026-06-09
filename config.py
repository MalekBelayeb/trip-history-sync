import os


class Config:
    DEBUG = os.getenv("FLASK_ENV") == "development"
    PORT = int(os.getenv("PORT", 5000))
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")
