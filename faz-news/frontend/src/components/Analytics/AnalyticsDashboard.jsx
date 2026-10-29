import React, { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Download, Calendar } from 'lucide-react'

const COLORS = ['#1877f2', '#42b72a', '#f7b928', '#e41e3f', '#8b9dc3']

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null)
  const [period, setPeriod] = useState('30')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [period])

  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/analytics/dashboard?period=${period}`)
      const data = await response.json()
      setAnalytics(data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportData = () => {
    window.open(`/api/analytics/export?period=${period}`, '_blank')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-facebook"></div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8 text-center">
        <p className="text-gray-500">No analytics data available</p>
      </div>
    )
  }

  const pieData = Object.entries(analytics.post_type_breakdown || {}).map(([name, value]) => ({
    name: name.toUpperCase(),
    value: value
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
        <div className="flex gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="input-field w-32"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          <button onClick={exportData} className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="text-3xl font-bold text-facebook">{analytics.summary?.total_posts || 0}</div>
          <div className="text-sm text-gray-500 mt-1">Total Posts</div>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="text-3xl font-bold text-pink-500">{analytics.summary?.total_likes?.toLocaleString() || 0}</div>
          <div className="text-sm text-gray-500 mt-1">Total Likes</div>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="text-3xl font-bold text-green-500">{analytics.summary?.total_comments?.toLocaleString() || 0}</div>
          <div className="text-sm text-gray-500 mt-1">Total Comments</div>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="text-3xl font-bold text-yellow-500">{analytics.summary?.total_shares?.toLocaleString() || 0}</div>
          <div className="text-sm text-gray-500 mt-1">Total Shares</div>
        </div>
      </div>
      
      {/* Engagement Chart */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="font-semibold text-gray-800 mb-4">Engagement Over Time</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={analytics.time_series}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="likes" stroke="#1877f2" name="Likes" strokeWidth={2} />
            <Line type="monotone" dataKey="comments" stroke="#42b72a" name="Comments" strokeWidth={2} />
            <Line type="monotone" dataKey="shares" stroke="#f7b928" name="Shares" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Post Type Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-semibold text-gray-800 mb-4">Post Type Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* Top Posts */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-semibold text-gray-800 mb-4">Top Performing Posts</h3>
          <div className="space-y-3 max-h-[300px] overflow-y-auto">
            {analytics.top_posts?.slice(0, 5).map((post, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-medium text-facebook">#{idx + 1}</span>
                  <div className="flex gap-2 text-xs">
                    <span>❤️ {post.likes}</span>
                    <span>💬 {post.comments}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-700 line-clamp-2">{post.message || 'No caption'}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}