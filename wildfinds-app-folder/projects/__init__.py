from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager
from flask_migrate import Migrate
import secrets
from dotenv import load_dotenv
# PREVENT CONSTANT RETYPING : 
# $env:FLASK_APP = "C:\Users\taylo\OneDrive\Desktop\WildFinds\wildfinds-app-folder\projects"
# init SQLAlchemy 
db = SQLAlchemy()
load_dotenv()
UPLOAD_FOLDER = 'static/uploads'
csrf_token = secrets.token_hex(32)  # 32-byte token (64 characters)


def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
        # Application-wide config settings
    app.config['SECRET_KEY'] = csrf_token
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Set a 16MB file upload limit
    migrate = Migrate(app, db)

    app.secret_key = os.urandom(24)
    # Configuring the Flask app to connect to the MySQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:iamroot33@localhost/wildfinds_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    @app.context_processor # API key available in all templates without passing it explicitly in each route
    def inject_google_maps_api_key():
        return {'google_maps_api_key': google_maps_api_key}

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

