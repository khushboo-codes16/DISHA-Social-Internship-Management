from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import User, Toli, Program, Resource, Message
from app.forms import StudentCreateToliForm, CreateProgramForm
from app.database import MongoDB
from datetime import datetime

student = Blueprint('student', __name__)
db = MongoDB()

@student.route('/student/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Get student's toli info
    toli_data = None
    team_members = []
    if current_user.toli_id:
        toli_data = db.get_toli_by_id(current_user.toli_id)
        if toli_data:
            toli = Toli(toli_data)
            # Get team members details
            for member in toli.members:
                member_data = db.get_user_by_scholar_no(member['scholar_no'])
                if member_data:
                    team_members.append(User(member_data))
    
    # Get student's programs
    programs_data = db.get_programs_by_student(current_user.id)
    programs = [Program(program) for program in programs_data]
    
    # Get recent resources
    resources_data = db.get_all_resources()[:5]
    resources = [Resource(resource) for resource in resources_data]
    
    # Get unread messages
    messages_data = db.get_messages_for_user(current_user.id)
    unread_count = len([msg for msg in messages_data if not msg.get('is_read', False)])
    
    return render_template('student/dashboard.html',
                         toli=toli_data,
                         team_members=team_members,
                         programs=programs,
                         resources=resources,
                         unread_count=unread_count)

@student.route('/student/toli/create', methods=['GET', 'POST'])
@login_required
def create_toli():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Check if student already in a toli
    if current_user.toli_id:
        flash('You are already in a toli!', 'warning')
        return redirect(url_for('student.dashboard'))
    
    form = StudentCreateToliForm()
    
    if form.validate_on_submit():
        # Check if current user is trying to add themselves
        current_scholar_no = current_user.scholar_no
        member_scholar_nos = [form.m2_scholar_no.data, form.m3_scholar_no.data]
        if form.m4_scholar_no.data:
            member_scholar_nos.append(form.m4_scholar_no.data)
        
        if current_scholar_no in member_scholar_nos:
            flash('You cannot add yourself as a member. You are automatically the leader!', 'danger')
            return render_template('student/create_toli.html', form=form)
        
        # Process members data - current user is leader + 2-3 additional members
        members = []
        
        # Add current user as leader (Member 1)
        leader_data = {
            'member_number': 1,
            'scholar_no': current_user.scholar_no,
            'name': current_user.name,
            'course': current_user.course,
            'dob': current_user.dob,
            'contact': current_user.contact,
            'email': current_user.email,
            'passport_photo': current_user.profile_photo,
            'is_leader': True
        }
        members.append(leader_data)
        
        # Member 2 (required)
        if form.m2_scholar_no.data:
            member2_data = db.get_user_by_scholar_no(form.m2_scholar_no.data)
            if not member2_data:
                flash(f'Student with scholar number {form.m2_scholar_no.data} not found!', 'danger')
                return render_template('student/create_toli.html', form=form)
            
            if member2_data.get('toli_id'):
                flash(f'Student {form.m2_scholar_no.data} is already in another toli!', 'danger')
                return render_template('student/create_toli.html', form=form)
            
            member_data = {
                'member_number': 2,
                'scholar_no': form.m2_scholar_no.data,
                'name': form.m2_name.data,
                'course': form.m2_course.data,
                'contact': form.m2_contact.data,
                'email': form.m2_email.data,
                'is_leader': False
            }
            members.append(member_data)
        
        # Member 3 (required)
        if form.m3_scholar_no.data:
            member3_data = db.get_user_by_scholar_no(form.m3_scholar_no.data)
            if not member3_data:
                flash(f'Student with scholar number {form.m3_scholar_no.data} not found!', 'danger')
                return render_template('student/create_toli.html', form=form)
            
            if member3_data.get('toli_id'):
                flash(f'Student {form.m3_scholar_no.data} is already in another toli!', 'danger')
                return render_template('student/create_toli.html', form=form)
            
            member_data = {
                'member_number': 3,
                'scholar_no': form.m3_scholar_no.data,
                'name': form.m3_name.data,
                'course': form.m3_course.data,
                'contact': form.m3_contact.data,
                'email': form.m3_email.data,
                'is_leader': False
            }
            members.append(member_data)
        
        # Member 4 (optional)
        if form.m4_scholar_no.data:
            member4_data = db.get_user_by_scholar_no(form.m4_scholar_no.data)
            if not member4_data:
                flash(f'Student with scholar number {form.m4_scholar_no.data} not found!', 'danger')
                return render_template('student/create_toli.html', form=form)
            
            if member4_data.get('toli_id'):
                flash(f'Student {form.m4_scholar_no.data} is already in another toli!', 'danger')
                return render_template('student/create_toli.html', form=form)
            
            member_data = {
                'member_number': 4,
                'scholar_no': form.m4_scholar_no.data,
                'name': form.m4_name.data,
                'course': form.m4_course.data,
                'contact': form.m4_contact.data,
                'email': form.m4_email.data,
                'is_leader': False
            }
            members.append(member_data)
        
        # Check if we have at least 3 members total (leader + 2)
        if len(members) < 3:
            flash('A toli must have at least 3 members including yourself!', 'danger')
            return render_template('student/create_toli.html', form=form)
        
        # Create toli
        toli_data = {
            'toli_no': form.toli_no.data,
            'name': f"Toli {form.toli_no.data}",
            'session_year': form.session_year.data,
            'members': members,
            'leader_id': current_user.id,  # Set current user as leader
            'status': 'pending',  # Submit for admin approval
            'created_by': current_user.id,
            'created_at': datetime.utcnow(),
            'location': {},
            'coordinator_name': '',
            'coordinator_contact': ''
        }
        
        toli = Toli(toli_data)
        result = db.create_toli(toli.to_dict())
        
        if result:
            # Update all members' toli_id
            for member in members:
                user_data = db.get_user_by_scholar_no(member['scholar_no'])
                if user_data:
                    db.update_user(str(user_data['_id']), {'toli_id': result})
            
            flash(f'Toli {form.toli_no.data} created successfully! Waiting for admin approval.', 'success')
            return redirect(url_for('student.dashboard'))
        else:
            flash('Error creating toli.', 'danger')
    
    return render_template('student/create_toli.html', form=form)


@student.route('/student/create-program', methods=['GET', 'POST'])
@login_required
def create_program():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    form = CreateProgramForm()
    
    if form.validate_on_submit():
        program_data = {
            'title': form.title.data,
            'description': form.description.data,
            'location': form.location.data,
            'start_date': form.start_date.data,
            'end_date': form.end_date.data,
            'objectives': form.objectives.data,
            'methodology': form.methodology.data,
            'expected_outcomes': form.expected_outcomes.data,
            'student_id': current_user.id,
            'toli_id': current_user.toli_id,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        
        program = Program(program_data)
        db.create_program(program.to_dict())
        flash('Program submitted successfully! Waiting for admin approval.', 'success')
        return redirect(url_for('student.dashboard'))
    
    return render_template('student/create_program.html', form=form)

@student.route('/student/resources')
@login_required
def view_resources():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    resources_data = db.get_all_resources()
    resources = [Resource(resource) for resource in resources_data]
    
    return render_template('student/resources.html', resources=resources)

@student.route('/student/messages')
@login_required
def view_messages():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    messages_data = db.get_messages_for_user(current_user.id)
    messages = [Message(message) for message in messages_data]
    
    return render_template('student/messages.html', messages=messages)