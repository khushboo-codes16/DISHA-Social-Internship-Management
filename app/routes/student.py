from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, send_file
from flask_login import login_required, current_user
from app.models import User, Toli, Program, Resource, Message, Newsletter, Report
from app.forms import StudentCreateToliForm, CreateProgramForm
from app.database import MongoDB
from datetime import datetime
import os

student = Blueprint('student', __name__)
db = MongoDB()

@student.route('/student/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Get student's toli
    toli = None
    team_members = []
    if current_user.toli_id:
        toli_data = db.get_toli_by_id(current_user.toli_id)
        if toli_data:
            toli = Toli(toli_data)
            # Get team members from toli members list
            if toli.members:
                for member in toli.members:
                    if isinstance(member, dict):
                        team_members.append({
                            'name': member.get('name', ''),
                            'scholar_no': member.get('scholar_no', ''),
                            'course': member.get('course', ''),
                            'is_leader': member.get('is_leader', False)
                        })
    
    # Get student's programs
    try:
        programs_data = db.get_programs_by_student(current_user.id)
        programs = []
        for program_data in programs_data:
            program = Program(program_data)
            programs.append({
                'id': program.id,
                'title': program.title,
                'program_type': program.program_type,
                'location': program.location,
                'start_date': program.start_date,
                'status': program.status,
                'total_persons': program.total_persons
            })
    except Exception as e:
        print(f"Error loading programs: {e}")
        programs = []
    
    # Get resources
    try:
        resources = db.get_all_resources()
    except Exception as e:
        print(f"Error loading resources: {e}")
        resources = []
    
    # Get unread messages count
    try:
        messages = db.get_messages_for_user(current_user.id)
        unread_count = len([m for m in messages if not m.get('is_read', False)])
    except Exception as e:
        print(f"Error loading messages: {e}")
        unread_count = 0
    
    return render_template('student/dashboard.html',
                         toli=toli,
                         team_members=team_members,
                         programs=programs,
                         resources=resources,
                         unread_count=unread_count,
                         now=datetime.utcnow())

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
    
    if request.method == 'POST':
        session_year = request.form.get('session_year')
        
        if not session_year:
            flash('Session year is required!', 'danger')
            return render_template('student/create_toli.html')
        
        # Process members data - current user is leader
        members = []
        
        # Add current user as leader
        leader_data = {
            'member_number': 1,
            'scholar_no': current_user.scholar_no,
            'name': current_user.name,
            'course': current_user.course,
            'dob': current_user.dob,
            'contact': current_user.contact,
            'email': current_user.email,
            'profile_photo': current_user.profile_photo,
            'is_leader': True
        }
        members.append(leader_data)
        
        # Process additional members from form
        member_count = 0
        i = 1
        while True:
            scholar_no = request.form.get(f'member_{i}_scholar_no')
            if not scholar_no:  # No more members
                break
                
            # Get student data from database
            member_data = db.get_user_by_scholar_no(scholar_no)
            if member_data:
                if member_data.get('toli_id'):
                    flash(f'Student {scholar_no} is already in another toli!', 'danger')
                    return render_template('student/create_toli.html')
                
                member_user = User(member_data)
                member_info = {
                    'member_number': i + 1,
                    'scholar_no': scholar_no,
                    'name': member_user.name,
                    'course': member_user.course,
                    'dob': member_user.dob,
                    'contact': member_user.contact,
                    'email': member_user.email,
                    'profile_photo': member_user.profile_photo,
                    'is_leader': False
                }
                members.append(member_info)
                member_count += 1
            else:
                flash(f'Student with scholar number {scholar_no} not found!', 'danger')
                return render_template('student/create_toli.html')
            
            i += 1
        
        # Create toli WITHOUT toli number (admin will assign later)
        toli_data = {
            'name': f"Toli (Pending Number)",  # Temporary name
            'toli_no': '',  # Empty - will be assigned by admin
            'session_year': session_year,
            'members': members,
            'leader_id': current_user.id,
            'status': 'pending',
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
            
            flash('Toli created successfully! Waiting for admin approval and assignment.', 'success')
            return redirect(url_for('student.dashboard'))
        else:
            flash('Error creating toli.', 'danger')
    
    return render_template('student/create_toli.html')

# API endpoint to get student details by scholar number
@student.route('/api/student/<scholar_no>')
@login_required
def get_student_details(scholar_no):
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    student_data = db.get_user_by_scholar_no(scholar_no)
    if student_data:
        student = User(student_data)
        return jsonify({
            'exists': True,
            'name': student.name,
            'course': student.course,
            'email': student.email,
            'contact': student.contact,
            'in_toli': bool(student.toli_id)
        })
    else:
        return jsonify({'exists': False})

@student.route('/student/create-program', methods=['GET', 'POST'])
@login_required
def create_program():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Check if student is in a toli
    if not current_user.toli_id:
        flash('You need to be in a toli to create programs!', 'warning')
        return redirect(url_for('student.dashboard'))
    
    # Check if toli is active
    toli_data = db.get_toli_by_id(current_user.toli_id)
    if toli_data and toli_data.get('status') != 'active':
        flash('Your toli is not active yet. Please wait for admin approval.', 'warning')
        return redirect(url_for('student.dashboard'))
    
    form = CreateProgramForm()
    
    if form.validate_on_submit():
        # Get additional form data from request
        state = request.form.get('state')
        district = request.form.get('district')
        
        print(f"Form data validated: {form.data}")
        print(f"State: {state}, District: {district}")
        
        # Validate state and district
        if not state or not district:
            flash('Please select both state and district.', 'danger')
            return render_template('student/create_program.html', form=form, toli_data=toli_data)
        
        # Build location string with all details
        full_location = f"{form.location.data}, {district}, {state} - {form.pincode.data}"
        
        program_data = {
            'title': form.title.data,
            'program_type': form.program_type.data,
            'date': form.date.data,
            'location': full_location,
            'state': state,
            'district': district,
            'pincode': form.pincode.data,
            'total_persons': form.total_persons.data,
            'achievements': form.achievements.data,
            'organizer_name': form.organizer_name.data,
            'organizer_contact': form.organizer_contact.data,
            'student_id': current_user.id,
            'toli_id': current_user.toli_id,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        
        print(f"Program data: {program_data}")
        
        try:
            program = Program(program_data)
            print("Program object created successfully")
            
            program_dict = program.to_dict()
            print(f"Program dict: {program_dict}")
            
            result = db.create_program(program_dict)
            print(f"Database result: {result}")
            
            if result:
                # Add start_date for newsletter and report functions
                program_data['start_date'] = program_data['date']
                
                # Auto-generate newsletter
                try:
                    newsletter_id = generate_newsletter(program_data, toli_data, current_user, result)
                    print(f"Newsletter generated: {newsletter_id}")
                except Exception as e:
                    print(f"Newsletter generation failed: {e}")
                
                # Auto-generate report
                try:
                    report_id = generate_program_report(program_data, toli_data, current_user, result)
                    print(f"Report generated: {report_id}")
                except Exception as e:
                    print(f"Report generation failed: {e}")
                
                flash('Program submitted successfully! Newsletter and report have been generated.', 'success')
                return redirect(url_for('student.dashboard'))
            else:
                flash('Error creating program. Database returned False.', 'danger')
                
        except Exception as e:
            print(f"Error creating program: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            flash('An error occurred while creating the program. Please try again.', 'danger')
    
    # Pass toli_data to the template
    return render_template('student/create_program.html', 
                         form=form, 
                         toli_data=toli_data)

def generate_program_report(program_data, toli_data, student, program_id):
    """Generate detailed program report for admin/student access"""
    
    # Get toli information
    toli_name = toli_data.get('name', 'Unknown Toli')
    toli_number = toli_data.get('toli_no', '')
    coordinator_name = toli_data.get('coordinator_name', 'N/A')
    coordinator_contact = toli_data.get('coordinator_contact', 'N/A')
    
    # Format date properly
    program_date = program_data['date']
    if hasattr(program_date, 'strftime'):
        formatted_date = program_date.strftime('%B %d, %Y')
    else:
        formatted_date = str(program_date)
    
    # Create report content
    report_content = f"""
    <div style="font-family: 'Arial', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <!-- DSVV Header -->
        <div style="text-align: center; border-bottom: 3px solid #1E40AF; padding-bottom: 20px; margin-bottom: 30px;">
            <h1 style="color: #1E40AF; margin: 0; font-size: 28px; font-weight: bold;">
                Dev Sanskriti Vishwavidyalaya
            </h1>
            <h2 style="color: #FFD700; margin: 5px 0; font-size: 22px;">
                DISHA - Program Report
            </h2>
            <p style="color: #666; margin: 0; font-style: italic;">
                Official Program Documentation
            </p>
        </div>

        <!-- Program Details -->
        <div style="margin-bottom: 30px;">
            <h3 style="color: #1E40AF; border-bottom: 2px solid #FFD700; padding-bottom: 10px;">
                Program Details
            </h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; width: 30%;">Program Name</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{program_data['title']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Program Type</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{program_data['program_type']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Date</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{formatted_date}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Location</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{program_data['location']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Participants</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{program_data['total_persons']} people</td>
                </tr>
            </table>
        </div>

        <!-- Organizer Details -->
        <div style="margin-bottom: 30px;">
            <h3 style="color: #1E40AF; border-bottom: 2px solid #FFD700; padding-bottom: 10px;">
                Organizer Information
            </h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; width: 30%;">Organizer Name</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{program_data['organizer_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Contact Number</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{program_data['organizer_contact']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Toli Name</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{toli_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Toli Coordinator</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{coordinator_name} ({coordinator_contact})</td>
                </tr>
            </table>
        </div>

        <!-- Achievements -->
        <div style="margin-bottom: 30px;">
            <h3 style="color: #1E40AF; border-bottom: 2px solid #FFD700; padding-bottom: 10px;">
                Program Achievements & Outcomes
            </h3>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px;">
                {program_data['achievements']}
            </div>
        </div>

        <!-- Impact Assessment -->
        <div style="margin-bottom: 30px;">
            <h3 style="color: #1E40AF; border-bottom: 2px solid #FFD700; padding-bottom: 10px;">
                Impact Assessment
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #1E40AF;">{program_data['total_persons']}</div>
                    <div style="color: #666;">People Impacted</div>
                </div>
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #856404;">{program_data['program_type']}</div>
                    <div style="color: #666;">Program Type</div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 2px solid #f0f0f0;">
            <p style="color: #666; margin: 5px 0;">
                <strong>Dev Sanskriti Vishwavidyalaya, Shantikunj, Haridwar</strong>
            </p>
            <p style="color: #999; margin: 5px 0; font-size: 12px;">
                DISHA Program Report | Generated on: {datetime.utcnow().strftime('%B %d, %Y at %H:%M')}
            </p>
            <p style="color: #999; margin: 5px 0; font-size: 10px;">
                Report ID: {program_id} | Confidential - For Internal Use Only
            </p>
        </div>
    </div>
    """
    
    # Create report data
    report_data = {
        'program_id': program_id,
        'title': f"Program Report: {program_data['title']}",
        'content': report_content,
        'program_type': program_data['program_type'],
        'location': program_data['location'],
        'date': program_data['date'],
        'participants_count': program_data['total_persons'],
        'achievements': program_data['achievements'],
        'organizer_name': program_data['organizer_name'],
        'toli_name': toli_name,
        'status': 'completed',
        'created_by': student.id,
        'created_at': datetime.utcnow()
    }
    
    report = Report(report_data)
    return db.create_report(report.to_dict())

def generate_newsletter(program_data, toli_data, student, program_id):
    """Generate newsletter automatically from program data"""
    
    # Get toli information
    toli_name = toli_data.get('name', 'Unknown Toli')
    toli_number = toli_data.get('toli_no', '')
    
    # Format date properly
    program_date = program_data['start_date']
    if hasattr(program_date, 'strftime'):
        formatted_date = program_date.strftime('%B %d, %Y')
    else:
        formatted_date = str(program_date)
    
    # Create newsletter title
    newsletter_title = f"{program_data['program_type']} Program by {toli_name}"
    if toli_number:
        newsletter_title += f" (Toli {toli_number})"
    
    # Create newsletter content with DSVV branding
    newsletter_content = f"""
    <div style="font-family: 'Arial', sans-serif; max-width: 800px; margin: 0 auto; background: linear-gradient(135deg, #FFD700 0%, #1E40AF 100%); padding: 20px; border-radius: 15px;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <!-- DSVV Header -->
            <div style="text-align: center; border-bottom: 3px solid #FFD700; padding-bottom: 20px; margin-bottom: 30px;">
                <h1 style="color: #1E40AF; margin: 0; font-size: 28px; font-weight: bold;">
                    Dev Sanskriti Vishwavidyalaya
                </h1>
                <h2 style="color: #FFD700; margin: 5px 0; font-size: 22px;">
                    DISHA - Social Internship Program
                </h2>
                <p style="color: #666; margin: 0; font-style: italic;">
                    "Where Education Meets Transformation"
                </p>
            </div>

            <!-- Program Highlights -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h3 style="color: #1E40AF; border-left: 4px solid #FFD700; padding-left: 15px; margin-top: 0;">
                    🎉 Program Successfully Conducted!
                </h3>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                    <div>
                        <strong>📅 Date:</strong> {formatted_date}
                    </div>
                    <div>
                        <strong>📍 Location:</strong> {program_data['location']}
                    </div>
                    <div>
                        <strong>👥 Participants:</strong> {program_data['total_persons']} people
                    </div>
                    <div>
                        <strong>🎯 Program Type:</strong> {program_data['program_type']}
                    </div>
                </div>
            </div>

            <!-- Achievements -->
            {f'''
            <div style="margin-bottom: 25px;">
                <h4 style="color: #1E40AF; margin-bottom: 10px;">⭐ Key Achievements</h4>
                <p style="line-height: 1.6; color: #333; background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                    {program_data['achievements']}
                </p>
            </div>
            ''' if program_data.get('achievements') else ''}

            <!-- Toli Information -->
            <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-bottom: 25px;">
                <h4 style="color: #1E40AF; margin-bottom: 10px; text-align: center;">👥 Organized By</h4>
                <div style="text-align: center;">
                    <strong>{toli_name}</strong>
                    {f"<br><small>Toli Number: {toli_number}</small>" if toli_number else ""}
                    <br><small>Coordinator: {program_data.get('organizer_name', 'N/A')}</small>
                </div>
            </div>

            <!-- Spiritual Message -->
            <div style="text-align: center; background: linear-gradient(135deg, #1E40AF 0%, #FFD700 100%); color: white; padding: 20px; border-radius: 8px; margin-top: 25px;">
                <h4 style="margin: 0; font-size: 18px;">🌿 Spiritual Wisdom</h4>
                <p style="margin: 10px 0 0 0; font-style: italic;">
                    "Service to humanity is service to divinity. Through DISHA, we transform lives while transforming ourselves."
                </p>
            </div>

            <!-- Footer -->
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #f0f0f0;">
                <p style="color: #666; margin: 5px 0;">
                    Dev Sanskriti Vishwavidyalaya, Shantikunj, Haridwar
                </p>
                <p style="color: #999; margin: 5px 0; font-size: 12px;">
                    DISHA - Developmental Initiatives for Societal Harmony and Awareness
                </p>
            </div>
        </div>
    </div>
    """
    
    # Create newsletter data
    newsletter_data = {
        'program_id': program_id,
        'title': newsletter_title,
        'content': newsletter_content,
        'program_type': program_data['program_type'],
        'location': program_data['location'],
        'date': program_data['start_date'],
        'participants_count': program_data['total_persons'],
        'achievements': program_data.get('achievements', ''),
        'organizer_name': program_data.get('organizer_name', ''),
        'images': [],
        'toli_name': toli_name,
        'status': 'published',
        'created_by': student.id,
        'created_at': datetime.utcnow()
    }
    
    newsletter = Newsletter(newsletter_data)
    return db.create_newsletter(newsletter.to_dict())

@student.route('/student/reports')
@login_required
def view_reports():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    reports_data = db.get_reports_by_student(current_user.id)
    reports = [Report(report) for report in reports_data]
    
    return render_template('student/reports.html', reports=reports)

@student.route('/student/report/<report_id>/download')
@login_required
def download_report(report_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    report_data = db.get_report_by_id(report_id)
    if not report_data:
        flash('Report not found.', 'danger')
        return redirect(url_for('student.view_reports'))
    
    report = Report(report_data)
    
    return render_template('student/report_download.html', report=report)

@student.route('/student/report/<report_id>/pdf')
@login_required
def download_report_pdf(report_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    report_data = db.get_report_by_id(report_id)
    if not report_data:
        flash('Report not found.', 'danger')
        return redirect(url_for('student.view_reports'))
    
    report = Report(report_data)
    
    flash('PDF download feature coming soon!', 'info')
    return redirect(url_for('student.view_reports'))

@student.route('/student/resources')
@login_required
def view_resources():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    resources_data = db.get_all_resources()
    resources = [Resource(resource) for resource in resources_data]
    
    # Sort resources by creation date (newest first)
    resources.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('student/resources.html', resources=resources)

@student.route('/student/resource/<resource_id>/download')
@login_required
def download_resource(resource_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    resource_data = db.get_resource_by_id(resource_id)
    if not resource_data:
        flash('Resource not found.', 'danger')
        return redirect(url_for('student.view_resources'))
    
    resource = Resource(resource_data)
    
    if resource.file_path:
        # Ensure the file path is safe
        safe_path = os.path.normpath(resource.file_path)
        resources_dir = os.path.join(current_app.root_path, 'static', 'resources')
        file_path = os.path.join(resources_dir, safe_path)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=resource.file_name or f"{resource.title}.{safe_path.split('.')[-1]}"
            )
        else:
            flash('File not found on server.', 'warning')
            return redirect(url_for('student.view_resources'))
    else:
        flash('No file available for download.', 'warning')
        return redirect(url_for('student.view_resources'))

@student.route('/student/messages')
@login_required
def view_messages():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    messages_data = db.get_messages_for_user(current_user.id)
    messages = [Message(message) for message in messages_data]
    
    # Mark messages as read when viewing
    for message_data in messages_data:
        if not message_data.get('is_read', False):
            db.update_message(str(message_data['_id']), {'is_read': True})
    
    return render_template('student/messages.html', messages=messages)

@student.route('/student/profile')
@login_required
def view_profile():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Get toli information if student is in a toli
    toli = None
    if current_user.toli_id:
        toli_data = db.get_toli_by_id(current_user.toli_id)
        if toli_data:
            toli = Toli(toli_data)
    
    return render_template('student/profile.html', toli=toli)

@student.route('/student/programs')
@login_required
def view_programs():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    programs_data = db.get_programs_by_student(current_user.id)
    programs = []
    
    for program_data in programs_data:
        program = Program(program_data)
        programs.append({
            'id': program.id,
            'title': program.title,
            'program_type': program.program_type,
            'location': program.location,
            'start_date': program.start_date,
            'total_persons': program.total_persons,
            'status': program.status,
            'created_at': program.created_at
        })
    
    return render_template('student/programs.html', programs=programs)

@student.route('/student/program/<program_id>/report')
@login_required
def view_program_report(program_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    program_data = db.get_program_by_id(program_id)
    if not program_data:
        flash('Program not found.', 'danger')
        return redirect(url_for('student.view_programs'))
    
    # Check if student owns this program
    if program_data.get('student_id') != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('student.view_programs'))
    
    program = Program(program_data)
    
    # Get report data
    report_data = db.get_report_by_program(program_id)
    if not report_data:
        # Generate report if not exists
        toli_data = db.get_toli_by_id(current_user.toli_id) if current_user.toli_id else {}
        report_data = generate_program_report({
            'title': program.title,
            'program_type': program.program_type,
            'location': program.location,
            'date': program.start_date,
            'total_persons': program.total_persons,
            'achievements': program_data.get('achievements', ''),
            'organizer_name': program_data.get('organizer_name', ''),
            'organizer_contact': program_data.get('organizer_contact', '')
        }, toli_data, current_user, program_id)
        report_data = db.get_report_by_program(program_id)  # Get the generated report
    
    report = Report(report_data) if report_data else None
    
    return render_template('student/program_report.html', program=program, report=report)

@student.route('/student/program/<program_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_program(program_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    program_data = db.get_program_by_id(program_id)
    if not program_data:
        flash('Program not found.', 'danger')
        return redirect(url_for('student.view_programs'))
    
    # Check if student owns this program
    if program_data.get('student_id') != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('student.view_programs'))
    
    program = Program(program_data)
    form = CreateProgramForm(obj=program)
    
    if form.validate_on_submit():
        # Update program data
        update_data = {
            'title': form.title.data,
            'program_type': form.program_type.data,
            'date': form.date.data,
            'location': form.location.data,
            'pincode': form.pincode.data,
            'total_persons': form.total_persons.data,
            'achievements': form.achievements.data,
            'organizer_name': form.organizer_name.data,
            'organizer_contact': form.organizer_contact.data,
            'updated_at': datetime.utcnow()
        }
        
        if db.update_program(program_id, update_data):
            flash('Program updated successfully!', 'success')
            return redirect(url_for('student.view_programs'))
        else:
            flash('Error updating program.', 'danger')
    
    return render_template('student/edit_program.html', form=form, program=program)

@student.route('/student/program/<program_id>/delete', methods=['POST'])
@login_required
def delete_program(program_id):
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    program_data = db.get_program_by_id(program_id)
    if not program_data:
        return jsonify({'error': 'Program not found'}), 404
    
    # Check if student owns this program
    if program_data.get('student_id') != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    if db.delete_program(program_id):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to delete program'}), 500

@student.route('/student/rules-regulations')
@login_required
def rules_regulations():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    return render_template('student/rules_regulations.html')

@student.route('/student/toli-details')
@login_required
def toli_details():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    if not current_user.toli_id:
        flash('You are not in any toli!', 'warning')
        return redirect(url_for('student.dashboard'))
    
    toli_data = db.get_toli_by_id(current_user.toli_id)
    if not toli_data:
        flash('Toli not found!', 'danger')
        return redirect(url_for('student.dashboard'))
    
    toli = Toli(toli_data)
    
    # Get detailed member information
    detailed_members = []
    if toli.members:
        for member in toli.members:
            if isinstance(member, dict):
                detailed_members.append({
                    'name': member.get('name', ''),
                    'scholar_no': member.get('scholar_no', ''),
                    'course': member.get('course', ''),
                    'email': member.get('email', ''),
                    'is_leader': member.get('is_leader', False)
                })
    
    # Get toli programs
    programs_data = db.get_programs_by_toli(current_user.toli_id)
    programs = [Program(program) for program in programs_data]
    
    return render_template('student/toli_details.html', 
                         toli=toli, 
                         members=detailed_members,
                         programs=programs)

# API endpoint to mark message as read
@student.route('/api/message/<message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    result = db.update_message(message_id, {'is_read': True})
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to mark message as read'}), 400

# API endpoint to get dashboard statistics
@student.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    stats = {
        'programs_count': len(db.get_programs_by_student(current_user.id)),
        'resources_count': len(db.get_all_resources()),
        'unread_messages': len([m for m in db.get_messages_for_user(current_user.id) if not m.get('is_read', False)]),
        'toli_status': 'none'
    }
    
    if current_user.toli_id:
        toli_data = db.get_toli_by_id(current_user.toli_id)
        if toli_data:
            stats['toli_status'] = toli_data.get('status', 'pending')
    
    return jsonify(stats)