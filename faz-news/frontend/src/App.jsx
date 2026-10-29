import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster, toast } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import Header from './components/Layout/Header'
import Sidebar from './components/Layout/Sidebar'
import ProtectedRoute from './components/Layout/ProtectedRoute'
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'
import FacebookFeed from './components/Feed/FacebookFeed'
import LiveVideo from './components/Live/LiveVideo'
import AnalyticsDashboard from './components/Analytics/AnalyticsDashboard'
import CommentModeration from './components/Moderation/CommentModeration'
import PostScheduler from './components/Scheduling/PostScheduler'
import PostCreator from './components/Publishing/PostCreator'

function AppContent() {
  const { user, isAuthenticated, loading } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    if (isAuthenticated) {
      fetchStats()
    }
  }, [isAuthenticated])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-facebook"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} stats={stats} />
      <Sidebar sidebarOpen={sidebarOpen} userRole={user?.role} />
      
      <main className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'} pt-16`}>
        <div className="p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/feed" />} />
            <Route path="/feed" element={<FacebookFeed />} />
            <Route path="/live" element={<LiveVideo />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route 
              path="/moderation" 
              element={
                <ProtectedRoute allowedRoles={['moderator', 'admin']}>
                  <CommentModeration />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/scheduler" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <PostScheduler />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/create" 
              element={
                <ProtectedRoute allowedRoles={['moderator', 'admin']}>
                  <PostCreator />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </div>
      </main>
      
      <Toaster position="top-right" />
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App