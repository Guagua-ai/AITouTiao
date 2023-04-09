import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
from flask_migrate import Migrate
from workflow import FlowMachine
from translator.core import TranslatorCore
from chat.chatbot import Chatbot
from pull.puller import Puller
from db import db

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
db.init_app(app)
migrate = Migrate(app, db)

# Set the secret key to sign the JWT tokens
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # 1 day
jwt = JWTManager(app)

# Configure Redis
app.config['REDIS_URL'] = os.getenv('REDIS_URL') + '/0'
redis_store = FlaskRedis(app)

# Create the chatbot and puller
open_ai_api = os.getenv('OPENAI_API_KEY')

# Use local mode
enable_local_mode = os.getenv("LOCAL_MODE", "False") == "True"

# Create the queue
q = FlowMachine(connection=os.getenv('REDIS_URL'))

# Configure SendGrid
app.config['SENDGRID_API_KEY'] = os.getenv('SENDGRID_API_KEY')

# Create the translator
translator = TranslatorCore(api_key=open_ai_api)

# Create the puller
puller = Puller(api_key=open_ai_api,
                translator=translator,
                local=enable_local_mode)

# Create the chatbot
chatbot = Chatbot(api_key=open_ai_api, local=enable_local_mode)
