-- Run this to initialize database
CREATE DATABASE IF NOT EXISTS facebook_feed;

-- Main tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facebook_pages (
    id SERIAL PRIMARY KEY,
    page_id VARCHAR(100) UNIQUE NOT NULL,
    page_name VARCHAR(255),
    access_token TEXT NOT NULL,
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facebook_posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) UNIQUE NOT NULL,
    page_id INTEGER REFERENCES facebook_pages(id),
    message TEXT,
    story TEXT,
    permalink_url VARCHAR(500),
    post_type VARCHAR(50),
    has_images BOOLEAN DEFAULT false,
    has_videos BOOLEAN DEFAULT false,
    has_live_video BOOLEAN DEFAULT false,
    live_video_id VARCHAR(100),
    created_time TIMESTAMP NOT NULL,
    updated_time TIMESTAMP,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    is_from_backfill BOOLEAN DEFAULT false,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS post_attachments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES facebook_posts(id) ON DELETE CASCADE,
    attachment_id VARCHAR(100),
    media_type VARCHAR(20),
    url TEXT,
    thumbnail_url TEXT,
    video_duration INTEGER,
    video_status VARCHAR(20),
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facebook_comments (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(100) UNIQUE NOT NULL,
    post_id INTEGER REFERENCES facebook_posts(id) ON DELETE CASCADE,
    parent_comment_id VARCHAR(100),
    message TEXT,
    author_name VARCHAR(255),
    author_id VARCHAR(100),
    created_time TIMESTAMP NOT NULL,
    like_count INTEGER DEFAULT 0,
    is_hidden BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_posts_created_time ON facebook_posts(created_time);
CREATE INDEX idx_posts_page_id ON facebook_posts(page_id);
CREATE INDEX idx_comments_post_id ON facebook_comments(post_id);
CREATE INDEX idx_attachments_post_id ON post_attachments(post_id);