import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

load_dotenv()

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("flask-ai-chatbot"),
    "private_key_id": os.getenv("4520061c51b964b37ae100efb2519083f3e4d7e7"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("firebase-adminsdk-fbsvc@flask-ai-chatbot.iam.gserviceaccount.com"),
    "client_id": os.getenv(""103539760473939435879","),
    ...
})

firebase_admin.initialize_app(cred)
