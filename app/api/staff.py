from flask import jsonify
from app.api import api_bp
from app.models import User

@api_bp.route('/staff', methods=['GET'])
def get_staff():
    staff_members = User.query.filter_by(role='staff').all()
    result = []
    for staff in staff_members:
        result.append({
            'id': staff.id,
            'name': staff.name,
            'email': staff.email,
            'contact': staff.contact
        })
    return jsonify(result)