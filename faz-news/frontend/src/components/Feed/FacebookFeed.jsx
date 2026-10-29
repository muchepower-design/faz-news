import React, { useState, useEffect } from 'react'
import InfiniteScroll from 'react-infinite-scroll-component'
import { useAuth } from '../../context/AuthContext'
import PostCard from './PostCard'
import DateRangePicker from '../Search/DateRangePicker'
import { Filter, Loader2 } from 'lucide-react'

export default function FacebookFeed() {
  const [posts, setPosts] = useState([])
  const [hasMore, setHasMore] = useState(true)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [showFilters, setShowFilters] = useState(false)
  const [dateRange, setDateRange] = useState({ start: null, end: null })
  const [searchQuery, setSearchQuery] = useState('')
  
  const LIMIT = 20

  useEffect(() => {
    fetchPosts(true)
  }, [dateRange, searchQuery])

  const fetchPosts = async (reset = false) => {
    if (loading) return
    
    setLoading(true)
    const currentOffset = reset ? 0 : offset
    
    try {
      let url = `/api/posts?limit=${LIMIT}&offset=${currentOffset}`
      
      if (dateRange.start) {
        url += `&start_date=${dateRange.start.toISOString()}`
      }
      if (dateRange.end) {
        url += `&end_date=${dateRange.end.toISOString()}`
      }
      if (searchQuery) {
        url += `&q=${encodeURIComponent(searchQuery)}`
      }
      
      const response = await fetch(url)
      const data = await response.json()
      
      if (reset) {
        setPosts(data.posts)
      } else {
        setPosts([...posts, ...data.posts])
      }
      
      setTotal(data.total)
      setOffset(currentOffset + LIMIT)
      setHasMore(posts.length + data.posts.length < data.total)
    } catch (error) {
      console.error('Error fetching posts:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Search and Filter Bar */}
      <div className="bg-white rounded-xl shadow-md p-4 mb-6">
        <div className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search posts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-facebook focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 transition-colors"
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>
        
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <DateRangePicker onRangeChange={setDateRange} />
          </div>
        )}
      </div>
      
      {/* Posts Feed */}
      <InfiniteScroll
        dataLength={posts.length}
        next={() => fetchPosts(false)}
        hasMore={hasMore}
        loader={
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-facebook mx-auto" />
          </div>
        }
        endMessage={
          <div className="text-center py-8 text-gray-500">
            🎉 You've seen all posts!
          </div>
        }
      >
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      </InfiniteScroll>
      
      {posts.length === 0 && !loading && (
        <div className="text-center py-12 bg-white rounded-xl">
          <p className="text-gray-500">No posts found</p>
        </div>
      )}
    </div>
  )
}