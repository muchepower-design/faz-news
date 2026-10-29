import React, { useState, useRef } from 'react'
import { Image, Link as LinkIcon, Send, Save, X, Upload, Video } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PostCreator() {
  const [postType, setPostType] = useState('text')
  const [message, setMessage] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [imagePreview, setImagePreview] = useState('')
  const [videoUrl, setVideoUrl] = useState('')
  const [videoPreview, setVideoPreview] = useState('')
  const [videoFile, setVideoFile] = useState(null)
  const [linkUrl, setLinkUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [characterCount, setCharacterCount] = useState(0)
  const fileInputRef = useRef(null)
  const videoInputRef = useRef(null)
  
  const MAX_CHARS = 63206

  const handleMessageChange = (e) => {
    const text = e.target.value
    if (text.length <= MAX_CHARS) {
      setMessage(text)
      setCharacterCount(text.length)
    }
  }

  const handleImageUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file')
      return
    }
    
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image must be less than 10MB')
      return
    }
    
    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result)
    }
    reader.readAsDataURL(file)
    
    const formData = new FormData()
    formData.append('image', file)
    
    try {
      const response = await fetch('/api/upload/image', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      setImageUrl(data.url)
      toast.success('Image uploaded')
    } catch (error) {
      toast.error('Failed to upload image')
    }
  }

  const handleVideoUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    if (!file.type.startsWith('video/')) {
      toast.error('Please upload a video file')
      return
    }
    
    if (file.size > 100 * 1024 * 1024) {
      toast.error('Video must be less than 100MB')
      return
    }
    
    setVideoFile(file)
    
    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setVideoPreview(reader.result)
    }
    reader.readAsDataURL(file)
    
    // Upload video
    const formData = new FormData()
    formData.append('video', file)
    
    try {
      const xhr = new XMLHttpRequest()
      xhr.open('POST', '/api/upload/video')
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded * 100) / event.total)
          setUploadProgress(percent)
        }
      }
      xhr.onload = () => {
        if (xhr.status === 200) {
          const data = JSON.parse(xhr.response)
          setVideoUrl(data.url)
          toast.success('Video uploaded')
          setUploadProgress(0)
        } else {
          toast.error('Failed to upload video')
        }
      }
      xhr.send(formData)
    } catch (error) {
      toast.error('Failed to upload video')
      setUploadProgress(0)
    }
  }

  const handlePublish = async () => {
    if (!message.trim() && postType !== 'photo' && postType !== 'video') {
      toast.error('Please enter a message')
      return
    }
    
    setLoading(true)
    
    try {
      let response
      
      switch (postType) {
        case 'text':
          response = await fetch('/api/publish/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
          })
          break
          
        case 'photo':
          if (!imageUrl) {
            toast.error('Please upload an image')
            setLoading(false)
            return
          }
          response = await fetch('/api/publish/photo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_url: imageUrl, caption: message })
          })
          break
          
        case 'video':
          if (!videoUrl) {
            toast.error('Please upload a video')
            setLoading(false)
            return
          }
          response = await fetch('/api/publish/video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_url: videoUrl, title: message, description: message })
          })
          break
          
        case 'link':
          if (!linkUrl) {
            toast.error('Please enter a link URL')
            setLoading(false)
            return
          }
          response = await fetch('/api/publish/link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link_url: linkUrl, message })
          })
          break
      }
      
      const data = await response.json()
      console.log('Publish response:', data);
      
      if (data.success) {
        toast.success('Post published successfully!')
        setMessage('')
        setImageUrl('')
        setImagePreview('')
        setVideoUrl('')
        setVideoPreview('')
        setVideoFile(null)
        setLinkUrl('')
        setCharacterCount(0)
      } else {
        toast.error(data.error || 'Failed to publish')
      }
    } catch (error) {
      toast.error('Failed to publish post')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveDraft = async () => {
    if (!message.trim() && !imageUrl && !videoUrl && !linkUrl) {
      toast.error('Nothing to save')
      return
    }
    
    try {
      await fetch('/api/drafts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          media_urls: imageUrl ? [imageUrl] : videoUrl ? [videoUrl] : [],
          link_url: linkUrl,
          media_type: postType === 'video' ? 'video' : 'image'
        })
      })
      toast.success('Draft saved')
    } catch (error) {
      toast.error('Failed to save draft')
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">Create a Post</h2>
        </div>
        
        {/* Post Type Selector */}
        <div className="flex border-b border-gray-200">
          <button
            className={`flex-1 py-3 text-center font-medium transition-colors ${
              postType === 'text'
                ? 'text-facebook border-b-2 border-facebook'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setPostType('text')}
          >
            📝 Text
          </button>
          <button
            className={`flex-1 py-3 text-center font-medium transition-colors ${
              postType === 'photo'
                ? 'text-facebook border-b-2 border-facebook'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setPostType('photo')}
          >
            🖼️ Photo
          </button>
          <button
            className={`flex-1 py-3 text-center font-medium transition-colors ${
              postType === 'video'
                ? 'text-facebook border-b-2 border-facebook'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setPostType('video')}
          >
            🎥 Video
          </button>
          <button
            className={`flex-1 py-3 text-center font-medium transition-colors ${
              postType === 'link'
                ? 'text-facebook border-b-2 border-facebook'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setPostType('link')}
          >
            🔗 Link
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Message Input */}
          <div>
            <textarea
              placeholder="What's on your mind?"
              value={message}
              onChange={handleMessageChange}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-facebook focus:border-transparent resize-none"
            />
            <div className="text-right text-xs text-gray-500 mt-1">
              {characterCount} / {MAX_CHARS} characters
            </div>
          </div>
          
          {/* Photo Upload */}
          {postType === 'photo' && (
            <div>
              {imagePreview ? (
                <div className="relative inline-block">
                  <img src={imagePreview} alt="Preview" className="max-w-full max-h-64 rounded-lg" />
                  <button
                    onClick={() => {
                      setImagePreview('')
                      setImageUrl('')
                    }}
                    className="absolute top-2 right-2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div
                  onClick={() => fileInputRef.current.click()}
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-facebook transition-colors"
                >
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Click to upload an image</p>
                  <p className="text-xs text-gray-400 mt-1">PNG, JPG, GIF up to 10MB</p>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleImageUpload}
                    accept="image/*"
                    className="hidden"
                  />
                </div>
              )}
            </div>
          )}
          
          {/* Video Upload */}
          {postType === 'video' && (
            <div>
              {videoPreview ? (
                <div className="relative">
                  <video src={videoPreview} className="max-w-full max-h-64 rounded-lg" controls />
                  <button
                    onClick={() => {
                      setVideoPreview('')
                      setVideoUrl('')
                      setVideoFile(null)
                    }}
                    className="absolute top-2 right-2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  {uploadProgress > 0 && uploadProgress < 100 && (
                    <div className="mt-2">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-facebook rounded-full h-2 transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1 text-center">{uploadProgress}% uploaded</p>
                    </div>
                  )}
                </div>
              ) : (
                <div
                  onClick={() => videoInputRef.current.click()}
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-facebook transition-colors"
                >
                  <Video className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Click to upload a video</p>
                  <p className="text-xs text-gray-400 mt-1">MP4, MOV, AVI up to 100MB</p>
                  <input
                    type="file"
                    ref={videoInputRef}
                    onChange={handleVideoUpload}
                    accept="video/*"
                    className="hidden"
                  />
                </div>
              )}
            </div>
          )}
          
          {/* Link Input */}
          {postType === 'link' && (
            <div>
              <input
                type="url"
                placeholder="https://example.com"
                value={linkUrl}
                onChange={(e) => setLinkUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-facebook focus:border-transparent"
              />
            </div>
          )}
        </div>
        
        {/* Actions */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 flex gap-3">
          <button
            onClick={handleSaveDraft}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors flex items-center justify-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save Draft
          </button>
          <button
            onClick={handlePublish}
            disabled={loading || (postType === 'photo' && !imageUrl) || (postType === 'video' && !videoUrl)}
            className="flex-1 bg-facebook text-white px-4 py-2 rounded-lg hover:bg-facebook-dark transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Send className="w-4 h-4" />
            )}
            Publish to Facebook
          </button>
        </div>
      </div>
    </div>
  )
}