import React, { useState, useEffect } from 'react'
import { CheckCircle, XCircle, AlertTriangle, Flag } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CommentModeration() {
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPendingComments()
  }, [])

  const fetchPendingComments = async () => {
    try {
      const response = await fetch('/api/moderate/comments/pending')
      const data = await response.json()
      setComments(data.comments)
    } catch (error) {
      console.error('Error fetching comments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (commentId) => {
    try {
      const response = await fetch(`/api/moderate/comments/${commentId}/approve`, {
        method: 'POST'
      })
      if (response.ok) {
        toast.success('Comment approved')
        fetchPendingComments()
      }
    } catch (error) {
      toast.error('Failed to approve comment')
    }
  }

  const handleReject = async (commentId) => {
    const reason = prompt('Reason for rejection:')
    if (!reason) return
    
    try {
      const response = await fetch(`/api/moderate/comments/${commentId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      })
      if (response.ok) {
        toast.success('Comment rejected')
        fetchPendingComments()
      }
    } catch (error) {
      toast.error('Failed to reject comment')
    }
  }

  const getSpamScoreColor = (score) => {
    if (score >= 5) return 'bg-red-100 text-red-800'
    if (score >= 3) return 'bg-yellow-100 text-yellow-800'
    return 'bg-green-100 text-green-800'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-facebook"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Comment Moderation</h2>
        <p className="text-gray-500">Review and moderate comments from your Facebook page</p>
      </div>
      
      {comments.length === 0 ? (
        <div className="bg-white rounded-xl shadow-md p-12 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">All Clear!</h3>
          <p className="text-gray-500">No comments pending moderation</p>
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.queue_id} className="bg-white rounded-xl shadow-md p-6">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900">{comment.author}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(comment.created_time).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-gray-700">{comment.message}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(comment.comment_id)}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Approve"
                  >
                    <CheckCircle className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleReject(comment.comment_id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Reject"
                  >
                    <XCircle className="w-5 h-5" />
                  </button>
                </div>
              </div>
              
              {/* Moderation Flags */}
              <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-gray-100">
                {comment.moderation_flags.contains_profanity && (
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-red-100 text-red-700 rounded">
                    <AlertTriangle className="w-3 h-3" />
                    Profanity
                  </span>
                )}
                {comment.moderation_flags.contains_spam && (
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded">
                    <Flag className="w-3 h-3" />
                    Spam
                  </span>
                )}
                {comment.moderation_flags.contains_links && (
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                    🔗 Links
                  </span>
                )}
                {comment.moderation_flags.spam_score > 0 && (
                  <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded ${getSpamScoreColor(comment.moderation_flags.spam_score)}`}>
                    Spam Score: {comment.moderation_flags.spam_score}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}