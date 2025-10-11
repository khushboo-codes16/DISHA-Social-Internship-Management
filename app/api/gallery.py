from flask import jsonify, request
from app.api import api_bp
from app.models import Gallery
from sqlalchemy import desc

@api_bp.route('/gallery', methods=['GET'])
def get_gallery():
    gallery_items = Gallery.query.order_by(desc(Gallery.created_at)).all()
    result = []
    for item in gallery_items:
        result.append({
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'image_path': item.image_path,
            'created_at': item.created_at.isoformat(),
            'program_title': item.program.title if item.program else None
        })
    return jsonify(result)