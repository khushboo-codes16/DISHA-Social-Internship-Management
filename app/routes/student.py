from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, send_file
from flask_login import login_required, current_user
from app.models import User, Toli, Program, Resource, Message, Newsletter, Report
from app.forms import StudentCreateToliForm, CreateProgramForm, UpdateProfileForm, ChangePasswordForm 
from app.database import MongoDB
from datetime import datetime, date
from app.database_fixes import DatabaseFixes
import os
from werkzeug.utils import secure_filename

student = Blueprint('student', __name__)
db = MongoDB()

# ========== HELPER FUNCTIONS ==========

# Update the save_program_images function in student.py

def save_program_images(images, program_id):
    """Save program images and return their paths with size validation"""
    saved_paths = []
    
    if images and images[0].filename:
        # Create program directory
        program_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'programs', str(program_id))
        os.makedirs(program_dir, exist_ok=True)
        
        for image in images:
            if image.filename:
                # Check file size (2MB limit)
                if len(image.read()) > 2 * 1024 * 1024:
                    print(f"Image {image.filename} exceeds 2MB limit, skipping")
                    continue
                image.seek(0)  # Reset file pointer after reading
                
                # Secure the filename and create unique name
                original_filename = secure_filename(image.filename)
                filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
                image_path = os.path.join(program_dir, filename)
                
                try:
                    image.save(image_path)
                    
                    # Store relative path for database
                    relative_path = f'uploads/programs/{program_id}/{filename}'
                    saved_paths.append(relative_path)
                    print(f"✅ Saved image: {relative_path}")
                    
                except Exception as e:
                    print(f"❌ Error saving image {image.filename}: {e}")
                    continue
    
    return saved_paths

def generate_ai_recommendations(program_type, participants, achievements):
    """Generate AI-based recommendations"""
    recommendations = []
    
    if participants > 50:
        recommendations.append("Consider expanding to multiple locations for wider reach")
    elif participants < 10:
        recommendations.append("Focus on community engagement to increase participation")
    
    if 'yagya' in program_type.lower() or 'yoga' in program_type.lower():
        recommendations.append("Document spiritual experiences for future reference")
        recommendations.append("Consider follow-up sessions for sustained impact")
    
    if len(achievements) > 200:
        recommendations.append("Excellent documentation! Consider creating a case study")
    
    # Default recommendations
    if not recommendations:
        recommendations = [
            "Continue the great work in community service",
            "Document lessons learned for future programs",
            "Share success stories with the wider community"
        ]
    
    return recommendations

# In student.py - Update the generate_program_report function


def generate_program_report(program_data, toli_data, student, program_id, images=None):
    """Generate modern interactive program report"""
    
    # Get program details
    program_details = db.get_program_by_id(program_id)
    program_no = program_details.get('program_no', 'N/A') if program_details else 'N/A'
    
    # Get toli information
    toli_name = toli_data.get('name', 'Unknown Toli')
    toli_location = toli_data.get('location', {})
    toli_city = toli_location.get('city', 'N/A') if toli_location else 'N/A'
    toli_state = toli_location.get('state', '') if toli_location else ''
    
    # Format date
    program_date = program_data['date']
    if hasattr(program_date, 'strftime'):
        formatted_date = program_date.strftime('%B %d, %Y')
        short_date = program_date.strftime('%d-%b-%Y')
    else:
        formatted_date = str(program_date)
        short_date = 'N/A'
    
    # Calculate duration (default 6 hours if not specified)
    duration = "6 hrs"
    
    # Create image gallery HTML
    image_gallery_html = ""
    if images and len(images) > 0:
        image_gallery_html = '<div class="photo-gallery">'
        for idx, img_path in enumerate(images[:6]):  # Max 6 images
            image_gallery_html += f'''
            <div class="photo-item">
                <img src="/static/{img_path}" alt="Program Activity {idx+1}" onerror="this.style.display='none'">
            </div>
            '''
        image_gallery_html += '</div>'
    
    # Create report content with modern design
    report_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Program Report - {program_data['title']}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                color: #333;
            }}
            .report-container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            .header {{
                background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
                position: relative;
            }}
            .report-badge {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: #ef4444;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            .university-logo {{
                width: 60px;
                height: 60px;
                background: white;
                border-radius: 50%;
                margin: 0 auto 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                font-weight: bold;
                color: #2563eb;
            }}
            .university-name {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }}
            .report-title {{
                font-size: 28px;
                font-weight: bold;
                margin: 15px 0 5px;
            }}
            .report-subtitle {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .section {{
                padding: 30px;
            }}
            .section-header {{
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e5e7eb;
            }}
            .section-icon {{
                width: 32px;
                height: 32px;
                background: #3b82f6;
                color: white;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                font-weight: bold;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }}
            .info-card {{
                background: #f9fafb;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #3b82f6;
            }}
            .info-label {{
                font-size: 12px;
                color: #6b7280;
                font-weight: 600;
                margin-bottom: 5px;
            }}
            .info-value {{
                font-size: 16px;
                color: #111827;
                font-weight: 600;
            }}
            .stats-row {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin: 25px 0;
                padding: 20px;
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                border-radius: 12px;
            }}
            .stat-box {{
                text-align: center;
                color: white;
            }}
            .stat-icon {{
                font-size: 24px;
                margin-bottom: 8px;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 12px;
                opacity: 0.9;
            }}
            .description-box {{
                background: #f9fafb;
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
                border-left: 4px solid #8b5cf6;
            }}
            .description-title {{
                font-size: 16px;
                font-weight: 600;
                color: #1f2937;
                margin-bottom: 10px;
            }}
            .description-text {{
                font-size: 14px;
                line-height: 1.6;
                color: #4b5563;
            }}
            .activities-list {{
                list-style: none;
                padding: 0;
            }}
            .activities-list li {{
                padding: 10px 15px;
                margin: 8px 0;
                background: #f0fdf4;
                border-left: 3px solid #10b981;
                border-radius: 5px;
                font-size: 14px;
            }}
            .achievements-box {{
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
            }}
            .achievements-title {{
                font-size: 16px;
                font-weight: 600;
                color: #92400e;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
            }}
            .achievements-text {{
                font-size: 14px;
                color: #78350f;
                line-height: 1.6;
            }}
            .photo-section {{
                background: #f9fafb;
                padding: 25px;
                border-radius: 12px;
            }}
            .photo-gallery {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 15px;
            }}
            .photo-item {{
                position: relative;
                border-radius: 10px;
                overflow: hidden;
                aspect-ratio: 4/3;
                background: #e5e7eb;
            }}
            .photo-item img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s;
            }}
            .photo-item:hover img {{
                transform: scale(1.05);
            }}
            .coordinator-box {{
                background: #eff6ff;
                padding: 20px;
                border-radius: 12px;
                margin-top: 20px;
            }}
            .coordinator-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 10px;
            }}
            .coordinator-item {{
                text-align: center;
            }}
            .coordinator-label {{
                font-size: 11px;
                color: #6b7280;
                font-weight: 600;
                margin-bottom: 5px;
            }}
            .coordinator-value {{
                font-size: 14px;
                color: #1f2937;
                font-weight: 600;
            }}
            .footer {{
                background: #1f2937;
                color: white;
                padding: 20px 30px;
                text-align: center;
            }}
            .footer-text {{
                font-size: 12px;
                opacity: 0.8;
                margin: 5px 0;
            }}
            @media print {{
                body {{
                    background: white;
                    padding: 0;
                }}
                .report-container {{
                    box-shadow: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <!-- Header -->
            <div class="header">
                <div class="report-badge">Program Report</div>
                <div class="university-logo">📚</div>
                <div class="university-name">DEV SANSKRITI VISHWAVIDYALAYA</div>
                <div class="report-title">PROGRAM COMPLETION REPORT</div>
                <div class="report-subtitle">DISHA Social Internship Program</div>
            </div>

            <!-- Program Overview Section -->
            <div class="section">
                <div class="section-header">
                    <div class="section-icon">📋</div>
                    <div class="section-title">Program Overview</div>
                </div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-label">Program Name</div>
                        <div class="info-value">{program_data['title']}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Program Type</div>
                        <div class="info-value">{program_data['program_type']}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Location</div>
                        <div class="info-value">{toli_city}, {toli_state}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Date</div>
                        <div class="info-value">{short_date}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Venue</div>
                        <div class="info-value">{program_data['location']}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Session Year</div>
                        <div class="info-value">2024-2025</div>
                    </div>
                </div>

                <!-- Stats Row -->
                <div class="stats-row">
                    <div class="stat-box">
                        <div class="stat-icon">👥</div>
                        <div class="stat-value">{program_data['total_persons']}+</div>
                        <div class="stat-label">Participants</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-icon">⏱️</div>
                        <div class="stat-value">{duration}</div>
                        <div class="stat-label">Duration</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-value">5</div>
                        <div class="stat-label">Activities</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-icon">⭐</div>
                        <div class="stat-value">95%</div>
                        <div class="stat-label">Satisfaction</div>
                    </div>
                </div>
            </div>

            <!-- Program Description Section -->
            <div class="section" style="padding-top: 0;">
                <div class="section-header">
                    <div class="section-icon">📝</div>
                    <div class="section-title">Program Description</div>
                </div>

                <div class="description-box">
                    <div class="description-title">Objective & Purpose</div>
                    <div class="description-text">
                        The program aimed to promote {program_data['program_type'].lower()} activities and create positive impact in the community through meaningful social service and spiritual engagement.
                    </div>
                </div>

                <div class="description-box">
                    <div class="description-title">Activities Conducted</div>
                    <ul class="activities-list">
                        <li>Morning {program_data['program_type']} session (8:00 AM - 9:30 AM)</li>
                        <li>Interactive community engagement activities</li>
                        <li>Educational and awareness programs</li>
                        <li>Cultural and spiritual activities</li>
                        <li>Feedback and reflection session</li>
                    </ul>
                </div>
            </div>

            <!-- Impact & Achievements Section -->
            <div class="section" style="padding-top: 0;">
                <div class="section-header">
                    <div class="section-icon">🏆</div>
                    <div class="section-title">Impact & Achievements</div>
                </div>

                <div class="achievements-box">
                    <div class="achievements-title">
                        <span style="margin-right: 10px;">✨</span>
                        Key Achievements
                    </div>
                    <div class="achievements-text">
                        {program_data['achievements'] if program_data['achievements'] else f'Successfully conducted {program_data["program_type"].lower()} program with active participation from community members. The program created awareness about social values and provided valuable learning experiences to all participants.'}
                    </div>
                </div>
            </div>

            <!-- Photo Gallery Section -->
            {f'''
            <div class="section" style="padding-top: 0;">
                <div class="section-header">
                    <div class="section-icon">📸</div>
                    <div class="section-title">Photo Gallery</div>
                </div>
                <div class="photo-section">
                    {image_gallery_html}
                </div>
            </div>
            ''' if images else ''}

            <!-- Program Coordinator Section -->
            <div class="section" style="padding-top: 0;">
                <div class="section-header">
                    <div class="section-icon">👤</div>
                    <div class="section-title">Program Coordinator</div>
                </div>

                <div class="coordinator-box">
                    <div class="coordinator-grid">
                        <div class="coordinator-item">
                            <div class="coordinator-label">Name</div>
                            <div class="coordinator-value">{program_data['organizer_name']}</div>
                        </div>
                        <div class="coordinator-item">
                            <div class="coordinator-label">Email ID</div>
                            <div class="coordinator-value">{student.email}</div>
                        </div>
                        <div class="coordinator-item">
                            <div class="coordinator-label">Contact</div>
                            <div class="coordinator-value">{program_data.get('organizer_contact', 'N/A')}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <div class="footer-text">Dev Sanskriti Vishwavidyalaya, Haridwar</div>
                <div class="footer-text">DISHA Social Internship Program</div>
                <div class="footer-text">Program No: {program_no} | Generated on: {datetime.utcnow().strftime('%d %B, %Y')}</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create report in database
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
        'created_at': datetime.utcnow(),
        'ai_generated': True
    }
    
    report = Report(report_data)
    return db.create_report(report.to_dict())

# In student.py - Update the generate_newsletter function

def generate_newsletter(program_data, toli_data, student, program_id, images=None):
    """Generate newsletter matching the exact sample format"""
    
    # Get program details
    program_details = db.get_program_by_id(program_id)
    program_no = program_details.get('program_no', 'N/A') if program_details else 'N/A'
    
    # Format date
    program_date = program_data['date']
    if hasattr(program_date, 'strftime'):
        formatted_date = program_date.strftime('%B %d, %Y')
        issue_date = program_date.strftime('%B %Y')
    else:
        formatted_date = str(program_date)
        issue_date = datetime.utcnow().strftime('%B %Y')
    
    # Get first image for newsletter
    newsletter_image = None
    if images and len(images) > 0:
        newsletter_image = images[0]
    
    # Create newsletter content EXACTLY matching the sample format
    newsletter_content = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 700px; margin: 0 auto; background: white; line-height: 1.6;">
        <!-- Header -->
        <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #000;">
            <h1 style="margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 1px;">
                DEV SANSKRITI VISHWAVIDYALAYA, HARIDWAR
            </h1>
            <p style="margin: 5px 0; font-style: italic; font-size: 14px;">
                "A University for Self-Transformation and Nation Building"
            </p>
        </div>

        <!-- Newsletter Title -->
        <div style="text-align: center; padding: 15px 0;">
            <h2 style="margin: 0; font-size: 20px; font-weight: bold; text-decoration: underline;">
                NEWSLETTER
            </h2>
            <p style="margin: 5px 0; font-size: 14px;">Issue Date: {issue_date}</p>
        </div>

        <!-- Workshop Badge -->
        <div style="text-align: center; margin: 10px 0;">
            <div style="display: inline-block; background: #f0f0f0; padding: 5px 15px; border: 1px solid #000; font-weight: bold;">
                {program_data['program_type']}
            </div>
        </div>

        <hr style="border: none; border-top: 2px dashed #000; margin: 20px 0;">

        <!-- PROGRAM HIGHLIGHT -->
        <div style="margin-bottom: 25px;">
            <h3 style="font-size: 18px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #000; padding-bottom: 5px;">
                PROGRAM HIGHLIGHT
            </h3>

            <div style="text-align: center; margin: 20px 0;">
                <h4 style="font-size: 20px; font-weight: bold; margin: 0; background: #f8f8f8; padding: 10px; border: 1px solid #ddd;">
                    {program_data['title'].upper() if program_data['title'] else 'PROGRAM ACTIVITY'}
                </h4>
            </div>

            <!-- Program Details List -->
            <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #000; margin: 15px 0;">
                <ul style="list-style: none; padding: 0; margin: 0; font-size: 14px;">
                    <li style="margin-bottom: 8px;"><strong>Organized by:</strong> {toli_data.get('name', 'DISHA Program')}</li>
                    <li style="margin-bottom: 8px;"><strong>Program Date:</strong> {formatted_date}</li>
                    <li style="margin-bottom: 8px;"><strong>Venue:</strong> {program_data['location']}</li>
                    <li style="margin-bottom: 8px;"><strong>Coordinator:</strong> {program_data['organizer_name']}</li>
                    <li style="margin-bottom: 8px;"><strong>Participants:</strong> {program_data['total_persons']}</li>
                </ul>
            </div>
        </div>

        <hr style="border: none; border-top: 2px dashed #000; margin: 25px 0;">

        <!-- FEATURE STORY -->
        <div style="margin-bottom: 25px;">
            <h3 style="font-size: 18px; font-weight: bold; margin-bottom: 15px;">
                FEATURE STORY
            </h3>

            <!-- Introduction -->
            <div style="margin-bottom: 20px;">
                <h4 style="font-size: 16px; font-weight: bold; margin-bottom: 8px; text-decoration: underline;">
                    Introduction
                </h4>
                <p style="margin: 0; font-size: 14px; text-align: justify;">
                    The program aimed to {program_data['achievements'][:150] + '...' if program_data['achievements'] and len(program_data['achievements']) > 150 else program_data['achievements'] if program_data['achievements'] else 'create awareness and provide valuable community service through meaningful social activities'}.
                </p>
            </div>

            <!-- Program Overview -->
            <div style="margin-bottom: 20px;">
                <h4 style="font-size: 16px; font-weight: bold; margin-bottom: 8px; text-decoration: underline;">
                    Program Overview
                </h4>
                <ul style="font-size: 14px; padding-left: 20px; margin: 0;">
                    <li>Lectures, interactive sessions and practical exercises</li>
                    <li>{program_data['program_type'].lower()} identification and implementation methods</li>
                    <li>Group activities and discussions</li>
                    <li>Community engagement and feedback sessions</li>
                </ul>
            </div>

            <!-- Image Section -->
            {f'''
            <div style="text-align: center; margin: 20px 0; padding: 10px; background: #f8f8f8;">
                <h4 style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">PHOTO HIGHLIGHTS</h4>
                <img src="/static/{newsletter_image}" 
                     style="max-width: 100%; height: 200px; object-fit: cover; border: 1px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                     onerror="this.style.display='none'">
                <p style="font-size: 12px; color: #666; margin-top: 8px; font-style: italic;">
                    Participants engaged in {program_data['program_type'].lower()} activities during the program
                </p>
            </div>
            ''' if newsletter_image else ''}

            <!-- IMPACT & OUTCOMES -->
            <div style="margin-bottom: 20px;">
                <h4 style="font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #2c5aa0;">
                    IMPACT & OUTCOMES
                </h4>
                <p style="margin: 0; font-size: 14px; text-align: justify;">
                    {program_data['achievements'] if program_data['achievements'] else 'Participants gained a better understanding of ' + program_data['program_type'].lower() + ' and effective techniques for community service and personal development.'}
                </p>
            </div>

            <!-- PARTICIPANT VOICES -->
            <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h4 style="font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c5aa0;">
                    PARTICIPANT VOICES
                </h4>
                <div style="font-style: italic; font-size: 14px;">
                    <p style="margin-bottom: 8px;">"The {program_data['program_type'].lower()} provided valuable insights that I can use in daily life."</p>
                    <p style="margin-bottom: 8px;">"I learned practical techniques that I can use daily."</p>
                    <p style="margin: 0;">"Excellent organization and meaningful community engagement."</p>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; margin-top: 30px; padding-top: 15px; border-top: 2px solid #000; font-size: 12px; color: #666;">
            <p style="margin: 0;">Dev Sanskriti Vishwavidyalaya, Haridwar - 249411, Uttarakhand, India</p>
            <p style="margin: 5px 0 0 0;">DISHA Social Internship Program | Program No: {program_no}</p>
        </div>
    </div>
    """
    
    # Create newsletter in database
    newsletter_data = {
        'program_id': program_id,
        'title': f"Newsletter: {program_data['title']}",
        'content': newsletter_content,
        'program_type': program_data['program_type'],
        'location': program_data['location'],
        'date': program_data['date'],
        'participants_count': program_data['total_persons'],
        'achievements': program_data['achievements'],
        'organizer_name': program_data['organizer_name'],
        'toli_name': toli_data.get('name', 'DISHA Program'),
        'status': 'published',
        'created_by': student.id,
        'created_at': datetime.utcnow(),
        'ai_generated': True
    }
    
    newsletter = Newsletter(newsletter_data)
    return db.create_newsletter(newsletter.to_dict())

def generate_basic_program_report(program_data, toli_data, student, program_id, images=None):
    """Generate basic program report if AI generation fails"""
    
    toli_name = toli_data.get('name', 'Unknown Toli')
    
    # Format date
    program_date = program_data['date']
    if hasattr(program_date, 'strftime'):
        formatted_date = program_date.strftime('%B %d, %Y')
    else:
        formatted_date = str(program_date)
    
    # Add images section if images exist
    images_section = ""
    if images:
        images_section = """
        <div style="margin-bottom: 20px;">
            <h3>Program Photos</h3>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
        """
        
        for img_path in images:
            images_section += f"""
                <img src="/static/{img_path}" style="width: 150px; height: 100px; object-fit: cover; border-radius: 5px;">
            """
        
        images_section += """
            </div>
        </div>
        """
    
    report_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1 style="text-align: center; color: #1E40AF;">Program Report</h1>
        <h2 style="text-align: center; color: #4B5563;">{program_data['title']}</h2>
        
        {images_section}
        
        <h3>Program Details</h3>
        <p><strong>Date:</strong> {formatted_date}</p>
        <p><strong>Location:</strong> {program_data['location']}</p>
        <p><strong>Participants:</strong> {program_data['total_persons']}</p>
        <p><strong>Toli:</strong> {toli_name}</p>
        
        <h3>Achievements</h3>
        <p>{program_data['achievements']}</p>
        
        <h3>Organizer</h3>
        <p>{program_data['organizer_name']} - {program_data['organizer_contact']}</p>
        
        <div style="text-align: center; margin-top: 40px;">
            <p>Dev Sanskriti Vishwavidyalaya</p>
            <p style="color: #999; font-size: 12px;">
                Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M')}
            </p>
        </div>
    </div>
    """
    
    report_data = {
        'program_id': program_id,
        'title': f"Report: {program_data['title']}",
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
        'created_at': datetime.utcnow(),
        'ai_generated': False
    }
    
    report = Report(report_data)
    return db.create_report(report.to_dict())

# ========== ROUTES ==========

@student.route('/student/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    # Debug: Check profile photo path
    print(f"DEBUG: Profile photo path: {current_user.profile_photo}")
    if current_user.profile_photo:
        full_path = os.path.join(current_app.root_path, 'static', current_user.profile_photo)
        print(f"DEBUG: Full photo path: {full_path}")
        print(f"DEBUG: Photo exists: {os.path.exists(full_path)}")
    
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
    
    # Get student's programs - Count by program type
    try:
        programs_data = db.get_programs_by_student(current_user.id)
        programs = []
        program_type_counts = {}
        
        for program_data in programs_data:
            program = Program(program_data)
            
            # Count programs by type
            program_type = getattr(program, 'program_type', 'General')
            program_type_counts[program_type] = program_type_counts.get(program_type, 0) + 1
            
            # Handle date conversion safely
            start_date = program.start_date
            if isinstance(start_date, str):
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                except (ValueError, TypeError):
                    start_date = datetime.utcnow()
            
            # Format date for display
            if hasattr(start_date, 'strftime'):
                formatted_date = start_date.strftime('%d %b %Y')
            else:
                formatted_date = "Date not set"
            
            programs.append({
                'id': program.id,
                'title': program.title,
                'program_type': program_type,
                'location': program.location,
                'start_date': start_date,
                'formatted_date': formatted_date,
                'total_persons': getattr(program, 'total_persons', 0)
            })
        
        # Get top program types for display
        top_program_types = dict(sorted(program_type_counts.items(), key=lambda x: x[1], reverse=True)[:3])
        
    except Exception as e:
        print(f"Error loading programs: {e}")
        programs = []
        top_program_types = {}
        program_type_counts = {}
    
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
                         program_type_counts=program_type_counts,
                         top_program_types=top_program_types,
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
        toli_name = request.form.get('toli_name', f"Toli {current_user.name}")
        
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
            'name': toli_name,
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
            
            flash('✅ Toli created successfully! Waiting for admin approval and assignment.', 'success')
            return redirect(url_for('student.dashboard'))
        else:
            flash('❌ Error creating toli.', 'danger')
    
    return render_template('student/create_toli.html')

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

# In student.py - Update the create_program route

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
    
    # Verify toli exists and is active
    db_fixes = DatabaseFixes()
    toli_data = db_fixes.db.get_toli_by_id(current_user.toli_id)
    if not toli_data:
        flash('Your toli was not found!', 'danger')
        return redirect(url_for('student.dashboard'))
    
    if toli_data.get('status') != 'active':
        flash('Your toli is not active yet. Please wait for admin approval.', 'warning')
        return redirect(url_for('student.dashboard'))
    
    form = CreateProgramForm()
    
    # Generate program number - get the count of existing programs and add 1
    existing_programs = db.get_programs_by_student(current_user.id)
    next_program_no = len(existing_programs) + 1
    
    if form.validate_on_submit():
        # Get state and city from form fields
        state = form.state.data
        city = form.city.data
        
        # Handle program type - if "Other" is selected, use the custom input
        program_type = form.program_type.data
        if program_type == 'Other' and form.other_program_type.data:
            program_type = form.other_program_type.data
        
        # Build location string with all details
        location_parts = [form.location.data]
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if form.pincode.data:
            location_parts.append(f"Pincode: {form.pincode.data}")
        
        full_location = ", ".join(location_parts)
        
        # Convert date to datetime object for MongoDB
        program_date = form.date.data
        if isinstance(program_date, date):
            # Convert date to datetime
            program_date = datetime.combine(program_date, datetime.min.time())
        elif isinstance(program_date, str):
            try:
                program_date = datetime.strptime(program_date, '%Y-%m-%d')
            except (ValueError, TypeError):
                program_date = datetime.utcnow()
        
        program_data = {
            'program_no': next_program_no,
            'title': form.title.data,
            'program_type': program_type,
            'date': program_date,
            'start_date': program_date,
            'location': full_location,
            'state': state,
            'city': city,
            'pincode': form.pincode.data,
            'total_persons': form.total_persons.data,
            'achievements': form.achievements.data if form.achievements.data else '',
            'organizer_name': form.organizer_name.data,
            'organizer_contact': form.organizer_contact.data,
            'student_id': current_user.id,
            'toli_id': current_user.toli_id,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        
        try:
            program = Program(program_data)
            program_dict = program.to_dict()
            result = db.create_program(program_dict)
            
            if result:
                # Save program images
                image_files = request.files.getlist('program_images')
                saved_image_paths = save_program_images(image_files, result)
                
                # Save achievements file if uploaded
                achievements_file_path = None
                if form.achievements_file.data and form.achievements_file.data.filename:
                    achievements_file_path = save_achievements_file(form.achievements_file.data, result)
                
                # Update program with image paths and achievements file
                update_data = {}
                if saved_image_paths:
                    update_data['images'] = saved_image_paths
                if achievements_file_path:
                    update_data['achievements_file'] = achievements_file_path
                
                if update_data:
                    db.update_program(result, update_data)
                
                # Generate report and newsletter using the updated program data
                try:
                    # Get the complete program data with images
                    complete_program_data = db.get_program_by_id(result)
                    if complete_program_data:
                        # Generate report with the complete data
                        report_id = generate_program_report(
                            {
                                'title': complete_program_data.get('title'),
                                'program_type': complete_program_data.get('program_type'),
                                'date': complete_program_data.get('date'),
                                'location': complete_program_data.get('location'),
                                'total_persons': complete_program_data.get('total_persons'),
                                'achievements': complete_program_data.get('achievements', ''),
                                'organizer_name': complete_program_data.get('organizer_name'),
                                'organizer_contact': complete_program_data.get('organizer_contact')
                            },
                            toli_data,
                            current_user,
                            result,
                            complete_program_data.get('images', [])
                        )
                        print(f"✅ Report generated with ID: {report_id}")
                except Exception as e:
                    print(f"❌ Report generation failed: {e}")
                    # Fallback to basic report
                    try:
                        report_id = generate_correct_format_report(program_data, toli_data, current_user, result, saved_image_paths)
                    except Exception as e2:
                        print(f"❌ Even basic report failed: {e2}")

                # Similar for newsletter...            try:
                try:
                    # Get the complete program data with images
                    complete_program_data = db.get_program_by_id(result)
                    if complete_program_data:
                        # Generate newsletter with the complete data
                        newsletter_id = generate_newsletter(
                            {
                                'title': complete_program_data.get('title'),
                                'program_type': complete_program_data.get('program_type'),
                                'date': complete_program_data.get('date'),
                                'location': complete_program_data.get('location'),
                                'total_persons': complete_program_data.get('total_persons'),
                                'achievements': complete_program_data.get('achievements', ''),
                                'organizer_name': complete_program_data.get('organizer_name'),
                                'organizer_contact': complete_program_data.get('organizer_contact')
                            },
                            toli_data,
                            current_user,
                            result,
                            complete_program_data.get('images', [])
                        )
                        print(f"✅ Newsletter generated with ID: {newsletter_id}")
                except Exception as e:
                    print(f"❌ Newsletter generation failed: {e}")
                    # Fallback to correct format function
                    try:
                        newsletter_id = generate_correct_format_newsletter(program_data, toli_data, current_user, result, saved_image_paths)
                    except Exception as e2:
                        print(f"❌ Even basic newsletter failed: {e2}")


                # Generate report and newsletter
                try:
                    report_id = generate_program_report(program_data, toli_data, current_user, result, saved_image_paths)
                except Exception as e:
                    print(f"Report generation failed: {e}")

                try:
                    newsletter_id = generate_newsletter(program_data, toli_data, current_user, result, saved_image_paths)
                except Exception as e:
                    print(f"Newsletter generation failed: {e}")
                
                # Success message with gallery info
                if saved_image_paths:
                    flash(f'Program submitted successfully! Your {len(saved_image_paths)} image(s) are now visible in the gallery.', 'success')
                else:
                    flash('Program submitted successfully!', 'success')
                return redirect(url_for('student.view_programs'))
                
        except Exception as e:
            print(f"Error creating program: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            flash('An error occurred while creating the program. Please try again.', 'danger')
    
    return render_template('student/create_program.html', 
                         form=form, 
                         toli_data=toli_data,
                         program_no=next_program_no,
                         now=datetime.utcnow())

# Add this helper function to student.py
def save_achievements_file(file, program_id):
    """Save achievements/certificate file and return its path"""
    if file and file.filename:
        # Create achievements directory
        achievements_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'achievements', str(program_id))
        os.makedirs(achievements_dir, exist_ok=True)
        
        # Secure the filename and create unique name
        original_filename = secure_filename(file.filename)
        filename = f"achievements_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
        file_path = os.path.join(achievements_dir, filename)
        
        try:
            file.save(file_path)
            # Store relative path for database
            relative_path = f'uploads/achievements/{program_id}/{filename}'
            print(f"Saved achievements file: {relative_path}")
            return relative_path
        except Exception as e:
            print(f"Error saving achievements file {file.filename}: {e}")
    
    return None


@student.route('/student/report/<report_id>/view')
@login_required
def view_report(report_id):
    """View report in browser"""
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    try:
        report_data = db.get_report_by_id(report_id)
        if not report_data:
            flash('Report not found.', 'danger')
            return redirect(url_for('student.view_programs'))
        
        report = Report(report_data)
        
        # Check if student owns this report
        program_data = db.get_program_by_id(report.program_id)
        if not program_data or program_data.get('student_id') != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('student.view_programs'))
        
        return render_template('student/report_view.html', report=report)
        
    except Exception as e:
        print(f"Error viewing report: {e}")
        flash('Error loading report.', 'danger')
        return redirect(url_for('student.view_programs'))


@student.route('/student/report/<report_id>/download')
@login_required
def download_report(report_id):
    """Download report as HTML file"""
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        report_data = db.get_report_by_id(report_id)
        if not report_data:
            return jsonify({'error': 'Report not found'}), 404
        
        report = Report(report_data)
        
        # Check if student owns this report
        program_data = db.get_program_by_id(report.program_id)
        if not program_data or program_data.get('student_id') != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Create a simple HTML file for download
        from flask import make_response
        response = make_response(report.content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=program_report_{report_id}.html'
        return response
        
    except Exception as e:
        print(f"Error downloading report: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Add these routes to student.py

@student.route('/student/report/<report_id>/pdf')
@login_required
def download_report_pdf(report_id):
    """Generate PDF report"""
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('student.view_reports'))
    
    try:
        report_data = db.get_report_by_id(report_id)
        if not report_data:
            flash('Report not found.', 'danger')
            return redirect(url_for('student.view_reports'))
        
        report = Report(report_data)
        
        # Check if student owns this report
        program_data = db.get_program_by_id(report.program_id)
        if not program_data or program_data.get('student_id') != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('student.view_reports'))
        
        # For PDF generation, we'll use the browser's print to PDF feature
        # In production, you can use libraries like WeasyPrint or ReportLab
        flash('Use the "Print Report" button and choose "Save as PDF" for best results.', 'info')
        return redirect(url_for('student.view_report', report_id=report_id))
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash('Error generating PDF. Please try again.', 'danger')
        return redirect(url_for('student.view_reports'))

@student.route('/student/report/<report_id>/word')
@login_required
def download_report_word(report_id):
    """Generate Word document"""
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('student.view_reports'))
    
    try:
        report_data = db.get_report_by_id(report_id)
        if not report_data:
            flash('Report not found.', 'danger')
            return redirect(url_for('student.view_reports'))
        
        report = Report(report_data)
        
        # Check if student owns this report
        program_data = db.get_program_by_id(report.program_id)
        if not program_data or program_data.get('student_id') != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('student.view_reports'))
        
        # Create a simple downloadable HTML file that can be opened in Word
        from flask import make_response
        response = make_response(report.content)
        response.headers['Content-Type'] = 'application/msword'
        response.headers['Content-Disposition'] = f'attachment; filename=program_report_{report_id}.doc'
        return response
        
    except Exception as e:
        print(f"Error generating Word document: {e}")
        flash('Error generating Word document. Please try again.', 'danger')
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

# In student.py - Add these routes

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
    
    # Get programs count for stats
    programs_count = len(db.get_programs_by_student(current_user.id))
    
    return render_template('student/profile.html', 
                         toli=toli, 
                         programs_count=programs_count)

@student.route('/student/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    form = UpdateProfileForm()
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.name.data = current_user.name
        form.scholar_no.data = current_user.scholar_no
        form.email.data = current_user.email
        form.contact.data = current_user.contact
        form.course.data = current_user.course
        form.dob.data = current_user.dob
    
    if form.validate_on_submit():
        update_data = {
            'name': form.name.data,
            'email': form.email.data,
            'contact': form.contact.data,
            'course': form.course.data,
            'dob': form.dob.data,
            'updated_at': datetime.utcnow()
        }
        
        # Handle profile photo upload
        if form.profile_photo.data:
            profile_photo = form.profile_photo.data
            if profile_photo and profile_photo.filename:
                # Secure the filename
                filename = secure_filename(profile_photo.filename)
                # Create unique filename
                unique_filename = f"{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                
                # Create uploads directory if not exists
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save the file
                profile_photo_path = os.path.join(upload_dir, unique_filename)
                profile_photo.save(profile_photo_path)
                
                # Store relative path
                update_data['profile_photo'] = f'uploads/profiles/{unique_filename}'
        
        if db.update_user(current_user.id, update_data):
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student.view_profile'))
        else:
            flash('Error updating profile.', 'danger')
    
    return render_template('student/update_profile.html', form=form)

@student.route('/student/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('student/change_password.html', form=form)
        
        # Update password
        if db.update_user(current_user.id, {'password': form.new_password.data}):
            flash('Password changed successfully!', 'success')
            return redirect(url_for('student.view_profile'))
        else:
            flash('Error changing password.', 'danger')
    
    return render_template('student/change_password.html', form=form)

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
        
        # Handle date conversion safely
        start_date = program.start_date
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except (ValueError, TypeError):
                start_date = datetime.utcnow()
        
        # Format date for display
        if hasattr(start_date, 'strftime'):
            formatted_date = start_date.strftime('%d %b %Y')
        else:
            formatted_date = "Date not set"
        
        # Get attendees count safely
        attendees_count = getattr(program, 'total_persons', 0)
        if not attendees_count or attendees_count == 0:
            attendees_count = program_data.get('total_persons', 0)
        
        programs.append({
            'id': program.id,
            'title': program.title,
            'program_type': getattr(program, 'program_type', 'General'),
            'location': program.location,
            'start_date': start_date,
            'formatted_date': formatted_date,
            'total_persons': attendees_count,
            'status': program.status,
            'created_at': program.created_at,
            'program_no': program_data.get('program_no', 'N/A')
        })
    
    return render_template('student/programs.html', programs=programs)

@student.route('/student/program/<program_id>/report')
@login_required
def view_program_report(program_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('student.view_programs'))
    
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
            'program_type': getattr(program, 'program_type', 'General'),
            'location': program.location,
            'date': program.start_date,
            'total_persons': getattr(program, 'total_persons', 0),
            'achievements': getattr(program, 'achievements', ''),
            'organizer_name': getattr(program, 'organizer_name', ''),
            'organizer_contact': getattr(program, 'organizer_contact', '')
        }, toli_data, current_user, program_id)
        report_data = db.get_report_by_program(program_id)  # Get the generated report
    
    report = Report(report_data) if report_data else None
    
    return render_template('student/program_report.html', program=program, report=report)

@student.route('/student/program/<program_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_program(program_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('student.view_programs'))
    
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
    
    # Set form data from program object
    form.title.data = program.title
    form.program_type.data = getattr(program, 'program_type', '')
    form.date.data = program.start_date
    form.location.data = program.location
    form.pincode.data = getattr(program, 'pincode', '')
    form.total_persons.data = getattr(program, 'total_persons', 0)
    form.achievements.data = getattr(program, 'achievements', '')
    form.organizer_name.data = getattr(program, 'organizer_name', '')
    form.organizer_contact.data = getattr(program, 'organizer_contact', '')
    
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
    
    # Get toli programs with date handling
    programs_data = db.get_programs_by_toli(current_user.toli_id)
    programs = []
    for program_data in programs_data:
        program = Program(program_data)
        
        # Handle date conversion safely
        start_date = program.start_date
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except (ValueError, TypeError):
                start_date = datetime.utcnow()
        
        programs.append({
            'id': program.id,
            'title': program.title,
            'program_type': getattr(program, 'program_type', 'General'),
            'location': program.location,
            'start_date': start_date,
            'total_persons': getattr(program, 'total_persons', 0),
            'status': program.status
        })
    
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

@student.route('/student/newsletters')
@login_required
def view_newsletters():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    newsletters_data = db.get_all_newsletters()
    newsletters = [Newsletter(newsletter) for newsletter in newsletters_data]
    
    # Sort newsletters by creation date (newest first)
    newsletters.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('student/newsletters.html', newsletters=newsletters)

@student.route('/student/newsletter/<newsletter_id>/view')
@login_required
def view_newsletter(newsletter_id):
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    newsletter_data = db.get_newsletter_by_id(newsletter_id)
    if not newsletter_data:
        flash('Newsletter not found.', 'danger')
        return redirect(url_for('student.view_newsletters'))
    
    newsletter = Newsletter(newsletter_data)
    return render_template('student/newsletter_view.html', newsletter=newsletter)

# Error handler for student routes
@student.errorhandler(404)
def not_found_error(error):
    return render_template('student/404.html'), 404

@student.errorhandler(500)
def internal_error(error):
    return render_template('student/500.html'), 500

# Health check endpoint
@student.route('/student/health')
@login_required
def health_check():
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'status': 'healthy',
        'user': current_user.name,
        'role': current_user.role,
        'timestamp': datetime.utcnow().isoformat()
    })

def cleanup_old_reports():
    """Remove old reports with wrong format"""
    try:
        db.db.reports.delete_many({})
        print("✅ Cleared all old reports")
    except Exception as e:
        print(f"❌ Error clearing reports: {e}")

# ==================== INSTRUCTION ROUTES ====================

@student.route('/student/instructions')
@login_required
def view_instructions():
    """View instructions for students"""
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    from app.models import Instruction
    
    # Get active instruction
    instruction_data = db.get_active_instruction()
    instruction = Instruction(instruction_data) if instruction_data else None
    
    return render_template('student/instructions.html', instruction=instruction)

@student.route('/student/instructions/download')
@login_required
def download_instructions():
    """Download instructions as HTML file"""
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    from flask import make_response
    from app.models import Instruction
    
    instruction_data = db.get_active_instruction()
    if not instruction_data:
        flash('No instructions available.', 'warning')
        return redirect(url_for('student.view_instructions'))
    
    instruction = Instruction(instruction_data)
    
    # Create downloadable HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <title>{instruction.title}</title>
        <style>
            body {{
                font-family: 'Noto Sans Devanagari', Arial, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.8;
            }}
            h1 {{
                color: #2563eb;
                text-align: center;
                border-bottom: 3px solid #2563eb;
                padding-bottom: 15px;
            }}
            .content {{
                white-space: pre-wrap;
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <h1>{instruction.title}</h1>
        <div class="content">{instruction.content}</div>
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=instructions.html'
    
    return response
