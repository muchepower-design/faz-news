import requests
from datetime import datetime
from app import app, db, FacebookPage, FacebookPost, PostAttachment
from config import Config

def full_resync_with_media():
    with app.app_context():
        print("="*60)
        print("FULL RESYNC WITH MEDIA")
        print("="*60)
        
        # Clear existing posts and attachments
        print("\n🗑️ Clearing existing data...")
        PostAttachment.query.delete()
        FacebookPost.query.delete()
        db.session.commit()
        print("   Cleared!")
        
        # Get page
        page = FacebookPage.query.first()
        if not page:
            page = FacebookPage(
                page_id=Config.FACEBOOK_PAGE_ID,
                page_name='Facebook Page',
                access_token=Config.FACEBOOK_PAGE_ACCESS_TOKEN,
                is_active=True
            )
            db.session.add(page)
            db.session.commit()
            print("   Page created!")
        
        access_token = page.access_token
        PAGE_ID = page.page_id
        
        print(f"\n📡 Fetching posts from Facebook...")
        
        # Fetch posts
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
        params = {
            "access_token": access_token,
            "fields": "id,message,created_time,type",
            "limit": 100
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
            return
        
        posts_data = data.get('data', [])
        print(f"📊 Found {len(posts_data)} posts")
        
        post_count = 0
        photo_count = 0
        video_count = 0
        
        for post_data in posts_data:
            # Create post
            created_time = datetime.fromisoformat(post_data['created_time'].replace('Z', '+00:00'))
            
            post = FacebookPost(
                post_id=post_data['id'],
                page_id=page.id,
                message=post_data.get('message', ''),
                post_type=post_data.get('type'),
                created_time=created_time,
                has_images=False,
                has_videos=False
            )
            db.session.add(post)
            db.session.flush()  # Get post ID without committing
            
            # Fetch attachments for this post
            att_url = f"https://graph.facebook.com/v18.0/{post_data['id']}/attachments"
            att_params = {"access_token": access_token}
            
            try:
                att_response = requests.get(att_url, params=att_params)
                att_data = att_response.json()
                
                if 'data' in att_data:
                    for idx, attachment in enumerate(att_data['data']):
                        media_type = attachment.get('type', 'unknown')
                        media_data = attachment.get('media', {})
                        
                        att_url_final = media_data.get('source', '')
                        
                        if att_url_final:
                            attachment_obj = PostAttachment(
                                post_id=post.id,
                                media_type='photo' if media_type == 'photo' else 'video',
                                url=att_url_final,
                                thumbnail_url=attachment.get('image', {}).get('src', ''),
                                display_order=idx
                            )
                            db.session.add(attachment_obj)
                            
                            if media_type == 'photo':
                                photo_count += 1
                                post.has_images = True
                            elif media_type == 'video':
                                video_count += 1
                                post.has_videos = True
            except Exception as e:
                print(f"   Error fetching media for {post_data['id']}: {e}")
            
            post_count += 1
            if post_count % 10 == 0:
                db.session.commit()
                print(f"   Synced {post_count} posts...")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ RESYNC COMPLETE!")
        print("="*60)
        print(f"   Total posts: {post_count}")
        print(f"   Total photos: {photo_count}")
        print(f"   Total videos: {video_count}")
        print("="*60)

if __name__ == '__main__':
    full_resync_with_media()