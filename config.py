import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # AI Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = 'llama3-8b-8192'  # Using Llama 3 model via Groq
    GROQ_TEMPERATURE = 0.7
    GROQ_MAX_TOKENS = 1000
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'flask-ai-chatbot')
    FIREBASE_PRIVATE_KEY_ID = os.getenv('FIREBASE_PRIVATE_KEY_ID')
    FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL')
    FIREBASE_CLIENT_ID = os.getenv('FIREBASE_CLIENT_ID')
    
    # Web Search Configuration
    WEB_SEARCH_ENABLED = os.getenv('WEB_SEARCH_ENABLED', 'True').lower() == 'true'
    WEB_SEARCH_TIMEOUT = int(os.getenv('WEB_SEARCH_TIMEOUT', '10'))
    
    # Code Execution Configuration
    CODE_EXECUTION_ENABLED = os.getenv('CODE_EXECUTION_ENABLED', 'False').lower() == 'true'
    CODE_EXECUTION_TIMEOUT = int(os.getenv('CODE_EXECUTION_TIMEOUT', '5'))
    
    # Conversation Configuration
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '20'))
    MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '10'))
    
    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10')) * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # 1 hour
    
    # Personality Modes Configuration
    PERSONALITY_MODES = {
        'default': {
            'name': 'FlaskAI Assistant',
            'tone': 'helpful and informative',
            'style': 'professional',
            'humor_level': 'moderate',
            'description': 'Balanced and helpful AI assistant'
        },
        'grok': {
            'name': 'Grok',
            'tone': 'witty and rebellious',
            'style': 'casual and humorous',
            'humor_level': 'high',
            'description': 'Witty and rebellious AI with attitude'
        },
        'professional': {
            'name': 'Professional Assistant',
            'tone': 'formal and precise',
            'style': 'business-like',
            'humor_level': 'low',
            'description': 'Formal and precise business assistant'
        },
        'creative': {
            'name': 'Creative Assistant',
            'tone': 'imaginative and artistic',
            'style': 'expressive',
            'humor_level': 'moderate',
            'description': 'Imaginative and artistic AI companion'
        }
    }
    
    # Safe Code Execution Configuration
    SAFE_IMPORTS = {
        'math', 'datetime', 'json', 'random', 'string', 'collections',
        'itertools', 'functools', 'operator', 'statistics', 'decimal'
    }
    
    UNSAFE_KEYWORDS = {
        'import', 'exec', 'eval', 'open', 'file', 'system', 'subprocess',
        'os.', 'sys.', '__import__', 'globals', 'locals', 'vars'
    }
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_firebase_credentials(cls):
        """Get Firebase credentials dictionary"""
        return {
            "type": "service_account",
            "project_id": cls.FIREBASE_PROJECT_ID,
            "private_key_id": cls.FIREBASE_PRIVATE_KEY_ID,
            "private_key": cls.FIREBASE_PRIVATE_KEY.replace("\\n", "\n") if cls.FIREBASE_PRIVATE_KEY else None,
            "client_email": cls.FIREBASE_CLIENT_EMAIL,
            "client_id": cls.FIREBASE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{cls.FIREBASE_CLIENT_EMAIL}",
            "universe_domain": "googleapis.com"
        }
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is required")
        
        if not cls.FIREBASE_PRIVATE_KEY:
            errors.append("FIREBASE_PRIVATE_KEY is required")
        
        if not cls.FIREBASE_CLIENT_EMAIL:
            errors.append("FIREBASE_CLIENT_EMAIL is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 