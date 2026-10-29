import React, { useState, useEffect } from 'react'
import DatePicker from 'react-datepicker'
import { Calendar, Clock, Trash2, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PostScheduler() {
  const [scheduledPosts, setScheduledPosts] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    message: '',
    scheduled_time: new Date(),
    is_recurring: false,
    recurring_pattern: 'weekly'
  })

  useEffect(() => {
    fetchScheduledPosts()
  }, [])

  const fetchScheduledPosts = async () => {
    try {
      const response = await fetch('/api/schedule/posts')
      const data = await response.json()
      setScheduledPosts(data)
    } catch (error) {
      console.error('Error fetching scheduled posts:', error)
    }
  }

  const handleSchedule = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await fetch('/api/schedule/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        toast.success('Post scheduled successfully')
        setShowForm(false)
        setFormData({
          message: '',
          scheduled_time: new Date(),
          is_recurring: false,
          recurring_pattern: 'weekly'
        })
        fetchScheduledPosts()
      } else {
        toast.error('Failed to schedule post')
      }
    } catch (error) {
      toast.error('Failed to schedule post')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (postId) => {
    if (!confirm('Are you sure you want to cancel this scheduled post?')) return
    
    try {
      const response = await fetch(`/api/schedule/posts/${postId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        toast.success('Post cancelled')
        fetchScheduledPosts()
      } else {
        toast.error('Failed to cancel post')
      }
    } catch (error) {
      toast.error('Failed to cancel post')
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: 'bg-blue-100 text-blue-800',
      processing: 'bg-yellow-100 text-yellow-800',
      posted: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    }
    return badges[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Scheduled Posts</h2>
            <p className="text-gray-500 mt-1">Schedule posts to be published automatically</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn-primary"
          >
            + New Scheduled Post
          </button>
        </div>
      </div>
      
      {showForm && (
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Schedule a Post</h3>
          <form onSubmit={handleSchedule} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                value={formData.message}
                onChange={(e) => setFormData({...formData, message: e.target.value})}
                required
                rows={3}
                className="input-field"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Schedule Time</label>
              <DatePicker
                selected={formData.scheduled_time}
                onChange={(date) => setFormData({...formData, scheduled_time: date})}
                showTimeSelect
                minDate={new Date()}
                dateFormat="MMMM d, yyyy h:mm aa"
                className="input-field"
              />
            </div>
            
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_recurring}
                  onChange={(e) => setFormData({...formData, is_recurring: e.target.checked})}
                  className="rounded border-gray-300 text-facebook focus:ring-facebook"
                />
                <span className="text-sm text-gray-700">Recurring Post</span>
              </label>
              
              {formData.is_recurring && (
                <select
                  value={formData.recurring_pattern}
                  onChange={(e) => setFormData({...formData, recurring_pattern: e.target.value})}
                  className="input-field w-32"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              )}
            </div>
            
            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex-1"
              >
                {loading ? 'Scheduling...' : 'Schedule Post'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
      
      <div className="space-y-4">
        {scheduledPosts.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No scheduled posts</p>
          </div>
        ) : (
          scheduledPosts.map((post) => (
            <div key={post.id} className="bg-white rounded-xl shadow-md p-6">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${getStatusBadge(post.status)}`}>
                    {post.status}
                  </span>
                  <div className="flex items-center gap-2 mt-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    {new Date(post.scheduled_time).toLocaleString()}
                  </div>
                </div>
                {post.status === 'scheduled' && (
                  <button
                    onClick={() => handleCancel(post.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
              
              <p className="text-gray-800 mt-3">{post.message}</p>
              
              {post.is_recurring && (
                <div className="mt-3 text-xs text-gray-500">
                  🔄 Repeats {post.recurring_pattern}ly
                </div>
              )}
              
              {post.facebook_post_id && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <a
                    href={`https://facebook.com/${post.facebook_post_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-facebook text-sm hover:underline"
                  >
                    View on Facebook →
                  </a>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}