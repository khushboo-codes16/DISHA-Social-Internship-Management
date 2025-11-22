from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.scholar_no = data.get('scholar_no', '')
        self.name = data.get('name', '')
        self.email = data.get('email', '')
        self.dob = data.get('dob', '')
        self.course = data.get('course', '')
        self.contact = data.get('contact', '')
        self.role = data.get('role', 'student')
        self.toli_id = data.get('toli_id')
        self.profile_photo = data.get('profile_photo', '')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.password_hash = data.get('password_hash', '')
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'scholar_no': self.scholar_no,
            'name': self.name,
            'email': self.email,
            'dob': self.dob,
            'course': self.course,
            'contact': self.contact,
            'role': self.role,
            'toli_id': self.toli_id,
            'profile_photo': self.profile_photo,
            'created_at': self.created_at,
            'password_hash': self.password_hash
        }

    # Flask-Login required properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

class Toli:
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.name = data.get('name', '')
        self.toli_no = data.get('toli_no', '')
        self.location = data.get('location', {})
        self.members = data.get('members', [])
        self.leader_id = data.get('leader_id', '')
        self.status = data.get('status', 'draft')
        self.session_year = data.get('session_year', '')
        self.created_by = data.get('created_by', '')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.approved_at = data.get('approved_at')
        self.coordinator_name = data.get('coordinator_name', '')
        self.coordinator_contact = data.get('coordinator_contact', '')
        
    def to_dict(self):
        # Convert any date objects to datetime in members data
        members_data = []
        for member in self.members:
            member_copy = member.copy()
            if 'dob' in member_copy and isinstance(member_copy['dob'], date):
                member_copy['dob'] = datetime.combine(member_copy['dob'], datetime.min.time())
            members_data.append(member_copy)
        
        return {
            'name': self.name,
            'toli_no': self.toli_no,
            'location': self.location,
            'members': members_data,
            'leader_id': self.leader_id,
            'status': self.status,
            'session_year': self.session_year,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'approved_at': self.approved_at,
            'coordinator_name': self.coordinator_name,
            'coordinator_contact': self.coordinator_contact
        }

# Update the Program class with all required attributes
class Program:
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.program_no = data.get('program_no', 1)
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.program_type = data.get('program_type', '')
        self.location = data.get('location', '')
        
        # Handle date conversion safely - ensure it's always datetime
        start_date = data.get('start_date') or data.get('date')
        if isinstance(start_date, date):
            # Convert date to datetime
            self.start_date = datetime.combine(start_date, datetime.min.time())
        elif isinstance(start_date, str):
            try:
                self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except (ValueError, TypeError):
                self.start_date = datetime.utcnow()
        else:
            self.start_date = start_date or datetime.utcnow()
            
        self.end_date = data.get('end_date', '')
        self.status = data.get('status', 'completed')
        self.student_id = data.get('student_id', '')
        self.toli_id = data.get('toli_id', '')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.total_persons = data.get('total_persons', 0)
        self.achievements = data.get('achievements', '')
        self.organizer_name = data.get('organizer_name', '')
        self.organizer_contact = data.get('organizer_contact', '')
        self.pincode = data.get('pincode', '')
        self.state = data.get('state', '')
        self.district = data.get('district', '')
        self.images = data.get('images', [])  # Add images field
        
    def to_dict(self):
        return {
            'program_no': self.program_no,
            'title': self.title,
            'description': self.description,
            'program_type': self.program_type,
            'location': self.location,
            'start_date': self.start_date,  # This is now always datetime
            'date': self.start_date,  # Store both for compatibility
            'end_date': self.end_date,
            'status': self.status,
            'student_id': self.student_id,
            'toli_id': self.toli_id,
            'created_at': self.created_at,
            'total_persons': self.total_persons,
            'achievements': self.achievements,
            'organizer_name': self.organizer_name,
            'organizer_contact': self.organizer_contact,
            'pincode': self.pincode,
            'state': self.state,
            'district': self.district,
            'images': self.images  # Include images in dict
        }
# Add the missing Resource class
class Resource:
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.resource_type = data.get('resource_type', '')
        self.file_path = data.get('file_path', '')
        self.file_name = data.get('file_name', '')
        self.file_size = data.get('file_size', 0)
        self.external_link = data.get('external_link', '')
        self.created_by = data.get('created_by', '')
        self.created_at = data.get('created_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'resource_type': self.resource_type,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'external_link': self.external_link,
            'created_by': self.created_by,
            'created_at': self.created_at
        }

class Newsletter:
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.program_id = data.get('program_id')
        self.title = data.get('title', '')
        self.content = data.get('content', '')
        self.program_type = data.get('program_type', '')
        self.location = data.get('location', '')
        self.date = data.get('date')
        self.participants_count = data.get('participants_count', 0)
        self.achievements = data.get('achievements', '')
        self.organizer_name = data.get('organizer_name', '')
        self.images = data.get('images', [])
        self.toli_name = data.get('toli_name', '')
        self.status = data.get('status', 'draft')
        self.created_by = data.get('created_by')
        self.created_at = data.get('created_at')
        self.ai_generated = data.get('ai_generated', False)

    def to_dict(self):
        return {
            'program_id': self.program_id,
            'title': self.title,
            'content': self.content,
            'program_type': self.program_type,
            'location': self.location,
            'date': self.date,
            'participants_count': self.participants_count,
            'achievements': self.achievements,
            'organizer_name': self.organizer_name,
            'images': self.images,
            'toli_name': self.toli_name,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'ai_generated': self.ai_generated
        }

class Report:
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.program_id = data.get('program_id')
        self.title = data.get('title', '')
        self.content = data.get('content', '')
        self.program_type = data.get('program_type', '')
        self.location = data.get('location', '')
        self.date = data.get('date')
        self.participants_count = data.get('participants_count', 0)
        self.achievements = data.get('achievements', '')
        self.organizer_name = data.get('organizer_name', '')
        self.toli_name = data.get('toli_name', '')
        self.status = data.get('status', 'completed')
        self.created_by = data.get('created_by')
        self.created_at = data.get('created_at')
        self.ai_generated = data.get('ai_generated', False)
        self.impact_score = data.get('impact_score', 0)
        self.recommendations = data.get('recommendations', [])

    def to_dict(self):
        return {
            'program_id': self.program_id,
            'title': self.title,
            'content': self.content,
            'program_type': self.program_type,
            'location': self.location,
            'date': self.date,
            'participants_count': self.participants_count,
            'achievements': self.achievements,
            'organizer_name': self.organizer_name,
            'toli_name': self.toli_name,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'ai_generated': self.ai_generated,
            'impact_score': self.impact_score,
            'recommendations': self.recommendations
        }

class Message:
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.title = data.get('title', '')
        self.content = data.get('content', '')
        self.sender_id = data.get('sender_id', '')
        self.receiver_id = data.get('receiver_id', '')
        self.is_read = data.get('is_read', False)
        self.created_at = data.get('created_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'is_read': self.is_read,
            'created_at': self.created_at
        }

class News:
    def __init__(self, news_data):
        self.id = str(news_data['_id']) if '_id' in news_data else None
        self.title = news_data.get('title', '')
        self.content = news_data.get('content', '')
        self.image = news_data.get('image', '')
        self.created_by = news_data.get('created_by', '')
        self.created_at = news_data.get('created_at', datetime.utcnow())
        self.is_published = news_data.get('is_published', True)
    
    def to_dict(self):
        data = {
            'title': self.title,
            'content': self.content,
            'image': self.image,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'is_published': self.is_published
        }
        if self.id:
            data['_id'] = self.id
        return data

class Gallery:
    def __init__(self, gallery_data):
        self.id = str(gallery_data['_id']) if '_id' in gallery_data else None
        self.title = gallery_data.get('title', '')
        self.description = gallery_data.get('description', '')
        self.image_path = gallery_data.get('image_path', '')
        self.program_id = gallery_data.get('program_id', '')
        self.created_by = gallery_data.get('created_by', '')
        self.created_at = gallery_data.get('created_at', datetime.utcnow())
    
    def to_dict(self):
        data = {
            'title': self.title,
            'description': self.description,
            'image_path': self.image_path,
            'program_id': self.program_id,
            'created_by': self.created_by,
            'created_at': self.created_at
        }
        if self.id:
            data['_id'] = self.id
        return data
class Instruction:
    def __init__(self, data):
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.title = data.get('title', 'परिवीक्षा दिशानिर्देश')
        self.content = data.get('content', '')
        self.created_by = data.get('created_by', '')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.is_active = data.get('is_active', True)
    
    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }
