from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, g
import os
import json
import groq
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import requests
from PIL import Image
import io
import base64
import uuid
import threading
import time
from typing import Dict, List, Optional
import re
import hashlib
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
DATABASE = os.path.join(os.path.dirname(__file__), 'users.db')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Groq AI
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# User preferences and conversation memory
user_preferences = {}
conversation_memory = {}

# Grok AI personality modes
PERSONALITY_MODES = {
    'default': {
        'name': 'FlaskAI Assistant',
        'tone': 'helpful and informative',
        'style': 'professional',
        'humor_level': 'moderate'
    },
    'grok': {
        'name': 'Grok',
        'tone': 'witty and rebellious',
        'style': 'casual and humorous',
        'humor_level': 'high'
    },
    'professional': {
        'name': 'Professional Assistant',
        'tone': 'formal and precise',
        'style': 'business-like',
        'humor_level': 'low'
    },
    'creative': {
        'name': 'Creative Assistant',
        'tone': 'imaginative and artistic',
        'style': 'expressive',
        'humor_level': 'moderate'
    }
}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        db.commit()

# Initialize DB on first run
init_db()

def init_chat_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
        )''')
        db.commit()

init_chat_db()

def get_user_preferences(user_id: str) -> Dict:
    """Get user preferences from memory or database"""
    if user_id in user_preferences:
        return user_preferences[user_id]
    
    # Default preferences
    default_prefs = {
        'personality_mode': 'default',
        'language': 'en',
        'max_context_length': 10,
        'enable_web_search': True,
        'enable_code_execution': False,
        'enable_voice': False,
        'theme': 'auto'
    }
    
    user_preferences[user_id] = default_prefs
    return default_prefs

def save_conversation_memory(user_id: str, message: str, response: str, metadata: Dict = None):
    """Save conversation to memory"""
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    
    conversation_memory[user_id].append({
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'response': response,
        'metadata': metadata or {}
    })
    
    # Keep only last 20 conversations
    if len(conversation_memory[user_id]) > 20:
        conversation_memory[user_id] = conversation_memory[user_id][-20:]

def get_conversation_context(user_id: str, max_length: int = 10) -> str:
    """Get recent conversation context"""
    if user_id not in conversation_memory:
        return ""
    
    recent_conversations = conversation_memory[user_id][-max_length:]
    context = []
    
    for conv in recent_conversations:
        context.append(f"User: {conv['message']}")
        context.append(f"Assistant: {conv['response']}")
    
    return "\n".join(context)

def web_search(query: str) -> List[Dict]:
    """Perform web search using DuckDuckGo API"""
    try:
        # Using DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        results = []
        
        # Extract abstract
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', ''),
                'snippet': data.get('Abstract', ''),
                'url': data.get('AbstractURL', ''),
                'source': 'DuckDuckGo'
            })
        
        # Extract related topics
        for topic in data.get('RelatedTopics', [])[:3]:
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                    'snippet': topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'source': 'DuckDuckGo'
                })
        
        return results
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []

def analyze_image(image_data: str) -> str:
    """Analyze image using Groq Vision (if available) or fallback to text description"""
    try:
        # For now, we'll use a text-based approach since Groq doesn't have vision yet
        # In the future, this can be updated when Groq adds vision capabilities
        
        # Decode base64 image to get basic info
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Get basic image information
        width, height = image.size
        format_type = image.format
        mode = image.mode
        
        # Create a basic description
        description = f"Image analysis: {format_type} image, {width}x{height} pixels, {mode} color mode."
        
        # Ask Groq to analyze the image based on user's description
        prompt = f"""
        The user has uploaded an image with the following technical details:
        - Format: {format_type}
        - Dimensions: {width}x{height} pixels
        - Color mode: {mode}
        
        Please provide a helpful response about what this image might contain based on common image types,
        and ask the user to describe what they see in the image so you can provide better assistance.
        """
        
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return "Sorry, I couldn't analyze this image properly. Please describe what you see in the image."

def execute_code(code: str, language: str = 'python') -> Dict:
    """Execute code safely (sandboxed)"""
    try:
        # Basic code execution for Python (very limited for security)
        if language.lower() == 'python':
            # Only allow safe operations
            safe_imports = ['math', 'datetime', 'json', 'random', 'string']
            unsafe_keywords = ['import', 'exec', 'eval', 'open', 'file', 'system', 'subprocess']
            
            # Check for unsafe operations
            for keyword in unsafe_keywords:
                if keyword in code.lower():
                    return {
                        'success': False,
                        'output': f"Security: {keyword} operations are not allowed",
                        'error': 'Unsafe operation detected'
                    }
            
            # Create a safe execution environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'bool': bool,
                    'type': type,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'pow': pow,
                    'divmod': divmod,
                    'all': all,
                    'any': any,
                    'sorted': sorted,
                    'reversed': reversed,
                }
            }
            
            # Add safe imports
            for module_name in safe_imports:
                try:
                    safe_globals[module_name] = __import__(module_name)
                except:
                    pass
            
            # Execute code
            exec_result = {}
            exec(code, safe_globals, exec_result)
            
            return {
                'success': True,
                'output': 'Code executed successfully',
                'result': exec_result
            }
        else:
            return {
                'success': False,
                'output': f"Language {language} not supported for execution",
                'error': 'Unsupported language'
            }
    except Exception as e:
        return {
            'success': False,
            'output': str(e),
            'error': 'Execution error'
        }

def verify_firebase_token(id_token):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None

def get_ai_response(query, user_id=None, personality_mode='default', include_web_search=True, include_image=None):
    """Get response from Groq AI with Grok-like features"""
    try:
        # Get user preferences
        prefs = get_user_preferences(user_id) if user_id else {}
        personality = PERSONALITY_MODES.get(personality_mode, PERSONALITY_MODES['default'])
        
        # Build context
        context = get_conversation_context(user_id, prefs.get('max_context_length', 10))
        
        # Perform web search if enabled
        web_results = []
        if include_web_search and prefs.get('enable_web_search', True):
            web_results = web_search(query)
        
        # Analyze image if provided
        image_analysis = ""
        if include_image:
            image_analysis = analyze_image(include_image)
        
        # Build comprehensive prompt
        prompt_parts = [
            f"You are {personality['name']}, an AI assistant with a {personality['tone']} tone and {personality['style']} style.",
            f"Humor level: {personality['humor_level']}",
            "You have access to real-time information and can provide witty, informative responses.",
            "Always be helpful, accurate, and engaging in your responses."
        ]
        
        if context:
            prompt_parts.append(f"Recent conversation context:\n{context}")
        
        if web_results:
            prompt_parts.append("Current web search results:")
            for result in web_results[:3]:
                prompt_parts.append(f"- {result['title']}: {result['snippet']}")
        
        if image_analysis:
            prompt_parts.append(f"Image analysis: {image_analysis}")
        
        prompt_parts.append(f"\nUser query: {query}")
        prompt_parts.append("""
        Please respond in the following JSON format:
        {
            "response": "Your detailed, engaging response",
            "suggestions": [
                "Follow-up question 1",
                "Follow-up question 2", 
                "Follow-up question 3",
                "Follow-up question 4",
                "Follow-up question 5"
            ],
            "web_sources": ["source1", "source2"],
            "code_suggestion": "optional code snippet if relevant",
            "personality_note": "optional personality-specific comment"
        }
        """)
        
        full_prompt = "\n".join(prompt_parts)
        
        # Use Groq AI
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="llama3-8b-8192",  # Using Llama 3 model via Groq
            temperature=0.7,
            max_tokens=1000
        )
        
        response_text = response.choices[0].message.content
        
        # Parse the response
        try:
            response_json = json.loads(response_text)
            return response_json
        except json.JSONDecodeError:
            # Fallback response
            return {
                "response": response_text,
                "suggestions": [
                    "Can you tell me more?",
                    "What are some examples?",
                    "How does this work?",
                    "What are the benefits?",
                    "Are there any alternatives?"
                ],
                "web_sources": [],
                "code_suggestion": "",
                "personality_note": ""
            }
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return {
            "response": "I apologize, but I'm having trouble processing your request right now. Please try again.",
            "suggestions": [
                "Try rephrasing your question",
                "Ask about a different topic",
                "Check your internet connection",
                "What can you help me with?",
                "Tell me a fun fact"
            ],
            "web_sources": [],
            "code_suggestion": "",
            "personality_note": ""
        }

@app.route('/')
def index():
    """Main page - redirect to login if not authenticated"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user={'email': session.get('user_email')})

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/auth/verify', methods=['POST'])
def verify_token():
    """Verify Firebase authentication token"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No token provided'}), 400
        
        decoded_token = verify_firebase_token(id_token)
        if decoded_token:
            # Store user info in session
            session['user_id'] = decoded_token['uid']
            session['user_info'] = {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture')
            }
            return jsonify({'success': True, 'user': session['user_info']})
        else:
            return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Authentication failed'}), 401

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title, created_at FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],))
    sessions = [{'id': row[0], 'title': row[1], 'created_at': row[2]} for row in cursor.fetchall()]
    return jsonify({'sessions': sessions})

@app.route('/api/session', methods=['POST'])
def create_session():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    db = get_db()
    cursor = db.cursor()
    title = request.json.get('title', 'New Chat')
    cursor.execute('INSERT INTO chat_sessions (user_id, title) VALUES (?, ?)', (session['user_id'], title))
    db.commit()
    return jsonify({'session_id': cursor.lastrowid})

@app.route('/api/session/<int:session_id>', methods=['GET'])
def get_session_messages(session_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT sender, content, metadata, timestamp FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
    messages = [
        {'sender': row[0], 'content': row[1], 'metadata': json.loads(row[2]) if row[2] else {}, 'timestamp': row[3]}
        for row in cursor.fetchall()
    ]
    return jsonify({'messages': messages})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        data = request.get_json()
        query = data.get('query', '').strip()
        personality_mode = data.get('personality_mode', 'default')
        include_web_search = data.get('include_web_search', True)
        image_data = data.get('image_data')
        session_id = data.get('session_id')
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        user_id = session['user_id']
        # Intercept short greetings
        greetings = [r'^\s*hey\s*$', r'^\s*hi\s*$', r'^\s*hello\s*$', r'^\s*yo\s*$', r'^\s*sup\s*$', r'^\s*hey!\s*$', r'^\s*hi!\s*$', r'^\s*hello!\s*$']
        if any(re.match(g, query, re.IGNORECASE) for g in greetings):
            return jsonify({
                'response': "Hey! 😊",
                'suggestions': [
                    "Ask me anything about Python!",
                    "Need help with code?",
                    "Want to know something cool?"
                ],
                'web_sources': [],
                'code_suggestion': "",
                'personality_note': ""
            })
        # For all other prompts, return JSON with 'response' key
        ai_response = get_ai_response(query, user_id, personality_mode, include_web_search, image_data)
        save_conversation_memory(user_id, query, ai_response['response'])
        if session_id:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('INSERT INTO chat_messages (session_id, sender, content, metadata) VALUES (?, ?, ?, ?)',
                (session_id, 'user', query, json.dumps({})))
            cursor.execute('INSERT INTO chat_messages (session_id, sender, content, metadata) VALUES (?, ?, ?, ?)',
                (session_id, 'assistant', ai_response['response'], json.dumps({k: v for k, v in ai_response.items() if k not in ['response']})))
            db.commit()
        # Always return JSON
        if isinstance(ai_response, dict) and 'response' in ai_response:
            return jsonify({'response': ai_response['response']})
        return jsonify({'response': str(ai_response)})
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({'error': 'Sorry, something went wrong. Please try again.'}), 500

@app.route('/api/execute-code', methods=['POST'])
def execute_code_endpoint():
    """Execute code safely"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        code = data.get('code', '').strip()
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        # Execute code
        result = execute_code(code, language)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        return jsonify({
            'success': False,
            'output': 'Code execution failed',
            'error': str(e)
        }), 500

@app.route('/api/preferences', methods=['GET', 'POST'])
def user_preferences_endpoint():
    """Manage user preferences"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        
        if request.method == 'GET':
            prefs = get_user_preferences(user_id)
            return jsonify(prefs)
        
        elif request.method == 'POST':
            data = request.get_json()
            user_preferences[user_id] = {**get_user_preferences(user_id), **data}
            return jsonify({'success': True, 'preferences': user_preferences[user_id]})
            
    except Exception as e:
        logger.error(f"Preferences error: {e}")
        return jsonify({'error': 'Failed to manage preferences'}), 500

@app.route('/api/conversation-history', methods=['GET'])
def conversation_history():
    """Get conversation history"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        history = conversation_memory.get(user_id, [])
        
        return jsonify({'history': history})
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'error': 'Failed to get history'}), 500

@app.route('/api/personality-modes', methods=['GET'])
def get_personality_modes():
    """Get available personality modes"""
    return jsonify({'modes': PERSONALITY_MODES})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'ai_provider': 'Groq AI',
        'model': 'llama3-8b-8192',
        'features': {
            'multi_modal': True,
            'web_search': True,
            'code_execution': True,
            'conversation_memory': True,
            'personality_modes': True
        }
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return render_template('register.html', error='Email already registered.')
        hashed_pw = generate_password_hash(password)
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_pw))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['user_email'] = email
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid email or password.')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 