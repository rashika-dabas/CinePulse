import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from logging import Formatter, FileHandler

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""
    DEBUG = False
    USE_TZ = True
    DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
    LOG_FILENAME = os.path.join(LOG_DIR, f"{datetime.now().strftime('%m%d%Y')}.log")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Ensure log directory exists
if not os.path.exists(Config.LOG_DIR):
    os.makedirs(Config.LOG_DIR)

# Configure logging
file_handler = FileHandler(Config.LOG_FILENAME)
file_handler.setFormatter(Formatter('{levelname} {asctime} {module} {message}', style='{'))
file_handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
