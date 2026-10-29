import React from 'react'
import { useAuth } from '../../context/AuthContext'
import { Menu, LogOut, Bell, User } from 'lucide-react'

export default function Header({ sidebarOpen, setSidebarOpen, stats }) {
  const { user, logout } = useAuth()

  return (
    <header className="fixed top-0 right-0 left-0 bg-white shadow-md z-30">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-facebook">Facebook Integration</h1>
            {stats && (
              <div className="flex gap-4 text-xs text-gray-500 mt-1">
                <span>📊 {stats.total_posts} posts</span>
                <span>💬 {stats.total_comments} comments</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <button className="p-2 rounded-lg hover:bg-gray-100 relative">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-facebook rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium">{user?.username}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <LogOut className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}