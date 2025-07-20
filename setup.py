#!/usr/bin/env python3
"""
Setup script for FlaskAI Chatbot with Grok AI Features
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    FlaskAI Chatbot Setup                     ║
║                 Grok AI Features Edition                     ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_virtual_environment():
    """Create virtual environment"""
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = 'venv\\Scripts\\pip'
    else:  # Unix/Linux/Mac
        pip_path = 'venv/bin/pip'
    
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_env_file():
    """Create .env file from template"""
    env_file = Path('.env')
    if not env_file.exists():
        print("🔧 Creating .env file...")
        
        env_content = """# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_DEBUG=True

# Groq AI Configuration
GROQ_API_KEY=your-groq-api-key-here

# Firebase Configuration
FIREBASE_PROJECT_ID=flask-ai-chatbot
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nYour private key here\\n-----END PRIVATE KEY-----\\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@flask-ai-chatbot.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Web Search Configuration
WEB_SEARCH_ENABLED=True
WEB_SEARCH_TIMEOUT=10

# Code Execution Configuration
CODE_EXECUTION_ENABLED=False
CODE_EXECUTION_TIMEOUT=5

# Conversation Configuration
MAX_CONVERSATION_HISTORY=20
MAX_CONTEXT_LENGTH=10

# File Upload Configuration
MAX_FILE_SIZE=10

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Logging Configuration
LOG_LEVEL=INFO
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created")
        print("⚠️  Please update the .env file with your actual API keys and configuration")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'uploads', 'static']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def print_next_steps():
    """Print next steps for the user"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                        Next Steps                            ║
╚══════════════════════════════════════════════════════════════╝

1. 🔑 Get your API keys:
   - Groq AI: https://console.groq.com/
   - Firebase: https://console.firebase.google.com/

2. ⚙️  Configure your .env file:
   - Update GROQ_API_KEY with your Groq API key
   - Update Firebase credentials
   - Set FLASK_SECRET_KEY to a secure random string

3. 🔥 Set up Firebase:
   - Create a Firebase project
   - Enable Google Authentication
   - Download service account key
   - Update Firebase config in app.py

4. 🚀 Run the application:
   - Activate virtual environment: source venv/bin/activate (or venv\\Scripts\\activate on Windows)
   - Run: python app.py
   - Open: http://localhost:5000

5. 📚 Read the documentation:
   - Check README.md for detailed instructions
   - Review API endpoints and features

╔══════════════════════════════════════════════════════════════╗
║                    Features Available                        ║
╚══════════════════════════════════════════════════════════════╝

✅ Multi-Modal Support (Images, Text)
✅ Real-time Web Search
✅ Personality Modes (Default, Grok, Professional, Creative)
✅ Safe Code Execution
✅ Conversation Memory
✅ User Preferences
✅ Dark Mode UI
✅ Responsive Design
✅ Firebase Authentication
✅ Advanced AI Responses

For support, check the README.md file or create an issue in the repository.
    """)

def main():
    """Main setup function"""
    print_banner()
    
    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        create_env_file()
        create_directories()
        print_next_steps()
        
        print("\n🎉 Setup completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 