import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


load_dotenv('.env')

app = Flask(__name__)
CORS(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') + '/news_dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

open_ai_api = os.getenv('OPENAI_API_KEY')

from pull.puller import Puller
puller = Puller(api_key=open_ai_api, local=False)

from chat.chatbot import Chatbot
chatbot = Chatbot(api_key=open_ai_api, local=False)

# Import the __init__.py from modules which had imported all files from the folder.
import modules