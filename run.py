from app import create_app
from app.database import MongoDB
from app.models import User
from datetime import datetime
import os

app = create_app()

def setup_directories():
    """Create necessary upload directories"""
    upload_dirs = [
        'static/uploads/profile_photos',
        'static/uploads/programs',
        'static/uploads/passport_photos',
        'static/resources'
    ]
    
    for dir_path in upload_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def create_admin_user():
    """Create admin user if doesn't exist"""
    try:
        db = MongoDB()
        
        # Check if database connection is successful
        if not db.is_connected():
            print("❌ Cannot create admin user: Database connection failed!")
            print("💡 The app will run in limited mode")
            return
        
        # Admin configuration (can be overridden via environment)
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@disha.com')
        admin_password = os.getenv('ADMIN_PASSWORD')

        # Check if admin already exists
        admin_data = db.get_user_by_email(admin_email)
        if not admin_data:
            admin_user = User({
                'name': 'Admin',
                'email': admin_email,
                'role': 'admin',
                'created_at': datetime.utcnow()
            })
            # Set password only if provided via environment variable
            if admin_password:
                admin_user.set_password(admin_password)
            result = db.create_user(admin_user.to_dict())
            if result:
                if admin_password:
                    print("✅ Admin user created")
                else:
                    print("✅ Admin user created (no password set)")
            else:
                print("❌ Failed to create admin user")
        else:
            print("ℹ️ Admin user already exists")
        
        db.close_connection()
    except Exception as e:
        print(f"⚠️ Admin creation skipped: {e}")

if __name__ == '__main__':
    print("🚀 Starting DISHA Application...")
    print("📍 Checking system requirements...")
    
    # Setup directories
    setup_directories()
    
    # Create admin user
    create_admin_user()
    
    # Run the application
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🔧 Debug mode: {debug_mode}")
    print("🌐 Starting web server on http://0.0.0.0:5000")
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )