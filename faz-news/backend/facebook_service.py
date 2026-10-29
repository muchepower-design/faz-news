import requests
from datetime import datetime
from typing import List, Dict, Any
import time
import os

class FacebookService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_all_historical_posts(self, page_id: str, progress_callback=None) -> List[Dict]:
        """Fetch ALL past posts from a Facebook Page"""
        all_posts = []
        # Use /feed endpoint instead of /posts (more reliable)
        url = f"{self.base_url}/{page_id}/feed"
        params = {
            "access_token": self.access_token,
            "fields": "id,message,story,created_time,updated_time,permalink_url,type,likes.summary(true),comments.summary(true),shares,attachments",
            "limit": 100
        }
        
        page_count = 0
        while url:
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                if 'error' in data:
                    print(f"Facebook API error: {data['error'].get('message', 'Unknown')}")
                    break
                
                posts = data.get('data', [])
                all_posts.extend(posts)
                
                if progress_callback:
                    progress_callback(len(all_posts), len(posts))
                
                url = data.get('paging', {}).get('next')
                params = None
                page_count += 1
                
                # Rate limiting to avoid hitting API limits
                if page_count % 10 == 0:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error fetching posts: {e}")
                break
        
        return all_posts
    
    def get_post_attachments(self, post_id: str) -> List[Dict]:
        """Fetch all attachments for a post"""
        all_attachments = []
        url = f"{self.base_url}/{post_id}/attachments"
        params = {
            "access_token": self.access_token,
            "fields": "media_type,media,type,title,url,target,image",
            "limit": 50
        }
        
        while url:
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                for idx, attachment in enumerate(data.get('data', [])):
                    media = attachment.get('media', {})
                    attachment_data = {
                        'attachment_id': attachment.get('id'),
                        'media_type': attachment.get('media_type', 'unknown'),
                        'url': media.get('source') if media else attachment.get('url'),
                        'thumbnail_url': attachment.get('image', {}).get('src'),
                        'display_order': idx
                    }
                    
                    if attachment_data['media_type'] == 'video':
                        video_info = self.get_video_info(attachment.get('target', {}).get('id'))
                        attachment_data['video_duration'] = video_info.get('duration')
                        attachment_data['video_status'] = video_info.get('status')
                    
                    all_attachments.append(attachment_data)
                
                url = data.get('paging', {}).get('next')
                params = None
                
            except Exception as e:
                print(f"Error fetching attachments: {e}")
                break
        
        return all_attachments
    
    def get_video_info(self, video_id: str) -> Dict:
        """Get video information"""
        if not video_id:
            return {}
        
        url = f"{self.base_url}/{video_id}"
        params = {
            "access_token": self.access_token,
            "fields": "duration,status,length,live_status"
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except:
            return {}
    
    def get_live_video_status(self, live_video_id: str) -> Dict:
        """Get current status of a live video"""
        url = f"{self.base_url}/{live_video_id}"
        params = {
            "access_token": self.access_token,
            "fields": "status,permalink_url,embed_html,stream_url,broadcast_start_time"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            return {
                'status': data.get('status'),
                'stream_url': data.get('stream_url'),
                'embed_html': data.get('embed_html'),
                'start_time': data.get('broadcast_start_time')
            }
        except Exception as e:
            print(f"Error getting live video status: {e}")
            return {}
    
    def get_post_comments(self, post_id: str, limit: int = 100) -> List[Dict]:
        """Get all comments for a post"""
        all_comments = []
        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "access_token": self.access_token,
            "fields": "id,message,from,created_time,like_count,comment_count,parent",
            "limit": limit
        }
        
        while url:
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                for comment in data.get('data', []):
                    comment_data = {
                        'comment_id': comment.get('id'),
                        'message': comment.get('message'),
                        'author_name': comment.get('from', {}).get('name'),
                        'author_id': comment.get('from', {}).get('id'),
                        'created_time': comment.get('created_time'),
                        'like_count': comment.get('like_count', 0),
                        'parent_comment_id': comment.get('parent', {}).get('id') if comment.get('parent') else None
                    }
                    all_comments.append(comment_data)
                
                url = data.get('paging', {}).get('next')
                params = None
                
            except Exception as e:
                print(f"Error fetching comments: {e}")
                break
        
        return all_comments
    
    # ============ POSTING METHODS ============
    
    def publish_text_post(self, page_id: str, message: str) -> dict:
        """Publish a text post to Facebook"""
        url = f"{self.base_url}/{page_id}/feed"
        
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(url, data=payload)
            result = response.json()
            
            if 'id' in result:
                return {
                    'success': True,
                    'post_id': result['id'],
                    'permalink': f"https://facebook.com/{result['id']}"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Unknown error')
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def publish_photo_post(self, page_id: str, image_url: str, caption: str = None) -> dict:
        """Publish a photo post to Facebook"""
        # First, download the image
        try:
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                return {'success': False, 'error': 'Failed to download image'}
        except Exception as e:
            return {'success': False, 'error': f'Error downloading image: {str(e)}'}
        
        # Upload photo (published=False means just upload, don't post yet)
        upload_url = f"{self.base_url}/{page_id}/photos"
        files = {'source': image_response.content}
        upload_params = {
            'access_token': self.access_token,
            'published': False
        }
        
        try:
            upload_response = requests.post(upload_url, files=files, data=upload_params)
            upload_result = upload_response.json()
            
            if 'id' not in upload_result:
                return {'success': False, 'error': 'Failed to upload image'}
            
            # Create post with the uploaded photo
            post_url = f"{self.base_url}/{page_id}/feed"
            post_payload = {
                'attached_media[0]': f'{{"media_fbid":"{upload_result["id"]}"}}',
                'access_token': self.access_token
            }
            
            if caption:
                post_payload['message'] = caption
            
            post_response = requests.post(post_url, data=post_payload)
            post_result = post_response.json()
            
            if 'id' in post_result:
                return {
                    'success': True,
                    'post_id': post_result['id'],
                    'permalink': f"https://facebook.com/{post_result['id']}"
                }
            else:
                return {'success': False, 'error': post_result.get('error', {}).get('message', 'Unknown error')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def publish_link_post(self, page_id: str, link_url: str, message: str = None) -> dict:
        """Publish a link post to Facebook"""
        url = f"{self.base_url}/{page_id}/feed"
        
        payload = {
            "link": link_url,
            "access_token": self.access_token
        }
        
        if message:
            payload["message"] = message
        
        try:
            response = requests.post(url, data=payload)
            result = response.json()
            
            if 'id' in result:
                return {
                    'success': True,
                    'post_id': result['id'],
                    'permalink': f"https://facebook.com/{result['id']}"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Unknown error')
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def publish_video_post(self, page_id: str, video_url: str, title: str = None, description: str = None) -> dict:
        """Publish a video post to Facebook"""
        url = f"{self.base_url}/{page_id}/videos"
        
        # Download video from URL
        try:
            video_response = requests.get(video_url)
            if video_response.status_code != 200:
                return {'success': False, 'error': 'Failed to download video'}
        except Exception as e:
            return {'success': False, 'error': f'Error downloading video: {str(e)}'}
        
        files = {
            'source': video_response.content
        }
        
        data = {
            'access_token': self.access_token,
            'title': title or 'Video Post',
            'description': description or ''
        }
        
        try:
            response = requests.post(url, files=files, data=data)
            result = response.json()
            
            if 'id' in result:
                return {
                    'success': True,
                    'post_id': result['id'],
                    'permalink': f"https://facebook.com/{result['id']}"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Unknown error')
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_post_attachments_simple(self, post_id: str) -> List[Dict]:
        """Fetch attachments (images/videos) for a specific post"""
        url = f"{self.base_url}/{post_id}/attachments"
        params = {
            "access_token": self.access_token,
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
                    
                    attachment_info = {
                        'type': 'photo' if media_type == 'photo' else 'video' if media_type == 'video' else 'other',
                        'url': media_data.get('source', ''),
                        'thumbnail': attachment.get('image', {}).get('src', ''),
                        'title': attachment.get('title', '')
                    }
                    
                    if attachment_info['url']:
                        attachments.append(attachment_info)
        except Exception as e:
            print(f"Error fetching attachments for {post_id}: {e}")
        
        return attachments