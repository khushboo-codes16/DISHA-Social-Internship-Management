from flask import Flask
from flask_login import LoginManager
from app.database import MongoDB
from .models import User
import os
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/disha_db')
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Initialize database
    db = MongoDB()
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            if db.is_connected():
                user_data = db.get_user_by_id(user_id)
                if user_data:
                    from app.models import User
                    return User(user_data)
        except Exception as e:
            print(f"Error loading user: {e}")
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
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.student import student
    from app.routes.admin import admin
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(admin, url_prefix='/admin')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return "Page not found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return "Internal server error", 500
    
    # Custom context processor to make current year available in all templates
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.now().year}
    
    # Custom context processor to check database connection
    @app.context_processor
    def inject_db_status():
        return {'db_connected': db.is_connected()}
    
    return app