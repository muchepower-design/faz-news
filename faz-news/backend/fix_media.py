import requests
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all necessary models
from app import app, db
from models import FacebookPage, FacebookPost, PostAttachment
from config import Config

def fetch_post_attachments(post_id, access_token):
    """Fetch attachments for a single post"""
    url = f"https://graph.facebook.com/v18.0/{post_id}/attachments"
    params = {
        "access_token": access_token
    }
    
    attachments = []
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'data' in data:
            for attachment in data['data']:
                # Get the media URL
                media_data = attachment.get('media', {})
                media_source = media_data.get('source', '')
                
                # Also check subattachments for multiple images
                subattachments = attachment.get('subattachments', {}).get('data', [])
                
                if media_source:
                    # Single media
                    attachments.append({
                        'type': attachment.get('type', 'unknown'),
                        'url': media_source,
                        'thumbnail': attachment.get('image', {}).get('src', '')
                    })
                elif subattachments:
                    # Multiple images in album
                    for sub in subattachments:
                        sub_media = sub.get('media', {})
                        sub_source = sub_media.get('source', '')
                        if sub_source:
                            attachments.append({
                                'type': 'photo',
                                'url': sub_source,
                                'thumbnail': sub.get('image', {}).get('src', '')
                            })
    except Exception as e:
        pass  # Silent fail for missing attachments
    
    return attachments

def fix_media():
    with app.app_context():
        print("="*60)
        print("FIXING POSTS WITH MEDIA ATTACHMENTS")
        print("="*60)
        
        # Get page and token
        page = FacebookPage.query.first()
        if not page:
            print("❌ No page found in database!")
            return
        
        access_token = page.access_token
        print(f"\n📌 Page: {page.page_name}")
        print(f"📌 Token: {access_token[:30]}...")
        
        # Get all posts
        posts = FacebookPost.query.all()
        print(f"\n📊 Found {len(posts)} posts to check")
        
        updated_count = 0
        total_photos = 0
        total_videos = 0
        
        for idx, post in enumerate(posts, 1):
            print(f"\n[{idx}/{len(posts)}] Checking post: {post.post_id[:20]}...")
            
            # Skip if already has attachments
            existing = PostAttachment.query.filter_by(post_id=post.id).count()
            if existing > 0:
                print(f"   ⏭️ Already has {existing} attachments, skipping")
                continue
            
            # Fetch attachments
            attachments = fetch_post_attachments(post.post_id, access_token)
            
            if attachments:
                print(f"   📎 Found {len(attachments)} attachment(s)")
                
                for att_idx, att in enumerate(attachments):
                    media_type = 'photo' if att['type'] == 'photo' else 'video'
                    
                    attachment = PostAttachment(
                        post_id=post.id,
                        media_type=media_type,
                        url=att['url'],
                        thumbnail_url=att['thumbnail'],
                        display_order=att_idx
                    )
                    db.session.add(attachment)
                    
                    if media_type == 'photo':
                        total_photos += 1
                        post.has_images = True
                    else:
                        total_videos += 1
                        post.has_videos = True
                
                updated_count += 1
                db.session.commit()
                print(f"   ✅ Updated! Photos: {len([a for a in attachments if a['type']=='photo'])}, Videos: {len([a for a in attachments if a['type']!='photo'])}")
            else:
                print(f"   📝 No media attachments")
        
        print("\n" + "="*60)
        print("✅ MEDIA UPDATE COMPLETE!")
        print("="*60)
        print(f"   Posts updated: {updated_count}")
        print(f"   Total photos: {total_photos}")
        print(f"   Total videos: {total_videos}")
        print(f"   Posts with images: {FacebookPost.query.filter(FacebookPost.has_images == True).count()}")
        print(f"   Posts with videos: {FacebookPost.query.filter(FacebookPost.has_videos == True).count()}")
        print("="*60)

if __name__ == '__main__':
    fix_media()