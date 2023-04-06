import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv('.env')

# Create the Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Configure login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') + '/news_dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create the chatbot and puller
open_ai_api = os.getenv('OPENAI_API_KEY')

# Create the puller
from pull.puller import Puller
puller = Puller(api_key=open_ai_api, local=False)

# Create the chatbot
from chat.chatbot import Chatbot
chatbot = Chatbot(api_key=open_ai_api, local=False)
