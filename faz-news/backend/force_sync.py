import requests
from datetime import datetime
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import FacebookPage, FacebookPost
from config import Config

def update_metrics():
    with app.app_context():
        print("="*60)
        print("UPDATING POSTS WITH LIKES, COMMENTS, SHARES")
        print("="*60)
        
        # Get page and token
        page = FacebookPage.query.first()
        if not page:
            print("❌ No page found!")
            return
        
        access_token = page.access_token
        PAGE_ID = page.page_id
        
        print(f"\n📌 Page: {page.page_name}")
        print(f"📌 Token: {access_token[:30]}...")
        
        # IMPORTANT: NO deprecated fields - ONLY basic metrics
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
        params = {
            "access_token": access_token,
            # Only these fields - NO attachments!
            "fields": "id,likes.limit(0).summary(true),comments.limit(0).summary(true),shares",
            "limit": 100
        }
        
        print(f"\n📡 Fetching engagement metrics...")
        print(f"URL: {url}")
        
        updated_count = 0
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                print(f"❌ API Error: {data['error'].get('message')}")
                print(f"   Code: {data['error'].get('code')}")
                return
            
            posts_data = data.get('data', [])
            print(f"✅ Found {len(posts_data)} posts")
            
            for post_data in posts_data:
                # Get metrics
                likes = post_data.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = post_data.get('comments', {}).get('summary', {}).get('total_count', 0)
                shares = post_data.get('shares', {}).get('count', 0)
                
                # Find post in database
                post = FacebookPost.query.filter_by(post_id=post_data['id']).first()
                
                if post:
                    # Update metrics
                    post.like_count = likes
                    post.comment_count = comments
                    post.share_count = shares
                    updated_count += 1
                    
                    if updated_count <= 10:  # Show first 10 updates
                        print(f"   📊 {post.post_id[:20]}... | 👍 {likes} | 💬 {comments} | 🔄 {shares}")
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ UPDATE COMPLETE!")
            print("="*60)
            print(f"   Posts updated: {updated_count}")
            
            # Show sample of updated metrics
            print("\n📊 Updated posts with metrics:")
            sample_posts = FacebookPost.query.order_by(FacebookPost.created_time.desc()).limit(5).all()
            for post in sample_posts:
                msg = post.message[:50] if post.message else 'No text'
                print(f"   - {msg}...")
                print(f"     ❤️ {post.like_count} | 💬 {post.comment_count} | 🔄 {post.share_count}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    update_metrics()