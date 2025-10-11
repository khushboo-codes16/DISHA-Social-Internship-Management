from flask import Flask
from flask_login import LoginManager
import os
from .database import MongoDB
from .models import User

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/disha_db')
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        db = MongoDB()
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(user_data)
        return None
    
    # Register blueprints
    from .routes.main import main
    from .routes.admin import admin
    from .routes.student import student
    from .routes.auth import auth
    
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(auth)
    
    return app