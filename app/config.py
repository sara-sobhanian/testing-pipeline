import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-a-very-secret-key'
    DEBUG = True  # Set to False in production
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
