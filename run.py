from app import create_app
from app.database import MongoDB
from app.models import User
from datetime import datetime

app = create_app()

def create_admin_user():
    with app.app_context():
        db = MongoDB()
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
                print("Admin user created: admin@disha.com / admin123")
            else:
                print("Failed to create admin user")

create_admin_user()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)