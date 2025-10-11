from flask import jsonify, request
from app.api import api_bp
from app.models import Toliya, User
from app import db

@api_bp.route('/toliyas', methods=['GET'])
def get_toliyas():
    tolkiyas = Toliya.query.all()
    result = []
    for toliya in tolkiyas:
        result.append({
            'id': toliya.id,
            'name': toliya.name,
            'location': toliya.location,
            'state': toliya.state,
            'member_count': len(toliya.members)
        })
    return jsonify(result)

@api_bp.route('/toliya/<int:toliya_id>', methods=['GET'])
def get_toliya(toliya_id):
    toliya = Toliya.query.get_or_404(toliya_id)
    members = []
    for member in toliya.members:
        members.append({
            'id': member.id,
            'name': member.name,
            'scholar_no': member.scholar_no,
            'course': member.course
        })
    
    return jsonify({
        'id': toliya.id,
        'name': toliya.name,
        'location': toliya.location,
        'state': toliya.state,
        'description': toliya.description,
        'members': members
    })