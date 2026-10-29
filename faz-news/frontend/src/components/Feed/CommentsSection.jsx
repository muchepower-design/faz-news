import React from 'react'
import { Heart } from 'lucide-react'

export default function CommentsSection({ comments }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="bg-gray-50 p-4 border-t border-gray-100">
      <h4 className="font-medium text-gray-900 mb-3">Comments</h4>
      <div className="space-y-3">
        {comments.map((comment, idx) => (
          <div key={comment.id || idx} className="flex gap-3">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex-shrink-0 flex items-center justify-center">
              <span className="text-xs font-bold text-gray-600">
                {comment.author?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1">
              <div className="bg-white rounded-lg p-2">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm">{comment.author}</span>
                  <span className="text-xs text-gray-500">{formatDate(comment.created_time)}</span>
                </div>
                <p className="text-sm text-gray-800">{comment.message}</p>
              </div>
              <div className="flex gap-4 mt-1 ml-2">
                <button className="text-xs text-gray-500 hover:text-facebook flex items-center gap-1">
                  <Heart className="w-3 h-3" /> Like
                </button>
                <button className="text-xs text-gray-500 hover:text-facebook">Reply</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}