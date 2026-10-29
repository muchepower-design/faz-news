import requests
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import FacebookPage, FacebookPost, PostAttachment
from config import Config

def get_all_media(post_id, access_token):
    """Get ALL media (images AND videos) for a post"""
    media_items = []
    
    # Method 1: Check attachments endpoint
    url = f"https://graph.facebook.com/v18.0/{post_id}/attachments"
    params = {"access_token": access_token}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'data' in data:
            for attachment in data['data']:
                media_type = attachment.get('type', 'unknown')
                
                # Get the media URL
                media_data = attachment.get('media', {})
                media_url = media_data.get('source', '')
                
                # Check for image in the attachment
                image_data = attachment.get('image', {})
                image_url = image_data.get('src', '')
                
                # Check for subattachments (multiple images in album)
                subattachments = attachment.get('subattachments', {}).get('data', [])
                
                if subattachments:
                    for sub in subattachments:
                        sub_media = sub.get('media', {})
                        sub_url = sub_media.get('source', '')
                        if sub_url:
                            media_items.append({
                                'type': sub.get('type', 'photo'),
                                'url': sub_url,
                                'thumbnail': sub.get('image', {}).get('src', '')
                            })
                elif media_url:
                    media_items.append({
                        'type': media_type,
                        'url': media_url,
                        'thumbnail': image_url
                    })
                elif image_url:
                    # This is an image without a media.source
                    media_items.append({
                        'type': 'photo',
                        'url': image_url,
                        'thumbnail': image_url
                    })
    except Exception as e:
        print(f"   Error in attachments: {e}")
    
    # Method 2: Check for full_picture field
    url2 = f"https://graph.facebook.com/v18.0/{post_id}"
    params2 = {
        "access_token": access_token,
        "fields": "full_picture,permalink_url"
    }
    
    try:
        response2 = requests.get(url2, params=params2)
        data2 = response2.json()
        
        if data2.get('full_picture'):
            # Check if we already have this URL
            existing_urls = [m['url'] for m in media_items]
            if data2['full_picture'] not in existing_urls:
                media_items.append({
                    'type': 'photo',
                    'url': data2['full_picture'],
                    'thumbnail': data2['full_picture']
                })
    except Exception as e:
        print(f"   Error in full_picture: {e}")
    
    return media_items

def fix_images():
    with app.app_context():
        print("="*60)
        print("FIXING IMAGES IN POSTS")
        print("="*60)
        
        # Get page and token
        page = FacebookPage.query.first()
        if not page:
            print("❌ No page found!")
            return
        
        access_token = page.access_token
        print(f"\n📌 Page: {page.page_name}")
        
        # Get all posts
        posts = FacebookPost.query.all()
        print(f"📊 Found {len(posts)} posts")
        
        updated_count = 0
        image_count = 0
        video_count = 0
        
        for idx, post in enumerate(posts, 1):
            print(f"\n[{idx}/{len(posts)}] Processing: {post.post_id[:30]}...")
            
            # Get existing attachments
            existing = PostAttachment.query.filter_by(post_id=post.id).all()
            existing_types = [a.media_type for a in existing]
            
            # Get fresh media from Facebook
            media_items = get_all_media(post.post_id, access_token)
            
            new_items = 0
            for media in media_items:
                # Check if we already have this URL
                url_exists = PostAttachment.query.filter_by(
                    post_id=post.id, 
                    url=media['url']
                ).first()
                
                if not url_exists:
                    attachment = PostAttachment(
                        post_id=post.id,
                        media_type=media['type'],
                        url=media['url'],
                        thumbnail_url=media.get('thumbnail', ''),
                        display_order=len(existing) + new_items
                    )
                    db.session.add(attachment)
                    new_items += 1
                    
                    if media['type'] == 'photo':
                        image_count += 1
                        post.has_images = True
                    elif media['type'] == 'video':
                        video_count += 1
                        post.has_videos = True
            
            if new_items > 0:
                updated_count += 1
                db.session.commit()
                print(f"   ✅ Added {new_items} new media items (Images: {len([m for m in media_items if m['type']=='photo'])}, Videos: {len([m for m in media_items if m['type']!='photo'])})")
            else:
                print(f"   📝 No new media found")
            
            # Rate limiting
            time.sleep(0.3)
        
        print("\n" + "="*60)
        print("✅ IMAGE FIX COMPLETE!")
        print("="*60)
        print(f"   Posts updated: {updated_count}")
        print(f"   Total images: {image_count}")
        print(f"   Total videos: {video_count}")
        print(f"   Posts with images: {FacebookPost.query.filter(FacebookPost.has_images == True).count()}")
        print(f"   Posts with videos: {FacebookPost.query.filter(FacebookPost.has_videos == True).count()}")
        print("="*60)

if __name__ == '__main__':
    fix_images()