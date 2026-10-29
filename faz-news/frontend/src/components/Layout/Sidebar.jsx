import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Tv, 
  BarChart3, 
  Shield, 
  Calendar, 
  PenSquare,
  Home
} from 'lucide-react'

export default function Sidebar({ sidebarOpen, userRole }) {
  const navItems = [
    { path: '/feed', icon: Home, label: 'Feed', roles: ['viewer', 'moderator', 'admin'] },
    { path: '/live', icon: Tv, label: 'Live Video', roles: ['viewer', 'moderator', 'admin'] },
    { path: '/analytics', icon: BarChart3, label: 'Analytics', roles: ['viewer', 'moderator', 'admin'] },
    { path: '/moderation', icon: Shield, label: 'Moderation', roles: ['moderator', 'admin'] },
    { path: '/scheduler', icon: Calendar, label: 'Scheduler', roles: ['admin'] },
    { path: '/create', icon: PenSquare, label: 'Create Post', roles: ['moderator', 'admin'] },
  ]

  const filteredNav = navItems.filter(item => item.roles.includes(userRole))

  return (
    <aside className={`fixed left-0 top-0 h-full bg-white shadow-lg transition-all duration-300 z-20 pt-16 ${sidebarOpen ? 'w-64' : 'w-20'}`}>
      <nav className="mt-6">
        {filteredNav.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 mx-2 rounded-lg transition-colors ${
                isActive
                  ? 'bg-facebook text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}