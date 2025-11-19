from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, FileField, SubmitField, IntegerField, BooleanField, PasswordField, TelField
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

class StudentCreateToliForm(FlaskForm):
    session_year = StringField('Session Year', validators=[DataRequired()])
    submit = SubmitField('Create Toli')

class AssignLocationForm(FlaskForm):
    toli_no = StringField('Toli Number', validators=[DataRequired()])
    location = SelectField('Location', validators=[DataRequired()])
    coordinator_name = StringField('Coordinator Name', validators=[DataRequired()])
    coordinator_contact = TelField('Coordinator Contact', validators=[DataRequired(), Length(min=10, max=15)])
    assign = SubmitField('Assign Location & Activate')

    def validate_coordinator_contact(self, field):
        if not re.match(r'^[6-9]\d{9}$', field.data):
            raise ValidationError('Please enter a valid Indian mobile number')

class AdminManageToliForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    update = SubmitField('Update Status')

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
                               choices=[
                                   ('', 'Select Resource Type'),
                                   ('book', '📚 Book'),
                                   ('video', '🎥 Video'), 
                                   ('audio', '🎵 Audio'),
                                   ('document', '📄 Document'),
                                   ('link', '🔗 Link'),
                                   ('other', '📦 Other')
                               ],
                               validators=[DataRequired()])
    file = FileField('Upload File', validators=[Optional()])
    external_link = StringField('External Link', validators=[Optional()])
    submit = SubmitField('Upload Resource')

    def validate(self, extra_validators=None):
        if not super().validate():
            return False
        
        if not self.file.data and not self.external_link.data:
            self.file.errors.append('Either file or external link must be provided.')
            return False
        
        if self.file.data and self.external_link.data:
            self.file.errors.append('Please provide either file or link, not both.')
            return False
            
        return True

class SendMessageForm(FlaskForm):
    title = StringField('Message Title', validators=[DataRequired()])
    content = TextAreaField('Message Content', validators=[DataRequired()])
    receiver_id = SelectField('Send To', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class CreateProgramForm(FlaskForm):
    title = StringField('Program Name', validators=[DataRequired()])
    program_type = SelectField('Program Type', 
                              choices=[
                                  ('', 'Select Program Type'),
                                  ('Yagya', 'Yagya'),
                                  ('Deep Yagya', 'Deep Yagya'),
                                  ('Yoga', 'Yoga'),
                                  ('Sanskar', 'Sanskar'),
                                  ('Therapy', 'Therapy'),
                                  ('Lectures', 'Lectures'),
                                  ('Tree Plantation', 'Tree Plantation'),
                                  ('Health Camp', 'Health Camp'),
                                  ('Educational', 'Educational'),
                                  ('Cultural', 'Cultural'),
                                  ('Other', 'Other - Please specify below')
                              ],
                              validators=[DataRequired()])
    other_program_type = StringField('Specify Other Program Type', validators=[Optional()])
    date = DateField('Program Date', validators=[DataRequired()])
    location = StringField('Location Details', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=50)])
    city = StringField('City/District', validators=[DataRequired(), Length(min=2, max=50)])
    pincode = StringField('Pincode', validators=[DataRequired(), Length(min=6, max=6)])
    total_persons = IntegerField('Number of Attendees', validators=[DataRequired()])
    achievements = TextAreaField('Program Achievements', validators=[Optional()])
    achievements_file = FileField('Upload Achievements/Certificate', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf'], 'Images and PDF only!')
    ])
    organizer_name = StringField('Organizer Name', validators=[DataRequired()])
    organizer_contact = TelField('Organizer Contact No', validators=[DataRequired(), Length(min=10, max=15)])
    program_images = FileField('Program Photos (Max 4 images, 2MB each)', validators=[
        DataRequired(message='Please upload at least one program photo'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ], render_kw={"multiple": True})
    submit = SubmitField('Submit Program')

    def validate_organizer_contact(self, field):
        if not re.match(r'^[6-9]\d{9}$', field.data):
            raise ValidationError('Please enter a valid Indian mobile number')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Add these new forms for profile management
class UpdateProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    scholar_no = StringField('Scholar Number', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    contact = TelField('Contact Number', validators=[Optional(), Length(min=10, max=15)])
    course = SelectField('Course', choices=[
        ('', 'Select Your Course'),
        ('mca_ds', 'MCA Data Science'),
        ('mca', 'MCA'),
        ('bca', 'BCA'),
        ('bsc_cs', 'BSc Computer Science'),
        ('bsc_it', 'BSc IT'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    profile_photo = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')

    def validate_contact(self, field):
        if field.data and not re.match(r'^[6-9]\d{9}$', field.data):
            raise ValidationError('Please enter a valid Indian mobile number')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
    
# Add this to your existing forms in forms.py

class AssignLocationForm(FlaskForm):
    toli_no = StringField('Toli Number', validators=[DataRequired()])
    location = SelectField('Location', validators=[DataRequired()])
    coordinator_name = StringField('Coordinator Name', validators=[DataRequired()])
    coordinator_contact = TelField('Coordinator Contact', validators=[DataRequired(), Length(min=10, max=15)])
    assign = SubmitField('Assign Location & Activate')

    def validate_coordinator_contact(self, field):
        if not re.match(r'^[6-9]\d{9}$', field.data):
            raise ValidationError('Please enter a valid Indian mobile number')
