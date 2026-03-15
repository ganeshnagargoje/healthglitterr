"""
Configuration Management with Environment Variable Support

This module provides centralized configuration management for the application,
reading values from environment variables with sensible defaults.

SOLID Principles:
- SRP: Only handles configuration loading and validation
- OCP: New configuration sections can be added without modifying existing code
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class OAuthConfig:
    """Google OAuth configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str


@dataclass
class APIConfig:
    """API server configuration"""
    host: str
    port: int
    debug: bool
    
    @property
    def base_url(self) -> str:
        """Generate API base URL"""
        return f"http://{self.host}:{self.port}"




@dataclass
class StorageConfig:
    """File storage configuration"""
    upload_path: str
    max_file_size_mb: int
    allowed_extensions: list[str]


@dataclass
class I18nConfig:
    """Internationalization configuration"""
    default_language: str
    supported_languages: list[str]


@dataclass
class SecurityConfig:
    """Security configuration"""
    session_timeout_minutes: int
    secret_key: str


class Config:
    """
    Main configuration class that loads all settings from environment variables
    
    SOLID Principles:
    - SRP: Centralizes configuration loading
    - DIP: Provides configuration to other components without them knowing the source
    """
    
    def __init__(self):
        self.database = self._load_database_config()
        self.oauth = self._load_oauth_config()
        self.api = self._load_api_config()
        self.storage = self._load_storage_config()
        self.i18n = self._load_i18n_config()
        self.security = self._load_security_config()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment variables"""
        return DatabaseConfig(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', 'medical_health_review'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres')
        )
    
    def _load_oauth_config(self) -> OAuthConfig:
        """Load OAuth configuration from environment variables"""
        return OAuthConfig(
            client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
            redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/callback')
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration from environment variables"""
        return APIConfig(
            host=os.getenv('API_HOST', 'localhost'),
            port=int(os.getenv('API_PORT', '8001')),
            debug=os.getenv('API_DEBUG', 'false').lower() == 'true'
        )
    
    
    def _load_storage_config(self) -> StorageConfig:
        """Load file storage configuration"""
        return StorageConfig(
            upload_path=os.getenv('UPLOAD_PATH', './uploads'),
            max_file_size_mb=int(os.getenv('MAX_FILE_SIZE_MB', '10')),
            allowed_extensions=['.pdf', '.png', '.jpg', '.jpeg']
        )
    
    def _load_i18n_config(self) -> I18nConfig:
        """Load internationalization configuration"""
        return I18nConfig(
            default_language=os.getenv('DEFAULT_LANGUAGE', 'en'),
            supported_languages=['en', 'hi', 'mr', 'ta']
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        return SecurityConfig(
            session_timeout_minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', '30')),
            secret_key=os.getenv('SECRET_KEY', 'change-this-in-production')
        )


# Global configuration instance
config = Config()
