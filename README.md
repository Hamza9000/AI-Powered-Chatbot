# FlaskAI Chatbot - Grok AI Features

A powerful Flask-based AI chatbot with Grok AI-like features including multi-modal support, real-time web search, personality modes, and advanced AI capabilities.

## 🚀 Features

### Core AI Capabilities
- **Multi-Modal Support**: Upload and analyze images using Gemini Vision
- **Real-time Web Search**: Get current information using DuckDuckGo API
- **Advanced Context Management**: Intelligent conversation memory
- **Code Execution**: Safe sandboxed code execution for Python
- **File Upload & Processing**: Support for image uploads and analysis

### Grok AI-Style Features
- **Personality Modes**: 
  - Default Assistant (helpful and informative)
  - Grok Mode (witty and rebellious)
  - Professional (formal and precise)
  - Creative (imaginative and artistic)
- **Humor & Personality**: Dynamic responses based on selected personality
- **Real-time Information Access**: Web search integration for current events
- **Advanced Analytics**: Conversation tracking and user preferences
- **Multi-language Support**: Framework ready for internationalization

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode**: Toggle between light and dark themes
- **Real-time Suggestions**: Dynamic follow-up question suggestions
- **Conversation History**: Persistent chat memory
- **User Preferences**: Customizable settings and preferences
- **Secure Authentication**: Firebase-based user authentication

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **AI Models**: Groq AI (Llama 3 8B)
- **Authentication**: Firebase Authentication
- **Database**: Firebase Firestore (for conversation storage)
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **APIs**: DuckDuckGo Search API, Groq AI API

## 📋 Prerequisites

- Python 3.8+
- Firebase project with authentication enabled
- Groq AI API access
- Modern web browser

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flask_ai_chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   FLASK_SECRET_KEY=your-secret-key-here
   GROQ_API_KEY=your-groq-api-key
   FIREBASE_PRIVATE_KEY=your-firebase-private-key
   ```

5. **Configure Firebase**
   - Create a Firebase project
   - Enable Google Authentication
   - Download service account key
   - Update Firebase configuration in `app.py`

6. **Run the application**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Authentication → Google Sign-in
4. Go to Project Settings → Service Accounts
5. Generate new private key
6. Update the credentials in `app.py`

### Groq AI Setup
1. Go to [Groq Console](https://console.groq.com/)
2. Create an API key
3. Add it to your `.env` file

## 📖 Usage

### Basic Chat
1. Sign in with Google
2. Type your message in the chat input
3. Receive AI response with suggestions

### Image Analysis
1. Click the camera icon
2. Upload an image
3. Ask questions about the image
4. Get detailed analysis using Gemini Vision

### Personality Modes
1. Click the personality selector in the header
2. Choose from:
   - **Default**: Balanced and helpful
   - **Grok**: Witty and rebellious
   - **Professional**: Formal and precise
   - **Creative**: Imaginative and artistic

### Web Search
1. Enable web search in settings
2. Ask current events or real-time questions
3. Get responses with web sources

### Code Execution
1. Enable code execution in settings
2. Ask for code examples
3. Execute safe Python code in sandbox

## 🔌 API Endpoints

### Authentication
- `POST /auth/verify` - Verify Firebase token

### Chat
- `POST /api/chat` - Send message and get AI response
- `GET /api/conversation-history` - Get chat history

### Code Execution
- `POST /api/execute-code` - Execute code safely

### User Preferences
- `GET /api/preferences` - Get user preferences
- `POST /api/preferences` - Update user preferences

### System
- `GET /api/personality-modes` - Get available personality modes
- `GET /health` - Health check endpoint

## 🎨 Customization

### Adding New Personality Modes
Edit the `PERSONALITY_MODES` dictionary in `app.py`:
```python
PERSONALITY_MODES = {
    'your_mode': {
        'name': 'Your Assistant',
        'tone': 'your tone description',
        'style': 'your style description',
        'humor_level': 'low/moderate/high'
    }
}
```

### Customizing AI Prompts
Modify the `get_ai_response()` function to customize how the AI responds.

### Styling
The frontend uses Tailwind CSS. Modify the classes in the HTML templates to change the appearance.

## 🔒 Security Features

- **Safe Code Execution**: Sandboxed Python execution with restricted imports
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Built-in protection against abuse
- **Secure Authentication**: Firebase-based secure user authentication
- **Environment Variables**: Sensitive data stored in environment variables

## 📊 Performance Features

- **Conversation Memory**: Efficient in-memory storage with automatic cleanup
- **Caching**: Intelligent caching of AI responses
- **Async Processing**: Non-blocking operations for better user experience
- **Optimized Queries**: Efficient database queries and data handling

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Authentication Fails**
   - Check Firebase configuration
   - Verify service account credentials
   - Ensure Google Sign-in is enabled

2. **Groq API Errors**
   - Verify API key is correct
   - Check API quota limits
   - Ensure proper API permissions

3. **Image Upload Issues**
   - Check file size limits
   - Verify supported image formats
   - Ensure proper file permissions

4. **Code Execution Fails**
   - Check if code execution is enabled in settings
   - Verify code doesn't contain restricted operations
   - Check for syntax errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Groq AI for powerful language models
- Firebase for authentication and database services
- Tailwind CSS for beautiful styling
- Flask community for the excellent web framework

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Built with ❤️ using Flask, Firebase, and Groq AI** 