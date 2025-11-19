from flask import Blueprint, render_template
from app.database import MongoDB
from app.models import Newsletter 

main = Blueprint('main', __name__)
db = MongoDB() 

# In main.py - Update the home route

@main.route('/')
def home():
    """Home page with recent newsletters and gallery preview"""
    try:
        # Get recent newsletters (last 3)
        newsletters_data = db.get_all_newsletters()
        recent_newsletters = [Newsletter(newsletter) for newsletter in newsletters_data[:3]]
        
        # Get recent gallery images (last 6)
        all_programs = db.get_all_programs()
        recent_gallery_images = []
        
        for program_data in all_programs[:6]:
            program = Program(program_data)
            images = getattr(program, 'images', [])
            
            if images:
                # Get toli name
                toli_name = "Unknown Toli"
                if hasattr(program, 'toli_id') and program.toli_id:
                    toli_data = db.get_toli_by_id(program.toli_id)
                    if toli_data:
                        toli_name = toli_data.get('name', 'Unknown Toli')
                
                # Take first image from each program
                recent_gallery_images.append({
                    'image_path': images[0],
                    'program_title': program.title,
                    'program_type': getattr(program, 'program_type', 'General'),
                    'location': getattr(program, 'location', 'Unknown Location'),
                    'toli_name': toli_name
                })
        
        return render_template('main/home.html', 
                             recent_newsletters=recent_newsletters,
                             recent_gallery_images=recent_gallery_images)
    except Exception as e:
        print(f"Error loading home page: {e}")
        return render_template('main/home.html', 
                             recent_newsletters=[],
                             recent_gallery_images=[])

@main.route('/about')
def about():
    return render_template('main/about.html')

# In main.py - Update the gallery route

@main.route('/gallery')
def gallery():
    """Display gallery with all program images"""
    try:
        # Get all programs with images
        all_programs = db.get_all_programs()
        
        gallery_images = []
        for program_data in all_programs:
            program = Program(program_data)
            images = getattr(program, 'images', [])
            
            if images:
                # Get toli name for display
                toli_name = "Unknown Toli"
                if hasattr(program, 'toli_id') and program.toli_id:
                    toli_data = db.get_toli_by_id(program.toli_id)
                    if toli_data:
                        toli_name = toli_data.get('name', 'Unknown Toli')
                
                for img_path in images:
                    gallery_images.append({
                        'image_path': img_path,
                        'program_title': program.title,
                        'program_type': getattr(program, 'program_type', 'General'),
                        'location': getattr(program, 'location', 'Unknown Location'),
                        'toli_name': toli_name
                    })
        
        return render_template('main/gallery.html', gallery_images=gallery_images)
    except Exception as e:
        print(f"Error loading gallery: {e}")
        return render_template('main/gallery.html', gallery_images=[])

@main.route('/news')
def news():
    return render_template('main/news.html')

@main.route('/resources')
def resources():
    return render_template('main/resources.html')

@main.route('/newsletter')
def newsletter():
    """Display all newsletters"""
    newsletters_data = db.get_all_newsletters()
    newsletters = [Newsletter(newsletter) for newsletter in newsletters_data]
    
    return render_template('main/newsletter.html', newsletters=newsletters)

@main.route('/newsletter/<newsletter_id>')
def newsletter_detail(newsletter_id):
    """Display single newsletter detail"""
    newsletter_data = db.get_newsletter_by_id(newsletter_id)
    if not newsletter_data:
        flash('Newsletter not found.', 'danger')
        return redirect(url_for('main.newsletter'))
    
    newsletter = Newsletter(newsletter_data)
    return render_template('main/newsletter_detail.html', newsletter=newsletter)

@main.route('/contact')
def contact():
    return render_template('main/contact.html')