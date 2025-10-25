from flask import Flask
from flask_login import LoginManager
import os
from .database import MongoDB
from .models import User
from datetime import datetime

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

    # Add custom Jinja2 filter for date formatting
    @app.template_filter('format_date')
    def format_date(date_string, fmt=None):
        if fmt is None:
            fmt = '%d %b %Y'
        
        if isinstance(date_string, str):
            # Try to parse the string to datetime
            try:
                # Try different date formats
                for date_format in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y']:
                    try:
                        date_obj = datetime.strptime(date_string, date_format)
                        return date_obj.strftime(fmt)
                    except ValueError:
                        continue
                # If all parsing fails, return original string
                return date_string
            except (ValueError, TypeError):
                return date_string
        elif hasattr(date_string, 'strftime'):
            # It's already a datetime object
            return date_string.strftime(fmt)
        else:
            return str(date_string)
    
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