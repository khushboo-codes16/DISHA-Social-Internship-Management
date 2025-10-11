from flask import jsonify, request
from app.api import api_bp
from app.models import User
from flask_login import login_user
from datetime import datetime

@api_bp.route('/auth/student-login', methods=['POST'])
def student_login():
    data = request.get_json()
    scholar_no = data.get('scholar_no')
    dob = data.get('dob')
    
    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
    except:
        return jsonify({'success': False, 'message': 'Invalid date format'})
    
    user = User.query.filter_by(scholar_no=scholar_no, dob=dob_date).first()
    
    if user:
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'role': user.role
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@api_bp.route('/auth/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email, role='admin').first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'role': user.role
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})