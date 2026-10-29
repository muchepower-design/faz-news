import React, { useState } from 'react'
import { Heart, MessageCircle, Share2, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'
import MediaGallery from './MediaGallery'

export default function PostCard({ post }) {
  const [expanded, setExpanded] = useState(false)
  const [liked, setLiked] = useState(false)
  const [likesCount, setLikesCount] = useState(post.metrics?.likes || 0)
  const [showComments, setShowComments] = useState(false)
  
  const MAX_TEXT_LENGTH = 200
  
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }
  
  const getPostTypeIcon = () => {
    if (post.media?.has_videos) return '🎥'
    if (post.media?.has_images) return '📷'
    return '📝'
  }
  
  const truncateText = (text) => {
    if (!text) return ''
    if (text.length <= MAX_TEXT_LENGTH || expanded) return text
    return text.substring(0, MAX_TEXT_LENGTH) + '...'
  }
  
  const handleLike = () => {
    if (liked) {
      setLikesCount(likesCount - 1)
    } else {
      setLikesCount(likesCount + 1)
    }
    setLiked(!liked)
  }
  
  const message = post.message || ''
  const needsTruncation = message.length > MAX_TEXT_LENGTH
  
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200">
      {/* Post Header */}
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div className="w-10 h-10 bg-gradient-to-br from-facebook to-facebook-dark rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-sm">FB</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900 hover:underline cursor-pointer">
                  Facebook Page
                </h3>
                <span className="text-xs text-gray-500">{getPostTypeIcon()}</span>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <span>{formatDate(post.created_time)}</span>
                <span>•</span>
                <span>🌍 Public</span>
              </div>
            </div>
          </div>
          
          {post.permalink_url && (
            <a
              href={post.permalink_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-facebook transition-colors p-1"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
      
      {/* Post Message */}
      {message && (
        <div className="px-4 pb-3">
          <p className="text-gray-800 whitespace-pre-wrap break-words leading-relaxed">
            {truncateText(message)}
          </p>
          {needsTruncation && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-1 text-facebook text-sm font-medium hover:underline flex items-center gap-1"
            >
              {expanded ? (
                <>
                  <ChevronUp className="w-4 h-4" />
                  See less
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4" />
                  See more
                </>
              )}
            </button>
          )}
        </div>
      )}
      
      {/* Media Gallery */}
      {post.media?.attachments && post.media.attachments.length > 0 && (
        <MediaGallery attachments={post.media.attachments} postId={post.id} />
      )}
      
      {/* Live Badge */}
      {post.media?.has_live_video && (
        <div className="px-4 pb-2">
          <div className="inline-flex items-center gap-1 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
            <span className="animate-pulse">🔴</span>
            LIVE NOW
          </div>
        </div>
      )}
      
      {/* Post Stats */}
      <div className="px-4 py-2 border-t border-gray-100">
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-1">
            <span>❤️</span>
            <span>{likesCount.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <span>💬</span>
            <span>{(post.metrics?.comments || 0).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <span>🔄</span>
            <span>{(post.metrics?.shares || 0).toLocaleString()}</span>
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex border-t border-gray-100">
        <button
          onClick={handleLike}
          className={`flex-1 flex items-center justify-center gap-2 py-2 font-medium transition-colors ${
            liked ? 'text-facebook' : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          <Heart className={`w-5 h-5 ${liked ? 'fill-current' : ''}`} />
          Like
        </button>
        <button
          onClick={() => setShowComments(!showComments)}
          className="flex-1 flex items-center justify-center gap-2 py-2 text-gray-600 hover:bg-gray-50 transition-colors font-medium"
        >
          <MessageCircle className="w-5 h-5" />
          Comment
        </button>
        <button className="flex-1 flex items-center justify-center gap-2 py-2 text-gray-600 hover:bg-gray-50 transition-colors font-medium">
          <Share2 className="w-5 h-5" />
          Share
        </button>
      </div>
      
      {/* Comments Section */}
      {showComments && post.comments && post.comments.length > 0 && (
        <div className="bg-gray-50 p-4 border-t border-gray-100">
          <h4 className="font-medium text-gray-900 mb-3">Comments</h4>
          <div className="space-y-3">
            {post.comments.slice(0, 5).map((comment, idx) => (
              <div key={comment.id || idx} className="flex gap-2">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex-shrink-0 flex items-center justify-center">
                  <span className="text-xs font-bold text-gray-600">
                    {comment.author?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="bg-white rounded-lg p-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-sm">{comment.author}</span>
                      <span className="text-xs text-gray-500">
                        {formatDate(comment.created_time)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-800 break-words">{comment.message}</p>
                  </div>
                </div>
              </div>
            ))}
            {post.metrics?.comments > 5 && (
              <button className="text-facebook text-sm font-medium hover:underline">
                View all {post.metrics.comments} comments
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}