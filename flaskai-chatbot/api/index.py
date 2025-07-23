from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    """
    Handles requests to the root URL.
    """
    return "Hello from Flask on Vercel!"

# You can add more routes here, for example:
# @app.route('/about')
# def about():
#     return "This is an AI-powered chatbot."

# This block is for local development only and is generally ignored by Vercel's build process.
# IMPORTANT: Corrected the typo __main__ disgraceful_ly to __main__
if __name__ == '__main__':
    # In a production environment (like Vercel), debug should be False
    # For local development, debug=True is useful for auto-reloading and debugging.
    app.run(debug=True)