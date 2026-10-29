import requests
from datetime import datetime
from app import app, db, FacebookPost, PostAttachment
from config import Config

def fetch_post_attachments(post_id, access_token):
    """Fetch attachments for a single post"""
    url = f"https://graph.facebook.com/v18.0/{post_id}/attachments"
    params = {
        "access_token": access_token,
        "limit": 10
    }
    
    attachments = []
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'data' in data:
            for attachment in data['data']:
                media_type = attachment.get('type', 'unknown')
                media_data = attachment.get('media', {})
                target = attachment.get('target', {})
                
                attachment_info = {
                    'type': 'photo' if media_type == 'photo' else 'video' if media_type == 'video' else 'other',
                    'url': media_data.get('source', '') or target.get('url', ''),
                    'thumbnail': attachment.get('image', {}).get('src', ''),
                    'title': attachment.get('title', '')
                }
                
                if attachment_info['url']:
                    attachments.append(attachment_info)
    except Exception as e:
        print(f"Error: {e}")
    
    return attachments

def update_all_posts_with_media():
    with app.app_context():
        print("="*60)
        print("UPDATING POSTS WITH IMAGES/VIDEOS")
        print("="*60)
        
        # Get page and token
        page = FacebookPage.query.first()
        if not page:
            print("No page found!")
            return
        
        access_token = page.access_token
        
        # Get all posts that don't have media tracked
        posts = FacebookPost.query.all()
        print(f"\n📊 Total posts to check: {len(posts)}")
        
        updated_count = 0
        photo_count = 0
        video_count = 0
        
        for i, post in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}] Checking post: {post.post_id}")
            
            # Check if post already has attachments
            existing_attachments = PostAttachment.query.filter_by(post_id=post.id).count()
            if existing_attachments > 0:
                print(f"   Already has {existing_attachments} attachments, skipping...")
                continue
            
            # Fetch attachments from Facebook
            attachments = fetch_post_attachments(post.post_id, access_token)
            
            if attachments:
                print(f"   Found {len(attachments)} attachment(s)")
                
                for idx, att in enumerate(attachments):
                    attachment = PostAttachment(
                        post_id=post.id,
                        attachment_id=f"{post.post_id}_{idx}",
                        media_type=att['type'],
                        url=att['url'],
                        thumbnail_url=att['thumbnail'],
                        display_order=idx
                    )
                    db.session.add(attachment)
                    
                    if att['type'] == 'photo':
                        photo_count += 1
                        post.has_images = True
                    elif att['type'] == 'video':
                        video_count += 1
                        post.has_videos = True
                
                updated_count += 1
                db.session.commit()
                print(f"   ✅ Updated post with {len(attachments)} media items")
            else:
                print(f"   No media attachments found")
        
        print("\n" + "="*60)
        print("✅ UPDATE COMPLETE!")
        print("="*60)
        print(f"   Posts updated: {updated_count}")
        print(f"   Total photos: {photo_count}")
        print(f"   Total videos: {video_count}")
        print("="*60)

if __name__ == '__main__':
    update_all_posts_with_media()