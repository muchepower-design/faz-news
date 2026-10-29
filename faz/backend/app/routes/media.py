from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Video, Gallery, GalleryImage
from app.schemas import VideoCreate, GalleryCreate, GalleryImageCreate
from app.auth import get_current_user

bp = Blueprint('media', __name__)

# ============ VIDEOS ============
@bp.route('/videos', methods=['GET'])
def get_videos():
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 12))
    videos = Video.query.filter_by(is_published=True).order_by(Video.published_at.desc()).offset(skip).limit(limit).all()
    return jsonify([v.to_dict() for v in videos])

@bp.route('/videos/search', methods=['GET'])
def search_videos():
    q = request.args.get('q')
    if not q:
        return jsonify([])
    videos = Video.query.filter(Video.is_published == True, (Video.title.ilike(f"%{q}%") | Video.description.ilike(f"%{q}%"))).all()
    return jsonify([v.to_dict() for v in videos])

@bp.route('/videos/<video_id>', methods=['GET'])
def get_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        abort(404)
    video.views += 1
    db.session.commit()
    return jsonify(video.to_dict())

@bp.route('/videos', methods=['POST'])
@jwt_required()
def create_video():
    user = get_current_user()
    if user.role not in ['admin', 'media_officer']:
        abort(403)
    data = request.get_json()
    youtube_id = data['youtube_url'].split('v=')[-1].split('&')[0]
    video = Video(
        title=data['title'],
        youtube_url=data['youtube_url'],
        youtube_id=youtube_id,
        thumbnail_url=f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg",
        description=data.get('description'),
        duration=data.get('duration'),
        is_published=data.get('is_published', True)
    )
    db.session.add(video)
    db.session.commit()
    return jsonify({"id": str(video.id)}), 201

@bp.route('/videos/<video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    user = get_current_user()
    if user.role not in ['admin', 'media_officer']:
        abort(403)
    video = Video.query.get(video_id)
    if not video:
        abort(404)
    db.session.delete(video)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ============ GALLERIES ============
@bp.route('/galleries', methods=['GET'])
def get_galleries():
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 12))
    galleries = Gallery.query.filter_by(is_published=True).order_by(Gallery.created_at.desc()).offset(skip).limit(limit).all()
    return jsonify([g.to_dict() for g in galleries])

@bp.route('/galleries/search', methods=['GET'])
def search_galleries():
    q = request.args.get('q')
    if not q:
        return jsonify([])
    galleries = Gallery.query.filter(Gallery.is_published == True, (Gallery.title.ilike(f"%{q}%") | Gallery.description.ilike(f"%{q}%"))).all()
    return jsonify([g.to_dict() for g in galleries])

@bp.route('/galleries/<gallery_id>', methods=['GET'])
def get_gallery(gallery_id):
    gallery = Gallery.query.get(gallery_id)
    if not gallery:
        abort(404)
    return jsonify(gallery.to_dict())

@bp.route('/galleries', methods=['POST'])
@jwt_required()
def create_gallery():
    user = get_current_user()
    if user.role not in ['admin', 'media_officer']:
        abort(403)
    data = request.get_json()
    gallery = Gallery(
        title=data['title'],
        description=data.get('description'),
        cover_image=data.get('cover_image'),
        event_date=data.get('event_date'),
        is_published=data.get('is_published', True)
    )
    db.session.add(gallery)
    db.session.commit()
    return jsonify({"id": str(gallery.id)}), 201

@bp.route('/galleries/<gallery_id>/images', methods=['POST'])
@jwt_required()
def add_gallery_image(gallery_id):
    user = get_current_user()
    if user.role not in ['admin', 'media_officer']:
        abort(403)
    gallery = Gallery.query.get(gallery_id)
    if not gallery:
        abort(404)
    data = request.get_json()
    image = GalleryImage(
        gallery_id=gallery_id,
        image_url=data['image_url'],
        caption=data.get('caption'),
        order=data.get('order', 0)
    )
    db.session.add(image)
    db.session.commit()
    return jsonify({"id": str(image.id)}), 201

@bp.route('/galleries/<gallery_id>', methods=['DELETE'])
@jwt_required()
def delete_gallery(gallery_id):
    user = get_current_user()
    if user.role not in ['admin', 'media_officer']:
        abort(403)
    gallery = Gallery.query.get(gallery_id)
    if not gallery:
        abort(404)
    db.session.delete(gallery)
    db.session.commit()
    return jsonify({"message": "Deleted"})

@bp.route('/galleries/<gallery_id>/images/<image_id>', methods=['DELETE'])
@jwt_required()
def delete_gallery_image(gallery_id, image_id):
    user = get_current_user()
    if user.role not in ['admin', 'media_officer']:
        abort(403)
    image = GalleryImage.query.filter_by(id=image_id, gallery_id=gallery_id).first()
    if not image:
        abort(404)
    db.session.delete(image)
    db.session.commit()
    return jsonify({"message": "Deleted"})