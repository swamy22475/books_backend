"""
Configuration Settings for the Application
"""
import os
from datetime import timedelta


class Config:
    """Base configuration"""
    # Flask
    DEBUG = os.getenv('DEBUG', False)
    TESTING = os.getenv('TESTING', False)

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///notification_settings.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')

    # Pagination
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Select configuration based on environment
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    config = ProductionConfig
elif config_name == 'testing':
    config = TestingConfig
else:
    config = DevelopmentConfig
