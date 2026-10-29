from flask import Blueprint, request, jsonify, abort
from app.database import db
from app.models import News
from sqlalchemy import func, desc

bp = Blueprint('news', __name__)

@bp.route('/', methods=['GET'])
def get_news():
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 12))
    news = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).offset(skip).limit(limit).all()
    return jsonify([n.to_dict() for n in news])

@bp.route('/featured', methods=['GET'])
def get_featured_news():
    limit = int(request.args.get('limit', 3))
    news = News.query.filter_by(is_published=True).order_by(News.views.desc()).limit(limit).all()
    return jsonify([n.to_dict() for n in news])

@bp.route('/search', methods=['GET'])
def search_news():
    q = request.args.get('q')
    if not q:
        return jsonify([])
    news = News.query.filter(News.is_published == True, (News.title.ilike(f"%{q}%") | News.content.ilike(f"%{q}%") | News.excerpt.ilike(f"%{q}%"))).order_by(News.published_at.desc()).all()
    return jsonify([n.to_dict() for n in news])

@bp.route('/filter', methods=['GET'])
def filter_news():
    month = request.args.get('month')
    year = request.args.get('year')
    query = News.query.filter_by(is_published=True)
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    if month and month in month_map:
        query = query.filter(func.extract('month', News.published_at) == month_map[month])
    if year:
        query = query.filter(func.extract('year', News.published_at) == int(year))
    news = query.order_by(News.published_at.desc()).all()
    return jsonify([n.to_dict() for n in news])

@bp.route('/years', methods=['GET'])
def get_years():
    years = db.session.query(func.distinct(func.extract('year', News.published_at))).filter(News.is_published == True).order_by(func.extract('year', News.published_at).desc()).all()
    years_list = [int(y[0]) for y in years if y[0] is not None]
    return jsonify(years_list)

@bp.route('/<news_id>', methods=['GET'])
def get_news_item(news_id):
    news = News.query.get(news_id)
    if not news:
        abort(404)
    news.views += 1
    db.session.commit()
    return jsonify(news.to_dict())