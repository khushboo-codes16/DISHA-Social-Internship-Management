from flask import jsonify, request
from app.api import api_bp
from app.models import Message, User
from app import db

@api_bp.route('/contact', methods=['POST'])
def submit_contact():
    data = request.get_json()
    
    message = Message(
        title=data.get('subject', 'Contact Form Submission'),
        content=data.get('message'),
        sender_id=None,  # Anonymous
        receiver_id=1  # Default admin
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Your message has been sent successfully!'})