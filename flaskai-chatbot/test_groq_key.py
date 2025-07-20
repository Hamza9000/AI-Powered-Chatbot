import os
from dotenv import load_dotenv
import groq

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
print('Loaded GROQ_API_KEY:', api_key)

try:
    client = groq.Groq(api_key=api_key)
    # Try a simple call to check authentication
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello!"}],
        model="llama3-8b-8192",
        temperature=0.1,
        max_tokens=10
    )
    print('Groq API test successful!')
    print('Sample response:', response.choices[0].message.content)
except Exception as e:
    print('Groq API test failed:', e) 