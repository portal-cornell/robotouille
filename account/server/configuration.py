import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import yaml
from dotenv import load_dotenv

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @property
    def url(self) -> str:
        """Generate database URL string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class SecurityConfig:
    """Security-related configuration settings."""
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 90

@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    google_client_id: str
    google_client_secret: str
    google_token_info_url: str = "https://oauth2.googleapis.com/tokeninfo"

@dataclass
class ServerConfig:
    """Server configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

class Config:
    """Main configuration class."""
    def __init__(
        self,
        env_file: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        # Load environment variables
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Load YAML config if provided
        config_data = {}
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
        
        # Initialize configuration sections
        self.database = self._init_database_config(config_data.get('database', {}))
        self.security = self._init_security_config(config_data.get('security', {}))
        self.oauth = self._init_oauth_config(config_data.get('oauth', {}))
        self.server = self._init_server_config(config_data.get('server', {}))
    
    def _init_database_config(self, config: dict) -> DatabaseConfig:
        """Initialize database configuration."""
        return DatabaseConfig(
            host=self._get_config_value('DB_HOST', config.get('host'), 'localhost'),
            port=int(self._get_config_value('DB_PORT', config.get('port'), '5432')),
            database=self._get_config_value('DB_NAME', config.get('database'), 'oauth_db'),
            user=self._get_config_value('DB_USER', config.get('user'), required=True),
            password=self._get_config_value('DB_PASSWORD', config.get('password'), required=True)
        )
    
    def _init_security_config(self, config: dict) -> SecurityConfig:
        """Initialize security configuration."""
        return SecurityConfig(
            jwt_secret=self._get_config_value('JWT_SECRET', config.get('jwt_secret'), required=True),
            jwt_algorithm=self._get_config_value(
                'JWT_ALGORITHM', 
                config.get('jwt_algorithm'), 
                'HS256'
            ),
            access_token_expiry_minutes=int(self._get_config_value(
                'ACCESS_TOKEN_EXPIRY_MINUTES',
                config.get('access_token_expiry_minutes'),
                '60'
            )),
            refresh_token_expiry_days=int(self._get_config_value(
                'REFRESH_TOKEN_EXPIRY_DAYS',
                config.get('refresh_token_expiry_days'),
                '90'
            ))
        )
    
    def _init_oauth_config(self, config: dict) -> OAuthConfig:
        """Initialize OAuth configuration."""
        return OAuthConfig(
            google_client_id=self._get_config_value(
                'GOOGLE_CLIENT_ID', 
                config.get('google_client_id'), 
                required=True
            ),
            google_client_secret=self._get_config_value(
                'GOOGLE_CLIENT_SECRET', 
                config.get('google_client_secret'), 
                required=True
            ),
            google_token_info_url=self._get_config_value(
                'GOOGLE_TOKEN_INFO_URL',
                config.get('google_token_info_url'),
                'https://oauth2.googleapis.com/tokeninfo'
            )
        )
    
    def _init_server_config(self, config: dict) -> ServerConfig:
        """Initialize server configuration."""
        return ServerConfig(
            host=self._get_config_value('SERVER_HOST', config.get('host'), '0.0.0.0'),
            port=int(self._get_config_value('SERVER_PORT', config.get('port'), '8000')),
            debug=self._get_config_value('DEBUG', config.get('debug'), 'false').lower() == 'true',
            log_level=self._get_config_value('LOG_LEVEL', config.get('log_level'), 'INFO').upper()
        )
    
    @staticmethod
    def _get_config_value(env_key: str, config_value: any, default: str = None, required: bool = False) -> str:
        """
        Get configuration value from environment variable or config file.
        
        Args:
            env_key: Name of environment variable
            config_value: Value from config file
            default: Default value if not found
            required: Whether the value is required
            
        Returns:
            Configuration value
            
        Raises:
            ValueError: If value is required but not found
        """
        value = os.getenv(env_key) or config_value or default
        if required and not value:
            raise ValueError(f"Required configuration value '{env_key}' not found")
        return value