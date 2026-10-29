import React, { useState, useEffect } from 'react'
import ReactPlayer from 'react-player'
import { RefreshCw, AlertCircle } from 'lucide-react'

export default function LiveVideo() {
  const [liveStatus, setLiveStatus] = useState(null)
  const [isLive, setIsLive] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchLiveStatus()
    const interval = setInterval(fetchLiveStatus, 15000)
    return () => clearInterval(interval)
  }, [])

  const fetchLiveStatus = async () => {
    try {
      const response = await fetch('/api/live-video')
      const data = await response.json()
      setLiveStatus(data)
      setIsLive(data.live)
      setError(null)
    } catch (err) {
      setError('Failed to fetch live status')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-facebook"></div>
      </div>
    )
  }

  if (!isLive || !liveStatus) {
    return (
      <div className="bg-white rounded-xl shadow-md p-12 text-center">
        <div className="text-6xl mb-4">📺</div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">No Live Stream</h3>
        <p className="text-gray-500">There's currently no live video streaming</p>
        <button
          onClick={fetchLiveStatus}
          className="mt-6 btn-secondary flex items-center gap-2 mx-auto"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="bg-red-500 text-white px-4 py-2 flex items-center gap-2">
        <span className="animate-pulse">🔴</span>
        <span className="font-semibold">LIVE NOW</span>
      </div>
      
      <div className="aspect-video bg-black">
        {liveStatus.stream_url ? (
          <ReactPlayer
            url={liveStatus.stream_url}
            playing={true}
            controls={true}
            width="100%"
            height="100%"
            config={{
              facebook: {
                appId: import.meta.env.VITE_FACEBOOK_APP_ID
              }
            }}
          />
        ) : liveStatus.embed_html ? (
          <div dangerouslySetInnerHTML={{ __html: liveStatus.embed_html }} />
        ) : (
          <div className="flex items-center justify-center h-full">
            <AlertCircle className="w-12 h-12 text-gray-500" />
          </div>
        )}
      </div>
      
      {liveStatus.message && (
        <div className="p-4 border-t border-gray-100">
          <h3 className="font-semibold text-gray-900 mb-1">Live Stream</h3>
          <p className="text-gray-600">{liveStatus.message}</p>
        </div>
      )}
    </div>
  )
}