from flask import Blueprint, render_template
from app.database import MongoDB
from app.models import Newsletter 

main = Blueprint('main', __name__)
db = MongoDB() 

@main.route('/')
def home():
    return render_template('main/home.html')

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/gallery')
def gallery():
    return render_template('main/gallery.html')

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