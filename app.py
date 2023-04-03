import modules
from functools import wraps
import os
from auth.auth import User
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from chat.chatbot import Chatbot
from pull.puller import Puller


load_dotenv('.env')

app = Flask(__name__)
CORS(app)

open_ai_api = os.getenv('OPENAI_API_KEY')
puller = Puller(api_key=open_ai_api, local=True)
chatbot = Chatbot(api_key=open_ai_api, local=True)

login_manager = LoginManager()
login_manager.init_app(app)


# Import the __init__.py from modules which had imported all files from the folder.
