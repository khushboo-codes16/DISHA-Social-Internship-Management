from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from app.forms import LoginForm, StudentSignupForm, StudentLoginForm
from app.database import MongoDB
from datetime import datetime
import os
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)
db = MongoDB()

def save_profile_photo(photo):
    if photo:
        filename = secure_filename(photo.filename)
        photo_dir = os.path.join(current_app.root_path, 'static/uploads/profile_photos')
        os.makedirs(photo_dir, exist_ok=True)
        photo_path = os.path.join(photo_dir, filename)
        photo.save(photo_path)
        return f'uploads/profile_photos/{filename}'
    return None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user_data = db.get_user_by_email(form.email.data)
        
        if user_data:
            user = User(user_data)
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                
                # Redirect based on role
                if user.role == 'admin':
                    flash('Admin login successful!', 'success')
                    return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
                else:
                    flash('Login successful!', 'success')
                    return redirect(next_page) if next_page else redirect(url_for('student.dashboard'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('User not found.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/login/student', methods=['GET', 'POST'])
def student_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = StudentLoginForm()
    
    if form.validate_on_submit():
        user_data = db.get_user_by_scholar_no(form.scholar_no.data)
        if user_data:
            user = User(user_data)
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                flash('Student login successful!', 'success')
                return redirect(url_for('student.dashboard'))
            else:
                flash('Invalid scholar number or password.', 'danger')
        else:
            flash('Student account not found.', 'danger')
    
    return render_template('auth/student_login.html', form=form)

@auth.route('/signup/student', methods=['GET', 'POST'])
def student_signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = StudentSignupForm()
    
    if form.validate_on_submit():
        # Check if student already exists
        if db.get_user_by_scholar_no(form.scholar_no.data):
            flash('Student with this scholar number already exists!', 'danger')
        elif db.get_user_by_email(form.email.data):
            flash('Student with this email already exists!', 'danger')
        else:
            # Save profile photo
            profile_photo_path = save_profile_photo(form.profile_photo.data)
            
            student_data = {
                'scholar_no': form.scholar_no.data,
                'name': form.name.data,
                'email': form.email.data,
                'dob': datetime.combine(form.dob.data, datetime.min.time()),
                'course': form.course.data,
                'contact': form.contact.data,
                'profile_photo': profile_photo_path,
                'role': 'student',
                'toli_id': None,
                'created_at': datetime.utcnow()
            }
            
            student = User(student_data)
            student.set_password(form.password.data)
            
            if db.create_user(student.to_dict()):
                flash('Student account created successfully! Please login.', 'success')
                return redirect(url_for('auth.student_login'))
            else:
                flash('Error creating student account.', 'danger')
    
    return render_template('auth/student_signup.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))