from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

# ============ AUTHENTICATION MODELS ============

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='viewer')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserPageAccess(db.Model):
    __tablename__ = 'user_page_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_pages.id'))
    access_level = db.Column(db.String(20), default='view')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============ FACEBOOK DATA MODELS ============

class FacebookPage(db.Model):
    __tablename__ = 'facebook_pages'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(100), unique=True, nullable=False)
    page_name = db.Column(db.String(255))
    access_token = db.Column(db.Text, nullable=False)
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    last_synced_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    posts = db.relationship('FacebookPost', backref='page', lazy='dynamic')
    scheduled_posts = db.relationship('ScheduledPost', backref='page', lazy='dynamic')

class FacebookPost(db.Model):
    __tablename__ = 'facebook_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(100), unique=True, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_pages.id'))
    
    message = db.Column(db.Text)
    story = db.Column(db.Text)
    permalink_url = db.Column(db.String(500))
    post_type = db.Column(db.String(50))
    
    has_images = db.Column(db.Boolean, default=False)
    has_videos = db.Column(db.Boolean, default=False)
    has_live_video = db.Column(db.Boolean, default=False)
    live_video_id = db.Column(db.String(100))
    
    created_time = db.Column(db.DateTime, nullable=False)
    updated_time = db.Column(db.DateTime)
    
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    is_from_backfill = db.Column(db.Boolean, default=False)
    synced_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    attachments = db.relationship('PostAttachment', backref='post', lazy='dynamic')
    comments = db.relationship('FacebookComment', backref='post', lazy='dynamic')

class PostAttachment(db.Model):
    __tablename__ = 'post_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('facebook_posts.id', ondelete='CASCADE'))
    attachment_id = db.Column(db.String(100))
    media_type = db.Column(db.String(20))
    url = db.Column(db.Text)
    thumbnail_url = db.Column(db.Text)
    video_duration = db.Column(db.Integer)
    video_status = db.Column(db.String(20))
    display_order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FacebookComment(db.Model):
    __tablename__ = 'facebook_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.String(100), unique=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('facebook_posts.id', ondelete='CASCADE'))
    parent_comment_id = db.Column(db.String(100))
    
    message = db.Column(db.Text)
    author_name = db.Column(db.String(255))
    author_id = db.Column(db.String(100))
    
    created_time = db.Column(db.DateTime, nullable=False)
    like_count = db.Column(db.Integer, default=0)
    is_hidden = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============ COMMENT MODERATION MODELS ============

class CommentModerationQueue(db.Model):
    __tablename__ = 'comment_moderation_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.String(100), db.ForeignKey('facebook_comments.comment_id'))
    status = db.Column(db.String(20), default='pending')
    moderation_reason = db.Column(db.Text)
    moderated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    moderated_at = db.Column(db.DateTime)
    
    contains_profanity = db.Column(db.Boolean, default=False)
    contains_spam = db.Column(db.Boolean, default=False)
    contains_links = db.Column(db.Boolean, default=False)
    spam_score = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comment = db.relationship('FacebookComment', backref='moderation_queue')
    moderator = db.relationship('User', backref='moderated_comments')

class ModerationRule(db.Model):
    __tablename__ = 'moderation_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False)
    rule_type = db.Column(db.String(20))
    pattern = db.Column(db.Text, nullable=False)
    action = db.Column(db.String(20))
    severity = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlockedUser(db.Model):
    __tablename__ = 'blocked_users'
    
    id = db.Column(db.Integer, primary_key=True)
    facebook_user_id = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(255))
    reason = db.Column(db.Text)
    blocked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

# ============ SCHEDULED POSTING MODELS ============

class ScheduledPost(db.Model):
    __tablename__ = 'scheduled_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_pages.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    message = db.Column(db.Text)
    media_urls = db.Column(db.ARRAY(db.String))
    link_url = db.Column(db.String(500))
    
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    retry_count = db.Column(db.Integer, default=0)
    last_error = db.Column(db.Text)
    
    facebook_post_id = db.Column(db.String(100))
    posted_at = db.Column(db.DateTime)
    
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_pattern = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', backref='scheduled_posts')

class PostDraft(db.Model):
    __tablename__ = 'post_drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_pages.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    message = db.Column(db.Text)
    media_urls = db.Column(db.ARRAY(db.String))
    link_url = db.Column(db.String(500))
    
    status = db.Column(db.String(20), default='draft')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PublishingHistory(db.Model):
    __tablename__ = 'publishing_history'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_pages.id'))
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    draft_id = db.Column(db.Integer, db.ForeignKey('post_drafts.id'))
    
    message = db.Column(db.Text)
    media_urls = db.Column(db.ARRAY(db.String))
    link_url = db.Column(db.String(500))
    
    facebook_post_id = db.Column(db.String(100))
    facebook_permalink = db.Column(db.String(500))
    
    status = db.Column(db.String(20))
    error_message = db.Column(db.Text)
    
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============ ANALYTICS & LOGGING ============

class AnalyticsCache(db.Model):
    __tablename__ = 'analytics_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('facebook_pages.id'))
    cache_key = db.Column(db.String(100))
    cache_data = db.Column(db.JSON)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.String(100))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WebhookLog(db.Model):
    __tablename__ = 'webhook_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    facebook_page_id = db.Column(db.String(100))
    event_type = db.Column(db.String(50))
    raw_payload = db.Column(db.JSON)
    processed = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)