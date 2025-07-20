from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
import json
import groq
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import firebase_config
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

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": "flask-ai-chatbot",
            "private_key_id": "4520061c51b964b37ae100efb2519083f3e4d7e7",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQD0Eh43jNdvcCyR\nRWJwtvd75uOXFklJaMaPiO6flYm4zA9YiF9nM0mVmzceTkjIFefXrv2L03L0KNo0\nRCSjW5tCspAyiR38sBk2tSrAVlYhFewnmdFVz/9mLFskxTiTNWjjqPtV86zTWa++\ns822GwX0JtjjGY1uPYTLPYLn2uRy17JfkVQBij+JqoeSb40ObSMqylNzQKdoSQjh\niUJbR6JlNJ+kbTV4Rbg0EGQhuFMYhsPUUrynlwsu94XTBgJ8cGvgP9n2G/GXVX9W\ncdB2ZuYQvcLQt6Zfe+DXbEBgN1mCErSqUu8yzB88v2kDLkKaOxIQpBg1Nty6h+xI\ngSMpCj6PAgMBAAECggEAYNq7wQGUEHXsSa3GFcKVzUZftHo0lPwOJ7GIOC3oXDwm\nLtTXPyXcIpFYux8HxNbkjPO1TAKaEIgRp0IPZAAbScmAbX16N+dN6ibUk0TvouuH\nLmPc7Xe/+zTI6nuVKt28BPPu4Tn0sF5b3oqNrKFmqG+uC9j9Be1FwD1lsEpt86Ac\nliZB9G37+z0JU/a42hocGg3jQw9/EOYKaic0DdZmYpYWC8sWbX85dXVAlL+9TzXD\ngqvAJal8bwKBt03OwpstEx4lM9vg2OAP9JhQEDduRF4xG/Xvrk1gKR/8lrtm8tz+\nOsbNfzryc9OJyVuZukwUc61xLE5NQ3ePrNZ6vZq28QKBgQD6AqEJmIHlFcqtj6+g\nE4KiVW1+ml1p4DpcjRUid0OeyG42+dMjMzsvIYkuZPYISp58dg5bLW5YPqUO4aSN\nf9AeQzpaJK/J8PrlDkYBlMhOrbEqV2FDqCSu6tXv9D98ibICwsJRc/9r/nRSCQK1\nbiuhxJPekh7/uFrMfCbMQ0hUZwKBgQD56w+IbWxmDlGeA7vLEi017r/GdN7FKUXu\nd2vnOKLEmCxpLfFAy09aEBwIkMPi4w9wYb/H3YDTsWw3yfFFGpwxFYD5GY4MiIx2\nMG0LXUxanXdD1APuG5EM8nFOLiGkYxyEllsOFDyiPu7ovknMuQfwvM/ZoENx2rmo\nlGQbvLmrmQKBgQCWDB/kZ3CGMib7NcJdG3iKvyTBGBo6YgYE5/OoRNYDpR1ox1Vt\nyeCab9EqVBPJdCdcYWpKVKDmO2rK3Kfq+KvKjeSml2AdnhCmioN/jXEOr3YmCF1q\nwq6JgI23vuqfbvC0cXk4c5r3kLb1SU0j4KQ1KYrpyN7r8RQlp9mNPFBbvwKBgQDi\n2dtfmvOqL5UmOX1c90LSkcTB/5O2o6A2tW/ckiwtB3RIhMtYZTPCLJ1FqSIl8LUy\n7YeHhChL/+CbQ1MdxunAJCTN98RY3BmjrpFMn4OPPR/lEa3/lEY12lu++2DONqjM\nMS61uOjQ3Q8/dHrIuavbeYexoyeVUVT1EL1N8CEZAQKBgQDvavzDwiuyPt3NfbM5\n15agtiylY3KcDCGbfHpooGKN15EGknwQq0KkJ79ObXhfMlKmKUV2/i7bAPolADdk\nQy2lGSCVkzO/3r7lnqBRmVNj3nzECUSU3x+o5SAkIbecFEnW0riEUFUbxJXgUYSj\noDfkqxfzckk/fC2gyXxmZVS9Qw==\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-fbsvc@flask-ai-chatbot.iam.gserviceaccount.com",
            "client_id": "103539760473939435879",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40flask-ai-chatbot.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        })
        firebase_admin.initialize_app(cred)
        db = firestore.client()
except Exception as e:
    logger.error(f"Firebase initialization error: {e}")
    db = None

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
        return render_template('login.html')
    return render_template('index.html', user=session.get('user_info'))

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

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat API endpoint with Grok-like features"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        query = data.get('query', '').strip()
        personality_mode = data.get('personality_mode', 'default')
        include_web_search = data.get('include_web_search', True)
        image_data = data.get('image_data')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get user ID for session management
        user_id = session['user_id']
        
        # Get AI response with enhanced features
        ai_response = get_ai_response(
            query, 
            user_id, 
            personality_mode, 
            include_web_search,
            image_data
        )
        
        # Save conversation to memory
        save_conversation_memory(user_id, query, ai_response['response'])
        
        # Log the interaction
        logger.info(f"User {user_id} asked: {query} (mode: {personality_mode})")
        
        return jsonify(ai_response)
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            'error': 'Sorry, something went wrong. Please try again.',
            'response': 'I apologize for the inconvenience. Please try your question again.',
            'suggestions': [
                'Try rephrasing your question',
                'Ask about a different topic',
                'What can you help me with?'
            ]
        }), 500

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)