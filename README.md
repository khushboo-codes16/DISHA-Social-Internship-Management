# Create .gitignore
cat > .gitignore << 'EOL'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
env/
.venv/
ENV/

# Environment variables
.env
.env.local
.env.production

# Flask
instance/

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
tmp/
temp/

# Coverage reports
htmlcov/
.coverage
.coverage.*

# Jupyter Notebook
.ipynb_checkpoints

# PyInstaller
build/
dist/

# MongoDB
/data/db/

# Uploads
/uploads/
EOL

# Create requirements.txt
cat > requirements.txt << 'EOL'
Flask==2.3.0
Werkzeug==2.3.0
pymongo==4.5.0
python-dotenv==1.0.0
Flask-Login==0.6.3
Flask-WTF==1.1.1
WTForms==3.0.1
email-validator==2.0.0
bcrypt==4.0.1
dnspython==2.4.2
gunicorn==21.2.0
EOL

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Create Procfile
echo "web: gunicorn run:app" > Procfile

# Create render.yaml
cat > render.yaml << 'EOL'
services:
  - type: web
    name: disha-app
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: MONGODB_URI
        value: mongodb+srv://Khushboo_code:CreateMongo16@disha-cluster.apnmwbs.mongodb.net/disha_db?retryWrites=true&w=majority
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: FLASK_ENV
        value: production
EOL

# Create .env.example
cat > .env.example << 'EOL'
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/disha_db?retryWrites=true&w=majority

# Application Configuration
SECRET_KEY=your-very-secret-key-here
DEBUG=False
FLASK_ENV=production

# For future AI features
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_TOKEN=your-huggingface-token-here
EOL

# Create README.md
cat > README.md << 'EOL'
# DISHA - DSVV Social Internship Management System

A comprehensive web application for managing social internship programs at Dev Sanskriti Vishwavidyalaya (DSVV).

## 🌟 Features

- **Student Management**: Complete student registration and profile management
- **Toli Management**: Digital management of student groups (Toliyas)
- **Program Tracking**: Social internship program registration and monitoring
- **Resource Sharing**: Centralized resource repository
- **Admin Dashboard**: Comprehensive administration panel
- **Real-time Messaging**: Communication system for students and admins

## 🛠️ Tech Stack

- **Backend**: Flask, Python
- **Database**: MongoDB Atlas
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Authentication**: Flask-Login, bcrypt
- **Deployment**: Render

<!-- Live demo link removed -->

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/khushboo-codes16/DISHA-Social-Internship-Management.git
cd DISHA-Social-Internship-Management