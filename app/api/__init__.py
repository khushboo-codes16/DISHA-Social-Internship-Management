from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import all API routes
from app.api import auth, toliya, news, gallery, resources, staff, messages, contact