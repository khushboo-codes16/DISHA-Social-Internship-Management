from flask import jsonify, request
from app.api import api_bp
from app.models import Message
from app import db
from flask_login import current_user

@api_bp.route('/messages', methods=['GET'])
def get_messages():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    messages = Message.query.filter(
        (Message.receiver_id == current_user.id) | (Message.receiver_id.is_(None))
    ).order_by(Message.created_at.desc()).all()
    
    result = []
    for message in messages:
        result.append({
            'id': message.id,
            'title': message.title,
            'content': message.content,
            'sender': message.sender.name,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat()
        })
    
    return jsonify(result)

@api_bp.route('/messages/<int:message_id>/read', methods=['POST'])
def mark_message_read(message_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    message = Message.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})