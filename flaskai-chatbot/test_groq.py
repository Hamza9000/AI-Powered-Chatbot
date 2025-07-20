#!/usr/bin/env python3
"""
Test script for Groq AI integration
"""

import os
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_connection():
    """Test Groq AI connection and basic functionality"""
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        return False
    
    try:
        # Initialize Groq client
        client = groq.Groq(api_key=api_key)
        
        # Test basic completion
        print("🧪 Testing Groq AI connection...")
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with 'Groq AI is working correctly!' and nothing else."
                }
            ],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ Groq AI Response: {result}")
        
        # Test personality mode
        print("\n🧪 Testing personality mode...")
        
        personality_prompt = """
        You are Grok, a witty and rebellious AI assistant. 
        Respond to this question in your characteristic style: "What's 2+2?"
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": personality_prompt}],
            model="llama3-8b-8192",
            temperature=0.8,
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"✅ Personality Test Response: {result}")
        
        print("\n🎉 All tests passed! Groq AI integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Groq AI: {e}")
        return False

def test_web_search():
    """Test web search functionality"""
    try:
        import requests
        
        print("\n🧪 Testing web search...")
        
        url = "https://api.duckduckgo.com/"
        params = {
            'q': 'Python programming',
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('Abstract'):
            print("✅ Web search is working correctly")
            return True
        else:
            print("⚠️  Web search returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Error testing web search: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 FlaskAI Chatbot - Groq AI Integration Test")
    print("=" * 50)
    
    # Test Groq AI
    groq_success = test_groq_connection()
    
    # Test web search
    web_success = test_web_search()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Groq AI: {'✅ PASS' if groq_success else '❌ FAIL'}")
    print(f"Web Search: {'✅ PASS' if web_success else '❌ FAIL'}")
    
    if groq_success and web_success:
        print("\n🎉 All tests passed! Your FlaskAI Chatbot is ready to use.")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Sign in and start chatting!")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("Make sure you have:")
        print("- Valid GROQ_API_KEY in your .env file")
        print("- Internet connection for web search")

if __name__ == "__main__":
    main() 