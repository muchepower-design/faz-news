from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
import uuid
import re
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from models import db, User, FacebookPage, FacebookPost, FacebookComment, PostAttachment
from models import CommentModerationQueue, ModerationRule, BlockedUser, ScheduledPost, PostDraft, PublishingHistory
from models import ActivityLog, AnalyticsCache, WebhookLog, UserPageAccess
from facebook_service import FacebookService

# Initialize app
app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Initialize extensions
CORS(app, origins=Config.CORS_ORIGINS)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create uploads directory
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ============ HELPER FUNCTIONS ============

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def log_activity(user_id, action, target_type, target_id, details=None, ip_address=None):
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        details=details or {},
        ip_address=ip_address or request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()

def perform_initial_sync(page_id, page_access_token):
    """Perform initial backfill of all historical data"""
    fb_service = FacebookService(page_access_token)
    page = FacebookPage.query.filter_by(page_id=page_id).first()
    
    if not page:
        return
    
    try:
        posts = fb_service.get_all_historical_posts(page_id)
        
        for post_data in posts:
            existing = FacebookPost.query.filter_by(post_id=post_data['id']).first()
            if existing:
                continue
            
            post = FacebookPost(
                post_id=post_data['id'],
                page_id=page.id,
                message=post_data.get('message') or post_data.get('story'),
                story=post_data.get('story'),
                permalink_url=post_data.get('permalink_url'),
                post_type=post_data.get('type'),
                created_time=datetime.fromisoformat(post_data['created_time'].replace('Z', '+00:00')),
                updated_time=datetime.fromisoformat(post_data['updated_time'].replace('Z', '+00:00')) if post_data.get('updated_time') else None,
                like_count=post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
                comment_count=post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
                share_count=post_data.get('shares', {}).get('count', 0),
                has_images='photo' in post_data.get('type', ''),
                has_videos='video' in post_data.get('type', ''),
                is_from_backfill=True
            )
            db.session.add(post)
            db.session.commit()
            
            attachments = fb_service.get_post_attachments(post_data['id'])
            for att in attachments:
                attachment = PostAttachment(
                    post_id=post.id,
                    attachment_id=att.get('attachment_id'),
                    media_type=att.get('media_type'),
                    url=att.get('url'),
                    thumbnail_url=att.get('thumbnail_url'),
                    video_duration=att.get('video_duration'),
                    video_status=att.get('video_status'),
                    display_order=att.get('display_order')
                )
                db.session.add(attachment)
            
            comments = fb_service.get_post_comments(post_data['id'])
            for comment_data in comments:
                comment = FacebookComment(
                    comment_id=comment_data['comment_id'],
                    post_id=post.id,
                    message=comment_data['message'],
                    author_name=comment_data['author_name'],
                    author_id=comment_data['author_id'],
                    created_time=datetime.fromisoformat(comment_data['created_time'].replace('Z', '+00:00')),
                    like_count=comment_data['like_count'],
                    parent_comment_id=comment_data['parent_comment_id']
                )
                db.session.add(comment)
            
            db.session.commit()
            
        page.last_synced_at = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        print(f"Sync failed: {e}")

# ============ AUTHENTICATION ENDPOINTS ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'viewer')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role}
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    login_user(user, remember=data.get('remember', False))
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    log_activity(user.id, 'login', 'user', user.id, {'ip': request.remote_addr})
    
    # Return token for frontend
    token = user.get_id()
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    log_activity(current_user.id, 'logout', 'user', current_user.id, {})
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'created_at': current_user.created_at.isoformat(),
        'last_login': current_user.last_login.isoformat() if current_user.last_login else None
    })

# ============ FACEBOOK FEED ENDPOINTS ============

@app.route('/api/posts', methods=['GET'])
def get_posts():
    page_id = request.args.get('page_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query = FacebookPost.query
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(FacebookPost.created_time >= start)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(FacebookPost.created_time <= end)
        except:
            pass
    
    page_record = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    if page_record:
        query = query.filter_by(page_id=page_record.id)
    
    total = query.count()
    posts = query.order_by(FacebookPost.created_time.desc()).offset(offset).limit(limit).all()
    
    result = []
    for post in posts:
        result.append({
            'id': post.post_id,
            'message': post.message or post.story,
            'type': post.post_type,
            'created_time': post.created_time.isoformat(),
            'permalink_url': post.permalink_url,
            'metrics': {
                'likes': post.like_count,
                'comments': post.comment_count,
                'shares': post.share_count
            },
            'media': {
                'has_images': post.has_images,
                'has_videos': post.has_videos,
                'has_live_video': post.has_live_video,
                'attachments': [{
                    'type': a.media_type,
                    'url': a.url,
                    'thumbnail': a.thumbnail_url,
                    'duration': a.video_duration
                } for a in post.attachments]
            },
            'comments': [{
                'id': c.comment_id,
                'author': c.author_name,
                'message': c.message,
                'created_time': c.created_time.isoformat(),
                'likes': c.like_count
            } for c in post.comments[:5]]
        })
    
    return jsonify({
        'total': total,
        'offset': offset,
        'limit': limit,
        'posts': result
    })

@app.route('/api/live-video', methods=['GET'])
def get_live_video():
    page_id = request.args.get('page_id')
    page = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    
    if not page:
        return jsonify({'live': False, 'message': 'No page configured'})
    
    live_post = FacebookPost.query.filter(
        FacebookPost.page_id == page.id,
        FacebookPost.has_live_video == True,
        FacebookPost.created_time >= datetime.utcnow() - timedelta(hours=24)
    ).first()
    
    if not live_post or not live_post.live_video_id:
        return jsonify({'live': False, 'message': 'No live video at the moment'})
    
    fb_service = FacebookService(page.access_token)
    live_info = fb_service.get_live_video_status(live_post.live_video_id)
    
    return jsonify({
        'live': live_info.get('status') == 'LIVE',
        'stream_url': live_info.get('stream_url'),
        'embed_html': live_info.get('embed_html'),
        'post_id': live_post.post_id,
        'message': live_post.message
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    page_id = request.args.get('page_id')
    page = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    total_posts = FacebookPost.query.filter_by(page_id=page.id).count()
    total_comments = db.session.query(FacebookComment).join(FacebookPost).filter(FacebookPost.page_id == page.id).count()
    oldest_post = FacebookPost.query.filter_by(page_id=page.id).order_by(FacebookPost.created_time.asc()).first()
    newest_post = FacebookPost.query.filter_by(page_id=page.id).order_by(FacebookPost.created_time.desc()).first()
    posts_with_images = FacebookPost.query.filter_by(page_id=page.id, has_images=True).count()
    posts_with_videos = FacebookPost.query.filter_by(page_id=page.id, has_videos=True).count()
    
    return jsonify({
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_images': posts_with_images,
        'total_videos': posts_with_videos,
        'oldest_post_date': oldest_post.created_time.isoformat() if oldest_post else None,
        'newest_post_date': newest_post.created_time.isoformat() if newest_post else None
    })

# ============ SEARCH ENDPOINTS ============

@app.route('/api/search', methods=['GET'])
def search_posts():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_likes = request.args.get('min_likes', type=int)
    min_comments = request.args.get('min_comments', type=int)
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    search_query = FacebookPost.query
    
    if query:
        search_query = search_query.filter(
            db.or_(
                FacebookPost.message.ilike(f'%{query}%'),
                FacebookPost.story.ilike(f'%{query}%')
            )
        )
    
    if search_type == 'photos':
        search_query = search_query.filter(FacebookPost.has_images == True)
    elif search_type == 'videos':
        search_query = search_query.filter(FacebookPost.has_videos == True)
    elif search_type == 'live':
        search_query = search_query.filter(FacebookPost.has_live_video == True)
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            search_query = search_query.filter(FacebookPost.created_time >= start)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            search_query = search_query.filter(FacebookPost.created_time <= end)
        except:
            pass
    
    if min_likes:
        search_query = search_query.filter(FacebookPost.like_count >= min_likes)
    
    if min_comments:
        search_query = search_query.filter(FacebookPost.comment_count >= min_comments)
    
    total = search_query.count()
    results = search_query.order_by(FacebookPost.created_time.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'query': query,
        'total': total,
        'offset': offset,
        'limit': limit,
        'results': [{
            'id': p.post_id,
            'message': p.message,
            'created_time': p.created_time.isoformat(),
            'like_count': p.like_count,
            'comment_count': p.comment_count
        } for p in results]
    })

@app.route('/api/search/suggestions', methods=['GET'])
def search_suggestions():
    term = request.args.get('term', '')
    
    # Get recent posts for content-based suggestions
    recent_posts = FacebookPost.query.order_by(
        FacebookPost.created_time.desc()
    ).limit(20).all()
    
    # Extract keywords from recent posts
    keywords = set()
    for post in recent_posts:
        if post.message:
            words = post.message.split()[:10]
            for w in words:
                if len(w) > 3 and w.lower() not in ['the', 'and', 'for', 'you', 'are', 'with']:
                    keywords.add(w.lower())
    
    return jsonify({
        'popular': list(keywords)[:10],
        'keywords': list(keywords)[:10]
    })

# ============ PUBLISHING ENDPOINTS ============

@app.route('/api/publish/text', methods=['POST'])
@login_required
def publish_text_post():
    data = request.json
    message = data.get('message')
    page_id = data.get('page_id')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    page = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    fb_service = FacebookService(page.access_token)
    result = fb_service.publish_text_post(page.page_id, message)
    
    if result['success']:
        history = PublishingHistory(
            page_id=page.id,
            posted_by=current_user.id,
            message=message,
            facebook_post_id=result['post_id'],
            facebook_permalink=result['permalink'],
            status='success',
            published_at=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()
        
        log_activity(current_user.id, 'publish_post', 'facebook_post', result['post_id'], {'type': 'text'})
        
        return jsonify({'success': True, 'post_id': result['post_id'], 'permalink': result['permalink']})
    else:
        return jsonify({'success': False, 'error': result.get('error')}), 500

@app.route('/api/publish/photo', methods=['POST'])
@login_required
def publish_photo_post():
    data = request.json
    image_url = data.get('image_url')
    caption = data.get('caption', '')
    page_id = data.get('page_id')
    
    if not image_url:
        return jsonify({'error': 'Image URL is required'}), 400
    
    page = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    fb_service = FacebookService(page.access_token)
    result = fb_service.publish_photo_post(page.page_id, image_url, caption)
    
    if result['success']:
        history = PublishingHistory(
            page_id=page.id,
            posted_by=current_user.id,
            message=caption,
            media_urls=[image_url],
            facebook_post_id=result['post_id'],
            facebook_permalink=result['permalink'],
            status='success'
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({'success': True, 'post_id': result['post_id'], 'permalink': result['permalink']})
    else:
        return jsonify({'success': False, 'error': result.get('error')}), 500

@app.route('/api/publish/link', methods=['POST'])
@login_required
def publish_link_post():
    data = request.json
    link_url = data.get('link_url')
    message = data.get('message', '')
    page_id = data.get('page_id')
    
    if not link_url:
        return jsonify({'error': 'Link URL is required'}), 400
    
    page = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    fb_service = FacebookService(page.access_token)
    result = fb_service.publish_link_post(page.page_id, link_url, message)
    
    if result['success']:
        history = PublishingHistory(
            page_id=page.id,
            posted_by=current_user.id,
            message=message,
            link_url=link_url,
            facebook_post_id=result['post_id'],
            facebook_permalink=result['permalink'],
            status='success'
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({'success': True, 'post_id': result['post_id'], 'permalink': result['permalink']})
    else:
        return jsonify({'success': False, 'error': result.get('error')}), 500

@app.route('/api/upload/image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    public_url = f"/uploads/{filename}"
    
    return jsonify({'url': public_url})


@app.route('/api/upload/video', methods=['POST'])
@login_required
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    public_url = f"/uploads/{filename}"
    
    return jsonify({'url': public_url})


# ============ DRAFTS ENDPOINTS ============

@app.route('/api/drafts', methods=['GET'])
@login_required
def get_drafts():
    drafts = PostDraft.query.filter_by(created_by=current_user.id, status='draft')\
        .order_by(PostDraft.updated_at.desc()).all()
    
    return jsonify([{
        'id': d.id,
        'message': d.message,
        'media_urls': d.media_urls,
        'link_url': d.link_url,
        'created_at': d.created_at.isoformat(),
        'updated_at': d.updated_at.isoformat()
    } for d in drafts])

@app.route('/api/drafts', methods=['POST'])
@login_required
def save_draft():
    data = request.json
    page = FacebookPage.query.first()
    
    draft = PostDraft(
        page_id=page.id if page else None,
        created_by=current_user.id,
        message=data.get('message'),
        media_urls=data.get('media_urls', []),
        link_url=data.get('link_url'),
        status='draft'
    )
    
    db.session.add(draft)
    db.session.commit()
    
    return jsonify({'message': 'Draft saved', 'draft_id': draft.id}), 201

@app.route('/api/drafts/<draft_id>', methods=['DELETE'])
@login_required
def delete_draft(draft_id):
    draft = PostDraft.query.get(draft_id)
    
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404
    
    if draft.created_by != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(draft)
    db.session.commit()
    
    return jsonify({'message': 'Draft deleted'})

@app.route('/api/publish/video', methods=['POST'])
@login_required
def publish_video_post():
    data = request.json
    video_url = data.get('video_url')
    title = data.get('title', '')
    description = data.get('description', '')
    page_id = data.get('page_id')
    
    if not video_url:
        return jsonify({'error': 'Video URL is required'}), 400
    
    page = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    fb_service = FacebookService(page.access_token)
    result = fb_service.publish_video_post(page.page_id, video_url, title, description)
    
    if result['success']:
        history = PublishingHistory(
            page_id=page.id,
            posted_by=current_user.id,
            message=title,
            media_urls=[video_url],
            facebook_post_id=result['post_id'],
            facebook_permalink=result['permalink'],
            status='success'
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({'success': True, 'post_id': result['post_id'], 'permalink': result['permalink']})
    else:
        return jsonify({'success': False, 'error': result.get('error')}), 500

@app.route('/api/publishing/history', methods=['GET'])
@login_required
def get_publishing_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = PublishingHistory.query
    
    if current_user.role != 'admin':
        query = query.filter_by(posted_by=current_user.id)
    
    history = query.order_by(PublishingHistory.published_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'history': [{
            'id': h.id,
            'message': h.message,
            'media_urls': h.media_urls,
            'link_url': h.link_url,
            'facebook_post_id': h.facebook_post_id,
            'facebook_permalink': h.facebook_permalink,
            'status': h.status,
            'error_message': h.error_message,
            'published_at': h.published_at.isoformat()
        } for h in history.items],
        'total': history.total,
        'page': page,
        'pages': history.pages
    })

# ============ ANALYTICS ENDPOINTS ============

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    page_id = request.args.get('page_id')
    period = request.args.get('period', '30')
    
    page = FacebookPage.query.filter_by(page_id=page_id).first() if page_id else FacebookPage.query.first()
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    try:
        days = int(period)
    except:
        days = 30
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    posts = FacebookPost.query.filter(
        FacebookPost.page_id == page.id,
        FacebookPost.created_time >= start_date,
        FacebookPost.created_time <= end_date
    ).all()
    
    total_posts = len(posts)
    total_likes = sum(p.like_count for p in posts)
    total_comments = sum(p.comment_count for p in posts)
    total_shares = sum(p.share_count for p in posts)
    
    daily_stats = {}
    for post in posts:
        date_key = post.created_time.strftime('%Y-%m-%d')
        if date_key not in daily_stats:
            daily_stats[date_key] = {'posts': 0, 'likes': 0, 'comments': 0, 'shares': 0}
        daily_stats[date_key]['posts'] += 1
        daily_stats[date_key]['likes'] += post.like_count
        daily_stats[date_key]['comments'] += post.comment_count
        daily_stats[date_key]['shares'] += post.share_count
    
    time_series = [{'date': d, **stats} for d, stats in sorted(daily_stats.items())]
    
    post_types = {}
    for post in posts:
        ptype = post.post_type or 'unknown'
        post_types[ptype] = post_types.get(ptype, 0) + 1
    
    top_posts = sorted(posts, key=lambda x: x.like_count + x.comment_count + x.share_count, reverse=True)[:10]
    
    return jsonify({
        'period': f'{days}_days',
        'summary': {
            'total_posts': total_posts,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'average_engagement_per_post': round((total_likes + total_comments + total_shares) / max(total_posts, 1), 2)
        },
        'time_series': time_series,
        'post_type_breakdown': post_types,
        'top_posts': [{
            'id': p.post_id,
            'message': (p.message or '')[:100],
            'created_time': p.created_time.isoformat(),
            'likes': p.like_count,
            'comments': p.comment_count,
            'shares': p.share_count,
            'total_engagement': p.like_count + p.comment_count + p.share_count
        } for p in top_posts]
    })

# ============ MODERATION ENDPOINTS ============

@app.route('/api/moderate/comments/pending', methods=['GET'])
@login_required
def get_pending_comments():
    pending = CommentModerationQueue.query.filter_by(status='pending')\
        .order_by(CommentModerationQueue.created_at.asc()).limit(50).all()
    
    results = []
    for queue_item in pending:
        comment = FacebookComment.query.get(queue_item.comment_id)
        if comment:
            results.append({
                'queue_id': queue_item.id,
                'comment_id': comment.comment_id,
                'message': comment.message,
                'author': comment.author_name,
                'created_time': comment.created_time.isoformat(),
                'post_id': comment.post_id,
                'moderation_flags': {
                    'contains_profanity': queue_item.contains_profanity,
                    'contains_spam': queue_item.contains_spam,
                    'contains_links': queue_item.contains_links,
                    'spam_score': queue_item.spam_score
                }
            })
    
    return jsonify({'comments': results})

@app.route('/api/moderate/comments/<comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    queue_item = CommentModerationQueue.query.filter_by(comment_id=comment_id).first()
    
    if not queue_item:
        return jsonify({'error': 'Comment not found'}), 404
    
    queue_item.status = 'approved'
    queue_item.moderated_by = current_user.id
    queue_item.moderated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Comment approved'})

@app.route('/api/moderate/comments/<comment_id>/reject', methods=['POST'])
@login_required
def reject_comment(comment_id):
    data = request.json
    queue_item = CommentModerationQueue.query.filter_by(comment_id=comment_id).first()
    
    if not queue_item:
        return jsonify({'error': 'Comment not found'}), 404
    
    queue_item.status = 'rejected'
    queue_item.moderated_by = current_user.id
    queue_item.moderated_at = datetime.utcnow()
    queue_item.moderation_reason = data.get('reason', 'Violates guidelines')
    db.session.commit()
    
    return jsonify({'message': 'Comment rejected'})

# ============ SCHEDULED POSTS ENDPOINTS ============

@app.route('/api/schedule/posts', methods=['GET'])
@login_required
def get_scheduled_posts():
    posts = ScheduledPost.query.filter_by(created_by=current_user.id, status='scheduled')\
        .order_by(ScheduledPost.scheduled_time.asc()).all()
    
    return jsonify([{
        'id': p.id,
        'message': p.message,
        'media_urls': p.media_urls,
        'link_url': p.link_url,
        'scheduled_time': p.scheduled_time.isoformat(),
        'status': p.status,
        'is_recurring': p.is_recurring,
        'recurring_pattern': p.recurring_pattern
    } for p in posts])

@app.route('/api/schedule/posts', methods=['POST'])
@login_required
def schedule_post():
    data = request.json
    page = FacebookPage.query.first()
    
    scheduled = ScheduledPost(
        page_id=page.id,
        created_by=current_user.id,
        message=data['message'],
        media_urls=data.get('media_urls', []),
        link_url=data.get('link_url'),
        scheduled_time=datetime.fromisoformat(data['scheduled_time']),
        is_recurring=data.get('is_recurring', False),
        recurring_pattern=data.get('recurring_pattern')
    )
    
    db.session.add(scheduled)
    db.session.commit()
    
    return jsonify({'message': 'Post scheduled', 'post_id': scheduled.id}), 201

@app.route('/api/schedule/posts/<post_id>', methods=['DELETE'])
@login_required
def cancel_scheduled_post(post_id):
    scheduled = ScheduledPost.query.get(post_id)
    
    if not scheduled:
        return jsonify({'error': 'Post not found'}), 404
    
    if scheduled.created_by != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    scheduled.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Post cancelled'})

@app.route('/api/schedule/templates', methods=['GET'])
@login_required
def get_post_templates():
    return jsonify([])  # Return empty list for now

@app.route('/api/schedule/templates', methods=['POST'])
@login_required
def create_post_template():
    return jsonify({'message': 'Template created', 'template_id': 1}), 201

@app.route('/api/schedule/analytics', methods=['GET'])
@login_required
def get_posting_analytics():
    return jsonify([])  # Return empty list for now

# ============ MODERATION RULES ENDPOINTS ============

@app.route('/api/moderate/rules', methods=['GET'])
@login_required
def get_moderation_rules():
    rules = ModerationRule.query.filter_by(is_active=True).all()
    
    return jsonify([{
        'id': rule.id,
        'rule_name': rule.rule_name,
        'rule_type': rule.rule_type,
        'pattern': rule.pattern,
        'action': rule.action,
        'severity': rule.severity
    } for rule in rules])

@app.route('/api/moderate/rules', methods=['POST'])
@login_required
def create_moderation_rule():
    data = request.json
    
    rule = ModerationRule(
        rule_name=data['rule_name'],
        rule_type=data['rule_type'],
        pattern=data['pattern'],
        action=data['action'],
        severity=data.get('severity', 1)
    )
    
    db.session.add(rule)
    db.session.commit()
    
    return jsonify({'message': 'Rule created', 'rule_id': rule.id}), 201

@app.route('/api/moderate/rules/<rule_id>', methods=['DELETE'])
@login_required
def delete_moderation_rule(rule_id):
    rule = ModerationRule.query.get(rule_id)
    
    if not rule:
        return jsonify({'error': 'Rule not found'}), 404
    
    rule.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Rule deleted'})

@app.route('/api/moderate/blocked-users', methods=['GET'])
@login_required
def get_blocked_users():
    blocked = BlockedUser.query.filter(
        db.or_(
            BlockedUser.expires_at.is_(None),
            BlockedUser.expires_at > datetime.utcnow()
        )
    ).all()
    
    return jsonify([{
        'id': b.id,
        'facebook_user_id': b.facebook_user_id,
        'user_name': b.user_name,
        'reason': b.reason,
        'blocked_at': b.blocked_at.isoformat(),
        'expires_at': b.expires_at.isoformat() if b.expires_at else None
    } for b in blocked])

@app.route('/api/moderate/blocked-users', methods=['POST'])
@login_required
def block_user():
    data = request.json
    
    blocked = BlockedUser(
        facebook_user_id=data['facebook_user_id'],
        user_name=data.get('user_name'),
        reason=data.get('reason'),
        blocked_by=current_user.id,
        expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
    )
    
    db.session.add(blocked)
    db.session.commit()
    
    return jsonify({'message': 'User blocked successfully'}), 201

# ============ WEBHOOK ============

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    if request.args.get('hub.verify_token') == Config.FACEBOOK_VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def webhook_receive():
    data = request.json
    
    log = WebhookLog(
        facebook_page_id=data.get('entry', [{}])[0].get('id'),
        event_type='feed',
        raw_payload=data,
        processed=False
    )
    db.session.add(log)
    db.session.commit()
    
    try:
        for entry in data.get('entry', []):
            page_id = entry.get('id')
            page = FacebookPage.query.filter_by(page_id=page_id).first()
            
            if not page:
                continue
            
            for change in entry.get('changes', []):
                if change.get('field') == 'feed':
                    value = change.get('value')
                    if 'post_id' in value:
                        # Process new post - simplified for webhook
                        fb_service = FacebookService(page.access_token)
                        post_data = fb_service.get_post_attachments(value['post_id'])
                        # Add to database logic here
                        pass
        
        log.processed = True
        db.session.commit()
        
    except Exception as e:
        log.error_message = str(e)
        db.session.commit()
    
    return 'OK', 200

# ============ STATIC FILES ============

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============ INITIALIZATION ============

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully")
        
        # Create default page if not exists
        if not FacebookPage.query.first():
            print("Creating default Facebook page entry...")
            page = FacebookPage(
                page_id=Config.FACEBOOK_PAGE_ID,
                page_name='Your Facebook Page',
                access_token=Config.FACEBOOK_PAGE_ACCESS_TOKEN,
                is_active=True
            )
            db.session.add(page)
            db.session.commit()
            
            # Perform initial sync of historical posts
            print("Starting initial sync of historical posts (this may take a while)...")
            perform_initial_sync(Config.FACEBOOK_PAGE_ID, Config.FACEBOOK_PAGE_ACCESS_TOKEN)
            print("Initial sync completed!")
        else:
            print("Facebook page already exists, skipping initial sync")
        
        # Create admin user if not exists
        if not User.query.filter_by(email='admin@example.com').first():
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print("  Email: admin@example.com")
            print("  Password: admin123")
        else:
            print("Admin user already exists")
    
    print("\n" + "="*50)
    print("🚀 Starting Flask Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📍 API Documentation: http://localhost:5000/api/posts")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)