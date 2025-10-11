from flask import jsonify, request, send_file
from app.api import api_bp
from app.models import Resource
import os
from flask import current_app

@api_bp.route('/resources', methods=['GET'])
def get_resources():
    category = request.args.get('category')
    
    if category:
        resources = Resource.query.filter_by(category=category).all()
    else:
        resources = Resource.query.all()
    
    result = []
    for resource in resources:
        result.append({
            'id': resource.id,
            'title': resource.title,
            'description': resource.description,
            'file_path': resource.file_path,
            'file_type': resource.file_type,
            'category': resource.category,
            'created_at': resource.created_at.isoformat()
        })
    return jsonify(result)

@api_bp.route('/resource/<int:resource_id>/download')
def download_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resources', resource.file_path)
    return send_file(file_path, as_attachment=True)