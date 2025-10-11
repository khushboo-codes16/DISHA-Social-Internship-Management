from flask import Blueprint, render_template

main = Blueprint('main', __name__)

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

@main.route('/contact')
def contact():
    return render_template('main/contact.html')