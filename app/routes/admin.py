from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length
import os
from werkzeug.utils import secure_filename
from app.models import User, Toli, Program, Resource, Message
from app.forms import AdminManageToliForm, AssignLocationForm, AddStudentForm, UploadResourceForm, SendMessageForm
from app.database import MongoDB
from datetime import datetime
import json

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

# Cities data
CITIES = [
    {"City/Town": "Haridwar", "State": "Uttarakhand"},
    {"City/Town": "Rishikesh", "State": "Uttarakhand"},
    {"City/Town": "Dehradun", "State": "Uttarakhand"},
    {"City/Town": "Roorkee", "State": "Uttarakhand"},
    {"City/Town": "Delhi", "State": "Delhi"},
    {"City/Town": "Mumbai", "State": "Maharashtra"},
    {"City/Town": "Bangalore", "State": "Karnataka"},
    {"City/Town": "Chennai", "State": "Tamil Nadu"},
    {"City/Town": "Kolkata", "State": "West Bengal"},
    {"City/Town": "Hyderabad", "State": "Telangana"},
    {"City/Town": "Ahmedabad", "State": "Gujarat"},
    {"City/Town": "Pune", "State": "Maharashtra"},
    {"City/Town": "Jaipur", "State": "Rajasthan"},
    {"City/Town": "Lucknow", "State": "Uttar Pradesh"},
    {"City/Town": "Kanpur", "State": "Uttar Pradesh"},
    {"City/Town": "Nagpur", "State": "Maharashtra"},
    {"City/Town": "Indore", "State": "Madhya Pradesh"},
    {"City/Town": "Thane", "State": "Maharashtra"},
    {"City/Town": "Bhopal", "State": "Madhya Pradesh"},
    {"City/Town": "Visakhapatnam", "State": "Andhra Pradesh"},
    {"City/Town": "Patna", "State": "Bihar"},
    {"City/Town": "Vadodara", "State": "Gujarat"},
    {"City/Town": "Ghaziabad", "State": "Uttar Pradesh"},
    {"City/Town": "Ludhiana", "State": "Punjab"},
    {"City/Town": "Agra", "State": "Uttar Pradesh"},
    {"City/Town": "Nashik", "State": "Maharashtra"},
    {"City/Town": "Faridabad", "State": "Haryana"},
    {"City/Town": "Meerut", "State": "Uttar Pradesh"},
    {"City/Town": "Rajkot", "State": "Gujarat"},
    {"City/Town": "Kalyan-Dombivali", "State": "Maharashtra"},
    {"City/Town": "Vasai-Virar", "State": "Maharashtra"},
    {"City/Town": "Varanasi", "State": "Uttar Pradesh"},
    {"City/Town": "Srinagar", "State": "Jammu and Kashmir"},
    {"City/Town": "Aurangabad", "State": "Maharashtra"},
    {"City/Town": "Dhanbad", "State": "Jharkhand"},
    {"City/Town": "Amritsar", "State": "Punjab"},
    {"City/Town": "Navi Mumbai", "State": "Maharashtra"},
    {"City/Town": "Allahabad", "State": "Uttar Pradesh"},
    {"City/Town": "Ranchi", "State": "Jharkhand"},
    {"City/Town": "Howrah", "State": "West Bengal"},
    {"City/Town": "Coimbatore", "State": "Tamil Nadu"},
    {"City/Town": "Jabalpur", "State": "Madhya Pradesh"},
    {"City/Town": "Gwalior", "State": "Madhya Pradesh"},
    {"City/Town": "Vijayawada", "State": "Andhra Pradesh"},
    {"City/Town": "Jodhpur", "State": "Rajasthan"},
    {"City/Town": "Madurai", "State": "Tamil Nadu"},
    {"City/Town": "Raipur", "State": "Chhattisgarh"},
    {"City/Town": "Kota", "State": "Rajasthan"},
    {"City/Town": "Chandigarh", "State": "Chandigarh"}
]

# ==================== DASHBOARD & MAIN ROUTES ====================

@admin.route('/admin/')
@admin.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Enhanced statistics
    total_students = db.count_users_by_role('student')
    total_tolis = db.count_tolis()
    active_tolis = db.count_active_tolis()
    pending_tolis = len([t for t in db.get_all_tolis() if t.get('status') == 'pending'])
    total_resources = db.count_resources()
    total_programs = db.count_programs()
    
    # Get student login stats
    students = db.get_all_users('student')
    active_students = len([s for s in students if s.get('last_login')])
    
    stats = {
        'total_students': total_students,
        'active_students': active_students,
        'total_tolis': total_tolis,
        'active_tolis': active_tolis,
        'pending_tolis': pending_tolis,
        'total_programs': total_programs,
        'total_resources': total_resources
    }
    
    # Recent activities
    recent_activities = [
        {'type': 'toli', 'icon': 'users', 'message': 'New toli registration from Delhi', 'time': '2 minutes ago'},
        {'type': 'student', 'icon': 'user-plus', 'message': '5 new students registered', 'time': '1 hour ago'},
        {'type': 'program', 'icon': 'calendar-check', 'message': 'Yagya program completed in Mumbai', 'time': '3 hours ago'},
        {'type': 'resource', 'icon': 'file-upload', 'message': 'New resource uploaded', 'time': '5 hours ago'}
    ]
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_activities=recent_activities,
                         now=datetime.utcnow())

@admin.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Forms for profile update and password change
    # Implementation for updating admin profile
    
    return render_template('admin/profile.html')

@admin.route('/admin/instructions')
@login_required
def instructions():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    return render_template('admin/instructions.html')

@admin.route('/admin/analytics')
@login_required
def analytics_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Analytics data
    tolis_by_state = db.get_tolis_by_state()
    program_stats = db.get_program_statistics()
    student_engagement = db.get_student_engagement_stats()
    
    return render_template('admin/analytics.html',
                         tolis_by_state=tolis_by_state,
                         program_stats=program_stats,
                         student_engagement=student_engagement)

@admin.route('/admin/settings')
@login_required
def settings():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    return render_template('admin/settings.html')

# ==================== TOLI MANAGEMENT ROUTES ====================

@admin.route('/admin/manage-tolis')
@login_required
def manage_tolis():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Get all tolis with their details
    all_tolis_data = db.get_all_tolis()
    tolis = []
    
    for toli_data in all_tolis_data:
        toli = Toli(toli_data)
        
        # Get leader info
        leader = None
        if toli.leader_id:
            leader_data = db.get_user_by_id(toli.leader_id)
            if leader_data:
                leader = User(leader_data)
        
        # Get member count from members list (based on your Toli model)
        member_count = len(toli.members) if toli.members else 0
        
        # Get location information safely
        location = toli_data.get('location', {})
        city = location.get('city', 'Not assigned') if location else 'Not assigned'
        state = location.get('state', '') if location else ''
        
        # Get programs for this toli
        programs = db.get_programs_by_toli(toli.id)
        
        tolis.append({
            'toli': toli,
            'toli_data': toli_data,
            'leader': leader,
            'member_count': member_count,
            'is_full': member_count >= 4,
            'city': city,
            'state': state,
            'session_year': toli_data.get('session_year', '2024'),
            'programs_completed': len(programs),
            'status': toli_data.get('status', 'pending')
        })
    
    # Get students without tolis for statistics
    all_students = db.get_all_users('student')
    students_without_toli = [s for s in all_students if not s.get('toli_id')]
    
    return render_template('admin/manage_tolis.html', 
                         tolis=tolis, 
                         students_without_toli=students_without_toli)

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
    
    # Forms
    status_form = AdminManageToliForm()
    location_form = AssignLocationForm()
    
    # Populate location choices
    location_form.location.choices = [('', 'Select Location')] + [
        (f"{city['City/Town']}, {city['State']}", f"{city['City/Town']} ({city['State']})") 
        for city in CITIES
    ]
    
    # Handle status update
    if status_form.validate_on_submit():
        update_data = {
            'status': status_form.status.data
        }
        
        if status_form.status.data == 'approved' and toli.status != 'approved':
            update_data['approved_at'] = datetime.utcnow()
        
        if db.update_toli(toli_id, update_data):
            flash('Toli status updated successfully!', 'success')
            return redirect(url_for('admin.manage_toli', toli_id=toli_id))
        else:
            flash('Error updating toli status.', 'danger')
    
    # Handle location assignment
    if location_form.validate_on_submit():
        # Split location into city and state
        location_parts = location_form.location.data.split(', ')
        city = location_parts[0] if len(location_parts) > 0 else ''
        state = location_parts[1] if len(location_parts) > 1 else ''
        
        location_data = {
            'city': city,
            'state': state
        }
        
        update_data = {
            'toli_no': location_form.toli_no.data,
            'name': f"Toli {location_form.toli_no.data}",
            'location': location_data,
            'coordinator_name': location_form.coordinator_name.data,
            'coordinator_contact': location_form.coordinator_contact.data,
            'status': 'active',  # Activate the toli
            'approved_at': datetime.utcnow()
        }
        
        if db.update_toli(toli_id, update_data):
            flash(f'Toli {location_form.toli_no.data} activated successfully with location assignment!', 'success')
            return redirect(url_for('admin.manage_toli', toli_id=toli_id))
        else:
            flash('Error assigning location.', 'danger')
    
    # Set current form values
    status_form.status.data = toli.status
    
    if toli.location:
        location_form.location.data = f"{toli.location.get('city', '')}, {toli.location.get('state', '')}"
    if toli.toli_no:
        location_form.toli_no.data = toli.toli_no
    if toli.coordinator_name:
        location_form.coordinator_name.data = toli.coordinator_name
    if toli.coordinator_contact:
        location_form.coordinator_contact.data = toli.coordinator_contact
    
    # Get leader info
    leader = None
    if toli.leader_id:
        leader_data = db.get_user_by_id(toli.leader_id)
        if leader_data:
            leader = User(leader_data)
    
    # Get team members
    team_members = []
    if toli.members:
        for member_data in toli.members:
            # If member is a dictionary (from toli members list)
            if isinstance(member_data, dict):
                team_members.append({
                    'name': member_data.get('name', ''),
                    'scholar_no': member_data.get('scholar_no', ''),
                    'course': member_data.get('course', ''),
                    'email': member_data.get('email', ''),
                    'is_leader': member_data.get('is_leader', False)
                })
    
    # Get programs for this toli
    programs_data = db.get_programs_by_toli(toli_id)
    programs = []
    for program_data in programs_data:
        program = Program(program_data)
        programs.append({
            'id': program.id,
            'title': program.title,
            'description': program.description,
            'program_type': program.program_type,
            'location': program.location,
            'start_date': program.start_date,
            'status': program.status,
            'participants_count': len(program.participants) if program.participants else 0
        })
    
    return render_template('admin/manage_toli.html', 
                         status_form=status_form, 
                         location_form=location_form,
                         toli=toli, 
                         leader=leader,
                         team_members=team_members,
                         programs=programs)

@admin.route('/admin/toli/<toli_id>/approve', methods=['GET', 'POST'])
@login_required
def approve_toli(toli_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        flash('Toli not found.', 'danger')
        return redirect(url_for('admin.manage_tolis'))
    
    toli = Toli(toli_data)
    
    # Only allow approval of pending tolis
    if toli.status != 'pending':
        flash('Toli is not in pending status.', 'warning')
        return redirect(url_for('admin.manage_tolis'))
    
    # Update toli status to approved
    update_data = {
        'status': 'approved',
        'approved_at': datetime.utcnow()
    }
    
    if db.update_toli(toli_id, update_data):
        flash(f'Toli approved successfully! Now assign location and coordinator details.', 'success')
        # Redirect to assign location page
        return redirect(url_for('admin.assign_location', toli_id=toli_id))
    else:
        flash('Error approving toli.', 'danger')
        return redirect(url_for('admin.manage_tolis'))     

@admin.route('/admin/toli/<toli_id>/assign-location', methods=['GET', 'POST'])
@login_required
def assign_location(toli_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        flash('Toli not found.', 'danger')
        return redirect(url_for('admin.manage_tolis'))
    
    toli = Toli(toli_data)
    
    # Only allow location assignment for approved tolis
    if toli.status != 'approved':
        flash('Toli must be approved before assigning location.', 'warning')
        return redirect(url_for('admin.manage_toli', toli_id=toli_id))
    
    form = AssignLocationForm()
    
    # Populate location choices
    form.location.choices = [('', 'Select Location')] + [
        (f"{city['City/Town']}, {city['State']}", f"{city['City/Town']} ({city['State']})") 
        for city in CITIES
    ]
    
    if form.validate_on_submit():
        # Split location into city and state
        location_parts = form.location.data.split(', ')
        city = location_parts[0] if len(location_parts) > 0 else ''
        state = location_parts[1] if len(location_parts) > 1 else ''
        
        location_data = {
            'city': city,
            'state': state
        }
        
        update_data = {
            'toli_no': form.toli_no.data,
            'name': f"Toli {form.toli_no.data}",
            'location': location_data,
            'coordinator_name': form.coordinator_name.data,
            'coordinator_contact': form.coordinator_contact.data,
            'status': 'active',  # Activate the toli
            'approved_at': datetime.utcnow()
        }
        
        if db.update_toli(toli_id, update_data):
            flash(f'Toli {form.toli_no.data} activated successfully with location assignment!', 'success')
            return redirect(url_for('admin.manage_tolis'))
        else:
            flash('Error assigning location.', 'danger')
    
    return render_template('admin/assign_location.html', form=form, toli=toli)

@admin.route('/admin/toli/<toli_id>/add-members', methods=['GET', 'POST'])
@login_required
def add_members_to_toli(toli_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        flash('Toli not found.', 'danger')
        return redirect(url_for('admin.manage_tolis'))
    
    toli = Toli(toli_data)
    
    # Get current members count from members list (based on your Toli model)
    current_member_count = len(toli.members) if toli.members else 0
    
    # Calculate available slots
    available_slots = 4 - current_member_count
    
    if available_slots <= 0:
        flash('This toli is already full (4/4 members).', 'warning')
        return redirect(url_for('admin.manage_tolis'))
    
    # Get students without tolis
    all_students = db.get_all_users('student')
    available_students = [
        student for student in all_students 
        if not student.get('toli_id')  # Students without toli assignment
    ]
    
    # Create a simple form for member selection
    class SimpleMemberForm(FlaskForm):
        student_ids = SelectMultipleField('Select Students', 
                                        validators=[DataRequired()],
                                        choices=[],
                                        render_kw={'class': 'form-select h-32', 'size': '6'})
        submit = SubmitField('Add Members', render_kw={'class': 'btn-primary'})
    
    form = SimpleMemberForm()
    
    # Populate student choices
    form.student_ids.choices = [
        (str(student['_id']), f"{student['name']} ({student['scholar_no']} - {student['course']})") 
        for student in available_students
    ]
    
    if form.validate_on_submit():
        selected_student_ids = form.student_ids.data
        
        if len(selected_student_ids) > available_slots:
            flash(f'You can only add {available_slots} more member(s) to this toli.', 'danger')
            return render_template('admin/add_members_to_toli.html', 
                                 form=form, toli=toli, available_slots=available_slots,
                                 available_students=available_students)
        
        # Update students with toli_id
        success_count = 0
        for student_id in selected_student_ids:
            # Update student's toli_id
            student_update = db.update_user(student_id, {'toli_id': toli_id})
            if student_update:
                # Add student to toli's members list
                toli_data = db.get_toli_by_id(toli_id)
                if toli_data:
                    toli = Toli(toli_data)
                    current_members = toli.members.copy() if toli.members else []
                    
                    student_data = db.get_user_by_id(student_id)
                    if student_data:
                        new_member = {
                            'name': student_data['name'],
                            'scholar_no': student_data['scholar_no'],
                            'course': student_data['course'],
                            'email': student_data['email'],
                            'is_leader': False
                        }
                        current_members.append(new_member)
                        
                        # Update toli with new member
                        db.update_toli(toli_id, {'members': current_members})
                        success_count += 1
        
        if success_count > 0:
            flash(f'Successfully added {success_count} member(s) to {toli.name}!', 'success')
            return redirect(url_for('admin.manage_tolis'))
        else:
            flash('Error adding members to toli.', 'danger')
    
    return render_template('admin/add_members_to_toli.html', 
                         form=form, toli=toli, available_slots=available_slots,
                         available_students=available_students)

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

# ==================== STUDENT MANAGEMENT ROUTES ====================

@admin.route('/admin/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    form = AddStudentForm()
    
    # Get available tolis with less than 4 members
    available_tolis = []
    all_tolis = db.get_all_tolis()
    for toli_data in all_tolis:
        toli = Toli(toli_data)
        member_count = len(toli.members) if toli.members else 0
        if member_count < 4:
            location_info = ""
            if toli.location and toli.location.get('city'):
                location_info = f" - {toli.location.get('city')}"
                if toli.location.get('state'):
                    location_info += f", {toli.location.get('state')}"
            
            available_tolis.append({
                'id': toli.id,
                'name': f"{toli.name}{location_info} ({member_count}/4 members)"
            })
    
    # Populate toli choices
    form.toli_id.choices = [('', 'Select Toli (Optional)')] + [
        (toli['id'], toli['name']) for toli in available_tolis
    ]
    
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
                # If toli is selected, add student to toli's members list
                if form.toli_id.data:
                    toli_data = db.get_toli_by_id(form.toli_id.data)
                    if toli_data:
                        toli = Toli(toli_data)
                        current_members = toli.members.copy() if toli.members else []
                        
                        # Add new member to toli
                        new_member = {
                            'name': form.name.data,
                            'scholar_no': form.scholar_no.data,
                            'course': form.course.data,
                            'email': form.email.data,
                            'is_leader': False
                        }
                        current_members.append(new_member)
                        
                        # Update toli with new member
                        db.update_toli(form.toli_id.data, {'members': current_members})
                
                flash(f'Student {student.name} added successfully!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Error adding student.', 'danger')
    
    return render_template('admin/add_student.html', form=form)

# ==================== RESOURCE MANAGEMENT ROUTES ====================

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
            'created_at': datetime.utcnow(),
            'file_path': '',
            'external_link': '',
            'file_size': 0,
            'file_name': ''
        }
        
        # Handle file upload
        if form.file.data:
            from app.utils import save_file, get_file_size
            filename = save_file(form.file.data, 'resources')
            if filename:
                resource_data['file_path'] = filename
                resource_data['file_name'] = form.file.data.filename
                resource_data['file_size'] = get_file_size(form.file.data)
        
        # Handle external link
        if form.external_link.data:
            resource_data['external_link'] = form.external_link.data
        
        resource = Resource(resource_data)
        if db.create_resource(resource.to_dict()):
            flash('Resource uploaded successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Error uploading resource.', 'danger')
    
    return render_template('admin/upload_resource.html', form=form)

@admin.route('/admin/resources')
@login_required
def view_resources():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    resources_data = db.get_all_resources()
    resources = [Resource(resource) for resource in resources_data]
    
    return render_template('admin/resources.html', resources=resources)

@admin.route('/admin/resource/<resource_id>/delete', methods=['POST'])
@login_required
def delete_resource(resource_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Implementation for deleting resource
    # You'll need to add delete_resource method to database.py
    flash('Resource deletion feature coming soon!', 'info')
    return redirect(url_for('admin.view_resources'))

# ==================== MESSAGE MANAGEMENT ROUTES ====================

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

# ==================== API ENDPOINTS ====================

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

@admin.route('/admin/api/analytics/map-data')
@login_required
def api_map_data():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Generate data for India map
    map_data = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Add toli locations to map
    tolis = db.get_all_tolis()
    for toli in tolis:
        if toli.get('location') and toli['location'].get('city'):
            feature = {
                "type": "Feature",
                "properties": {
                    "name": toli.get('name', 'Unknown'),
                    "members": len(toli.get('members', [])),
                    "programs": len(toli.get('programs', [])),
                    "status": toli.get('status', 'unknown')
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": get_coordinates_for_city(toli['location']['city'])
                }
            }
            map_data["features"].append(feature)
    
    return jsonify(map_data)

@admin.route('/admin/api/analytics/program-stats')
@login_required
def api_program_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    stats = {
        'programs_by_type': db.get_programs_by_type(),
        'monthly_trends': db.get_monthly_program_trends(),
        'completion_rates': db.get_program_completion_rates()
    }
    return jsonify(stats)

@admin.route('/admin/toli/<toli_id>/search-student', methods=['POST'])
@login_required
def search_student(toli_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    scholar_no = request.json.get('scholar_no')
    student = db.get_user_by_scholar_no(scholar_no)
    
    if student and student.get('role') == 'student':
        # Check if student is already in a toli
        if student.get('toli_id'):
            return jsonify({'error': 'Student is already assigned to a toli'}), 400
        
        return jsonify({
            'name': student['name'],
            'scholar_no': student['scholar_no'],
            'course': student['course'],
            'email': student['email'],
            'contact': student.get('contact', ''),
            'dob': student.get('dob', '')
        })
    
    return jsonify({'error': 'Student not found'}), 404

@admin.route('/admin/toli/<toli_id>/assign-leader', methods=['POST'])
@login_required
def assign_leader(toli_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    scholar_no = request.json.get('scholar_no')
    
    # Get toli data
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        return jsonify({'error': 'Toli not found'}), 404
    
    toli = Toli(toli_data)
    
    # Update all members to remove leader status
    updated_members = []
    for member in toli.members:
        if isinstance(member, dict):
            updated_member = member.copy()
            updated_member['is_leader'] = (member.get('scholar_no') == scholar_no)
            updated_members.append(updated_member)
    
    # Update toli with new leader
    update_data = {
        'members': updated_members,
        'leader_id': None  # You might want to set this to the student's user ID
    }
    
    # Find the student and set as leader_id
    student = db.get_user_by_scholar_no(scholar_no)
    if student:
        update_data['leader_id'] = student['_id']
    
    if db.update_toli(toli_id, update_data):
        return jsonify({'success': True, 'message': 'Leader assigned successfully'})
    else:
        return jsonify({'error': 'Failed to assign leader'}), 500

@admin.route('/admin/toli/<toli_id>/send-message', methods=['POST'])
@login_required
def send_toli_message(toli_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    title = request.json.get('title')
    content = request.json.get('content')
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    
    # Get toli members
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        return jsonify({'error': 'Toli not found'}), 404
    
    toli = Toli(toli_data)
    
    # Send message to each member
    success_count = 0
    if toli.members:
        for member in toli.members:
            if isinstance(member, dict):
                # Find student by email or scholar_no
                student = db.get_user_by_email(member.get('email')) or db.get_user_by_scholar_no(member.get('scholar_no'))
                if student:
                    message_data = {
                        'title': f"[Toli {toli.name}] {title}",
                        'content': content,
                        'sender_id': current_user.id,
                        'receiver_id': student['_id'],
                        'created_at': datetime.utcnow(),
                        'is_read': False
                    }
                    
                    if db.create_message(message_data):
                        success_count += 1
    
    if success_count > 0:
        return jsonify({'success': True, 'message': f'Message sent to {success_count} members'})
    else:
        return jsonify({'error': 'Failed to send message to any members'}), 500

@admin.route('/admin/toli/<toli_id>/add-student', methods=['POST'])
@login_required
def add_student_to_toli(toli_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    scholar_no = request.json.get('scholar_no')
    
    # Get student
    student = db.get_user_by_scholar_no(scholar_no)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Check if student is already in a toli
    if student.get('toli_id'):
        return jsonify({'error': 'Student is already in a toli'}), 400
    
    # Get toli
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        return jsonify({'error': 'Toli not found'}), 404
    
    toli = Toli(toli_data)
    
    # Check if toli has space
    if len(toli.members) >= 4:
        return jsonify({'error': 'Toli is already full'}), 400
    
    # Update student with toli_id
    student_update = db.update_user(student['_id'], {'toli_id': toli_id})
    if not student_update:
        return jsonify({'error': 'Failed to update student'}), 500
    
    # Add student to toli's members list
    current_members = toli.members.copy() if toli.members else []
    new_member = {
        'name': student['name'],
        'scholar_no': student['scholar_no'],
        'course': student['course'],
        'email': student['email'],
        'is_leader': False
    }
    current_members.append(new_member)
    
    # Update toli with new member
    toli_update = db.update_toli(toli_id, {'members': current_members})
    if toli_update:
        return jsonify({'success': True, 'message': 'Student added to toli successfully'})
    else:
        # Rollback student update if toli update fails
        db.update_user(student['_id'], {'toli_id': None})
        return jsonify({'error': 'Failed to add student to toli'}), 500

@admin.route('/admin/toli/<toli_id>/remove-member', methods=['POST'])
@login_required
def remove_member_from_toli(toli_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    scholar_no = request.json.get('scholar_no')
    
    # Get toli
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        return jsonify({'error': 'Toli not found'}), 404
    
    toli = Toli(toli_data)
    
    # Remove member from toli
    updated_members = []
    for member in toli.members:
        if isinstance(member, dict) and member.get('scholar_no') != scholar_no:
            updated_members.append(member)
    
    # Update toli members
    toli_update = db.update_toli(toli_id, {'members': updated_members})
    if not toli_update:
        return jsonify({'error': 'Failed to remove member from toli'}), 500
    
    # Update student's toli_id to None
    student = db.get_user_by_scholar_no(scholar_no)
    if student:
        db.update_user(student['_id'], {'toli_id': None})
    
    return jsonify({'success': True, 'message': 'Member removed from toli successfully'})

# ==================== HELPER FUNCTIONS ====================

def get_coordinates_for_city(city_name):
    # This is a simplified version - you'll need proper geocoding
    coordinates_map = {
        'Delhi': [77.1025, 28.7041],
        'Mumbai': [72.8777, 19.0760],
        'Bangalore': [77.5946, 12.9716],
        'Chennai': [80.2707, 13.0827],
        'Kolkata': [88.3639, 22.5726],
        'Hyderabad': [78.4867, 17.3850],
        'Pune': [73.8567, 18.5204],
        'Ahmedabad': [72.5714, 23.0225],
        'Jaipur': [75.7873, 26.9124],
        'Lucknow': [80.9462, 26.8467],
        'Haridwar': [78.1642, 29.9457],
        'Rishikesh': [78.2676, 30.0869],
        'Dehradun': [78.0322, 30.3165],
        'Roorkee': [77.8888, 29.8543]
    }
    return coordinates_map.get(city_name, [77.2090, 28.6139])  # Default to Delhi

# ==================== PROGRAM REPORT ROUTES ====================

@admin.route('/admin/program/<program_id>/report')
@login_required
def view_program_report(program_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    program_data = db.get_program_by_id(program_id)
    if not program_data:
        flash('Program not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    program = Program(program_data)
    return render_template('admin/program_report.html', program=program)

# ==================== ADDITIONAL ANALYTICS ROUTES ====================

@admin.route('/admin/api/toli/<toli_id>/analytics')
@login_required
def api_toli_analytics(toli_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get toli programs
    programs = db.get_programs_by_toli(toli_id)
    
    # Calculate analytics
    program_types = {}
    monthly_stats = {}
    
    for program_data in programs:
        program = Program(program_data)
        
        # Count by program type
        program_type = program.program_type
        program_types[program_type] = program_types.get(program_type, 0) + 1
        
        # Count by month
        month_key = program.start_date.strftime('%Y-%m') if program.start_date else 'Unknown'
        monthly_stats[month_key] = monthly_stats.get(month_key, 0) + 1
    
    return jsonify({
        'program_types': program_types,
        'monthly_stats': monthly_stats,
        'total_programs': len(programs),
        'completed_programs': len([p for p in programs if p.get('status') == 'completed']),
        'ongoing_programs': len([p for p in programs if p.get('status') == 'ongoing'])
    })

# Add these new routes to your admin.py

@admin.route('/admin/toli/<toli_id>/programs')
@login_required
def view_toli_programs(toli_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    toli_data = db.get_toli_by_id(toli_id)
    if not toli_data:
        flash('Toli not found.', 'danger')
        return redirect(url_for('admin.manage_tolis'))
    
    toli = Toli(toli_data)
    
    # Get all programs for this toli
    programs_data = db.get_programs_by_toli(toli_id)
    programs = []
    
    for program_data in programs_data:
        program = Program(program_data)
        programs.append({
            'id': program.id,
            'program_no': program_data.get('program_no', 'N/A'),
            'title': program.title,
            'description': program.description,
            'program_type': program.program_type,
            'location': program.location,
            'pincode': program_data.get('pincode', 'N/A'),
            'start_date': program.start_date,
            'end_date': program.end_date,
            'organizer_name': program_data.get('organizer_name', 'N/A'),
            'organizer_contact': program_data.get('organizer_contact', 'N/A'),
            'attendees_count': len(program.participants) if program.participants else 0,
            'feedback': program_data.get('feedback', 'No feedback yet'),
            'images': program_data.get('images', []),
            'status': program.status,
            'created_at': program.created_at
        })
    
    # Calculate analytics
    program_analytics = calculate_program_analytics(programs)
    
    return render_template('admin/toli_programs.html',
                         toli=toli,
                         programs=programs,
                         analytics=program_analytics)

@admin.route('/admin/toli/<toli_id>/program/<program_id>')
@login_required
def view_program_details(toli_id, program_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    program_data = db.get_program_by_id(program_id)
    if not program_data:
        flash('Program not found.', 'danger')
        return redirect(url_for('admin.view_toli_programs', toli_id=toli_id))
    
    program = Program(program_data)
    
    # Get toli info
    toli_data = db.get_toli_by_id(toli_id)
    toli = Toli(toli_data) if toli_data else None
    
    # Format program data for display
    program_details = {
        'id': program.id,
        'program_no': program_data.get('program_no', 'N/A'),
        'title': program.title,
        'description': program.description,
        'program_type': program.program_type,
        'location': program.location,
        'pincode': program_data.get('pincode', 'N/A'),
        'start_date': program.start_date,
        'end_date': program.end_date,
        'organizer_name': program_data.get('organizer_name', 'N/A'),
        'organizer_contact': program_data.get('organizer_contact', 'N/A'),
        'attendees': program.participants if program.participants else [],
        'feedback': program_data.get('feedback', 'No feedback yet'),
        'images': program_data.get('images', []),
        'status': program.status,
        'created_at': program.created_at
    }
    
    return render_template('admin/program_details.html',
                         toli=toli,
                         program=program_details)

@admin.route('/admin/toli/<toli_id>/program/<program_id>/delete', methods=['POST'])
@login_required
def delete_program(toli_id, program_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Implementation for deleting program
    if db.delete_program(program_id):
        flash('Program deleted successfully!', 'success')
    else:
        flash('Error deleting program.', 'danger')
    
    return redirect(url_for('admin.view_toli_programs', toli_id=toli_id))

@admin.route('/admin/api/toli/<toli_id>/program-analytics')
@login_required
def api_toli_program_analytics(toli_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    programs_data = db.get_programs_by_toli(toli_id)
    programs = []
    
    for program_data in programs_data:
        program = Program(program_data)
        programs.append({
            'program_type': program.program_type,
            'start_date': program.start_date.strftime('%Y-%m-%d') if program.start_date else None,
            'attendees_count': len(program.participants) if program.participants else 0,
            'status': program.status
        })
    
    analytics = calculate_program_analytics(programs)
    return jsonify(analytics)

def calculate_program_analytics(programs):
    """Calculate analytics for programs"""
    program_types = {}
    monthly_stats = {}
    status_count = {
        'completed': 0,
        'ongoing': 0,
        'planned': 0,
        'cancelled': 0
    }
    
    total_attendees = 0
    day_wise_comparison = {}
    
    for program in programs:
        # Count by program type
        program_type = program.get('program_type', 'Other')
        program_types[program_type] = program_types.get(program_type, 0) + 1
        
        # Count by status
        status = program.get('status', 'planned')
        if status in status_count:
            status_count[status] += 1
        
        # Count by month
        if program.get('start_date'):
            month_key = program['start_date'].strftime('%Y-%m')
            monthly_stats[month_key] = monthly_stats.get(month_key, 0) + 1
            
            # Day-wise comparison
            day_key = program['start_date'].strftime('%A')
            day_wise_comparison[day_key] = day_wise_comparison.get(day_key, 0) + 1
        
        # Total attendees
        total_attendees += program.get('attendees_count', 0)
    
    return {
        'program_types': program_types,
        'monthly_stats': monthly_stats,
        'status_count': status_count,
        'total_programs': len(programs),
        'total_attendees': total_attendees,
        'day_wise_comparison': day_wise_comparison,
        'average_attendees': total_attendees / len(programs) if programs else 0
    }