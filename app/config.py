
# app/config.py
import os

class Config:
    _db_url = os.environ.get('DATABASE_URL') or 'postgresql://postgres:kingrich@localhost:5432/inventory_db'
    # Render provides postgres:// but SQLAlchemy 2.x requires postgresql://
    SQLALCHEMY_DATABASE_URI = _db_url.replace('postgres://', 'postgresql://', 1) if _db_url else _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_here'

    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')