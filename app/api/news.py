from flask import jsonify, request
from app.api import api_bp
from app.models import News
from sqlalchemy import desc

@api_bp.route('/news', methods=['GET'])
def get_news():
    news_items = News.query.filter_by(is_published=True).order_by(desc(News.created_at)).all()
    result = []
    for news in news_items:
        result.append({
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'image': news.image,
            'created_at': news.created_at.isoformat(),
            'author': news.author.name
        })
    return jsonify(result)

@api_bp.route('/news/<int:news_id>', methods=['GET'])
def get_news_item(news_id):
    news = News.query.get_or_404(news_id)
    return jsonify({
        'id': news.id,
        'title': news.title,
        'content': news.content,
        'image': news.image,
        'created_at': news.created_at.isoformat(),
        'author': news.author.name
    })