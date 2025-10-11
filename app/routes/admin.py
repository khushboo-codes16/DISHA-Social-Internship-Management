from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from app.models import User, Toli, Program, Resource, Message
from app.forms import AdminManageToliForm, FinalizeToliForm, AddStudentForm, UploadResourceForm, SendMessageForm, AddMembersToToliForm
from app.database import MongoDB
from datetime import datetime

admin = Blueprint('admin', __name__)
db = MongoDB()

def save_photo(photo):
    if photo:
        filename = secure_filename(photo.filename)
        # Create directory if it doesn't exist
        photo_dir = os.path.join(current_app.root_path, 'static/uploads/passport_photos')
        os.makedirs(photo_dir, exist_ok=True)
        photo_path = os.path.join(photo_dir, filename)
        photo.save(photo_path)
        return f'uploads/passport_photos/{filename}'
    return None

@admin.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Statistics - Use only existing methods
    stats = {
        'total_students': db.count_users_by_role('student'),
        'total_tolis': db.count_tolis(),
        'total_programs': db.count_programs(),
        'active_tolis': db.count_active_tolis(),
        'total_resources': db.count_resources()
        # Removed pending_programs for now
    }
    
    # Try to get pending programs count if method exists
    try:
        stats['pending_programs'] = db.count_pending_programs()
    except AttributeError:
        # If method doesn't exist, calculate manually
        all_programs = db.get_all_programs()
        pending_count = len([p for p in all_programs if p.get('status') == 'pending'])
        stats['pending_programs'] = pending_count
    
    # Recent activities
    recent_tolis = db.get_all_tolis()[:5]
    recent_students = db.get_all_users('student')[:5]
    
    # Get recent programs safely
    try:
        recent_programs = db.get_all_programs()[:5]
    except:
        recent_programs = []
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_tolis=recent_tolis,
                         recent_students=recent_students,
                         recent_programs=recent_programs)

# Toli Management Routes - UPDATED
@admin.route('/admin/tolis')
@login_required
def manage_tolis():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    tolis_data = db.get_all_tolis()
    tolis = [Toli(toli) for toli in tolis_data]
    
    # Separate tolis by status
    pending_tolis = [toli for toli in tolis if toli.status == 'pending']
    approved_tolis = [toli for toli in tolis if toli.status == 'approved']
    active_tolis = [toli for toli in tolis if toli.status == 'active']
    rejected_tolis = [toli for toli in tolis if toli.status == 'rejected']
    
    return render_template('admin/manage_tolis.html', 
                         pending_tolis=pending_tolis,
                         approved_tolis=approved_tolis,
                         active_tolis=active_tolis,
                         rejected_tolis=rejected_tolis)

@admin.route('/admin/toli/<toli_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_toli(toli_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        flash('Toli not found.', 'danger')
        return redirect(url_for('admin.manage_tolis'))
    
    toli = Toli(toli_data)
    form = AdminManageToliForm()
    
    if form.validate_on_submit():
        location_data = {
            'city': form.city.data,
            'state': form.state.data
        }
        
        update_data = {
            'location': location_data,
            'coordinator_name': form.coordinator_name.data,
            'coordinator_contact': form.coordinator_contact.data,
            'status': form.status.data
        }
        
        if form.status.data == 'approved' and toli.status != 'approved':
            update_data['approved_at'] = datetime.utcnow()
        
        if db.update_toli(toli_id, update_data):
            flash('Toli updated successfully!', 'success')
            return redirect(url_for('admin.manage_tolis'))
        else:
            flash('Error updating toli.', 'danger')
    
    # Pre-fill form with existing data
    if toli.location:
        form.city.data = toli.location.get('city', '')
        form.state.data = toli.location.get('state', '')
    form.coordinator_name.data = toli.coordinator_name
    form.coordinator_contact.data = toli.coordinator_contact
    form.status.data = toli.status
    
    # Get leader info
    leader = None
    if toli.leader_id:
        leader_data = db.get_user_by_id(toli.leader_id)
        if leader_data:
            leader = User(leader_data)
    
    return render_template('admin/manage_toli.html', form=form, toli=toli, leader=leader)

@admin.route('/admin/toli/<toli_id>/delete', methods=['POST'])
@login_required
def delete_toli(toli_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Implementation for deleting toli
    # (You'll need to add delete_toli method to database.py)
    flash('Toli deletion feature coming soon!', 'info')
    return redirect(url_for('admin.manage_tolis'))

# REMOVE the old create_toli route since students create tolis now
# @admin.route('/admin/toli/create', methods=['GET', 'POST'])

# Student Management Routes
@admin.route('/admin/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    form = AddStudentForm()
    
    # Get available tolis with less than 4 members
    available_tolis = db.get_tolis_with_available_slots()
    form.toli_id.choices = [('', 'Select Toli (Optional)')] + [(str(toli['_id']), f"{toli['name']} - {toli['location']} ({toli.get('member_count', 0)}/4 members)") for toli in available_tolis]
    
    if form.validate_on_submit():
        # Check if student exists
        if db.get_user_by_scholar_no(form.scholar_no.data) or db.get_user_by_email(form.email.data):
            flash('Student with this scholar number or email already exists!', 'danger')
        else:
            student_data = {
                'scholar_no': form.scholar_no.data,
                'name': form.name.data,
                'email': form.email.data,
                'dob': datetime.combine(form.dob.data, datetime.min.time()),
                'course': form.course.data,
                'contact': form.contact.data,
                'toli_id': form.toli_id.data if form.toli_id.data else None,
                'role': 'student',
                'created_at': datetime.utcnow()
            }
            
            student = User(student_data)
            student.set_password(form.scholar_no.data)  # Default password
            
            if db.create_user(student.to_dict()):
                # If toli is selected, add student to toli
                if form.toli_id.data:
                    toli_data = db.get_toli_by_id(form.toli_id.data)
                    if toli_data:
                        updated_member_ids = toli_data.get('member_ids', []) + [student.id]
                        db.update_toli(form.toli_id.data, {'member_ids': updated_member_ids})
                
                flash(f'Student {student.name} added successfully!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Error adding student.', 'danger')
    
    return render_template('admin/add_student.html', form=form)

@admin.route('/admin/upload-resource', methods=['GET', 'POST'])
@login_required
def upload_resource():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    form = UploadResourceForm()
    
    if form.validate_on_submit():
        resource_data = {
            'title': form.title.data,
            'description': form.description.data,
            'resource_type': form.resource_type.data,
            'created_by': current_user.id,
            'created_at': datetime.utcnow()
        }
        
        # Handle file upload (simplified)
        if form.file.data:
            from app.utils import save_file
            filename = save_file(form.file.data, 'resources')
            if filename:
                resource_data['file_path'] = filename
        
        resource = Resource(resource_data)
        if db.create_resource(resource.to_dict()):
            flash('Resource uploaded successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Error uploading resource.', 'danger')
    
    return render_template('admin/upload_resource.html', form=form)

@admin.route('/admin/send-message', methods=['GET', 'POST'])
@login_required
def send_message():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    form = SendMessageForm()
    students = db.get_all_users('student')
    form.receiver_id.choices = [('all', 'All Students')] + [(str(student['_id']), student['name']) for student in students]
    
    if form.validate_on_submit():
        message_data = {
            'title': form.title.data,
            'content': form.content.data,
            'sender_id': current_user.id,
            'receiver_id': None if form.receiver_id.data == 'all' else form.receiver_id.data,
            'created_at': datetime.utcnow(),
            'is_read': False
        }
        
        message = Message(message_data)
        if db.create_message(message.to_dict()):
            flash('Message sent successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Error sending message.', 'danger')
    
    return render_template('admin/send_message.html', form=form)

# API endpoints for interactive features
@admin.route('/admin/api/toli-stats')
@login_required
def api_toli_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    stats = {
        'total_tolis': db.count_tolis(),
        'active_tolis': db.count_active_tolis(),
        'tolis_by_session': db.get_tolis_by_session(),
        'average_members_per_toli': db.get_average_members_per_toli()
    }
    return jsonify(stats)