
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, FileField, SubmitField, IntegerField, FieldList, FormField, BooleanField, PasswordField, SelectMultipleField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError, EqualTo
from flask_wtf.file import FileAllowed
import re

class StudentSignupForm(FlaskForm):
    scholar_no = StringField('Scholar Number', validators=[DataRequired(), Length(min=3, max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    course = SelectField('Course', choices=[
        ('', 'Select Your Course'),
        ('mca_ds', 'MCA Data Science'),
        ('mca', 'MCA'),
        ('bca', 'BCA'),
        ('bsc_cs', 'BSc Computer Science'),
        ('bsc_it', 'BSc IT'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    contact = TelField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_photo = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    agree_terms = BooleanField('I agree to the terms and conditions', validators=[DataRequired()])
    submit = SubmitField('Create My Account')

    def validate_contact(self, field):
        if not re.match(r'^[6-9]\d{9}$', field.data):
            raise ValidationError('Please enter a valid Indian mobile number')

class StudentLoginForm(FlaskForm):
    scholar_no = StringField('Scholar Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In to Dashboard')


class MemberForm(FlaskForm):
    scholar_no = StringField('Scholar Number', validators=[DataRequired()])
    name = StringField('Student Name', validators=[DataRequired()])
    course = StringField('Course', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    passport_photo = FileField('Passport Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

# Create separate forms for each member instead of using FormField
# Student Forms
class StudentCreateToliForm(FlaskForm):
    toli_no = StringField('Toli Number', validators=[DataRequired()])
    session_year = StringField('Session Year', validators=[DataRequired()])
    
    # Member 2 (required)
    m2_scholar_no = StringField('Scholar Number', validators=[DataRequired()])
    m2_name = StringField('Student Name', validators=[DataRequired()])
    m2_course = StringField('Course', validators=[DataRequired()])
    m2_contact = StringField('Contact Number', validators=[DataRequired()])
    m2_email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Member 3 (required)
    m3_scholar_no = StringField('Scholar Number', validators=[DataRequired()])
    m3_name = StringField('Student Name', validators=[DataRequired()])
    m3_course = StringField('Course', validators=[DataRequired()])
    m3_contact = StringField('Contact Number', validators=[DataRequired()])
    m3_email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Member 4 (optional)
    m4_scholar_no = StringField('Scholar Number', validators=[Optional()])
    m4_name = StringField('Student Name', validators=[Optional()])
    m4_course = StringField('Course', validators=[Optional()])
    m4_contact = StringField('Contact Number', validators=[Optional()])
    m4_email = StringField('Email', validators=[Optional(), Email()])
    
    submit = SubmitField('Create Toli')

# Admin Forms
class AdminManageToliForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    coordinator_name = StringField('Coordinator Name', validators=[DataRequired()])
    coordinator_contact = StringField('Coordinator Contact', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    update = SubmitField('Update Toli')

class FinalizeToliForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    coordinator_name = StringField('Coordinator Name', validators=[DataRequired()])
    coordinator_contact = StringField('Coordinator Contact', validators=[DataRequired()])
    finalize = SubmitField('Finalize Toli Location')

class AddStudentForm(FlaskForm):
    scholar_no = StringField('Scholar Number', validators=[DataRequired()])
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    course = StringField('Course', validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[Optional()])
    toli_id = SelectField('Assign to Toli', validators=[Optional()], choices=[])
    submit = SubmitField('Add Student')

class UploadResourceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    resource_type = SelectField('Resource Type', 
                               choices=[('book', 'Book'), ('video', 'Video'), ('document', 'Document'), ('other', 'Other')],
                               validators=[DataRequired()])
    file = FileField('Upload File', validators=[DataRequired()])
    submit = SubmitField('Upload Resource')

class SendMessageForm(FlaskForm):
    title = StringField('Message Title', validators=[DataRequired()])
    content = TextAreaField('Message Content', validators=[DataRequired()])
    receiver_id = SelectField('Send To', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class CreateProgramForm(FlaskForm):
    title = StringField('Program Title', validators=[DataRequired()])
    description = TextAreaField('Program Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    objectives = TextAreaField('Objectives', validators=[DataRequired()])
    methodology = TextAreaField('Methodology', validators=[DataRequired()])
    expected_outcomes = TextAreaField('Expected Outcomes', validators=[DataRequired()])
    submit = SubmitField('Submit Program')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AddMembersToToliForm(FlaskForm):
    student_ids = SelectMultipleField('Select Students', validators=[DataRequired()])
    submit = SubmitField('Add Members to Toli')