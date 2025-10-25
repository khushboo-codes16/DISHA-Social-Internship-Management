from app import create_app
from app.database import MongoDB
from app.models import User
from datetime import datetime
import os

app = create_app()

def create_admin_user():
    with app.app_context():
        db = MongoDB()
        
        # Check if database connection is successful
        if not db.is_connected():
            print("❌ Cannot create admin user: Database connection failed!")
            print("💡 Please check your MONGODB_URI in .env file")
            return
        
        # Check if admin already exists
        admin_data = db.get_user_by_email('admin@disha.com')
        if not admin_data:
            admin_user = User({
                'name': 'Admin',
                'email': 'admin@disha.com',
                'role': 'admin',
                'created_at': datetime.utcnow()
            })
            admin_user.set_password('admin123')
            result = db.create_user(admin_user.to_dict())
            if result:
                print("✅ Admin user created: admin@disha.com / admin123")
            else:
                print("❌ Failed to create admin user")
        else:
            print("ℹ️ Admin user already exists")
        
        db.close_connection()

if __name__ == '__main__':
    print("🚀 Starting DISHA Application with MongoDB Atlas...")
    print("📍 Database: MongoDB Atlas Cluster")
    
    # Create admin user
    try:
        create_admin_user()
    except Exception as e:
        print(f"⚠️ Admin creation: {e}")
    
    # Run the application
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(
        debug=debug_mode, 
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )