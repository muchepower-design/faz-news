import React, { useState } from 'react'
import { ChevronLeft, ChevronRight, X, Play, Maximize2 } from 'lucide-react'
import ReactPlayer from 'react-player'

export default function MediaGallery({ attachments, postId }) {
  const [lightboxOpen, setLightboxOpen] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [playingVideo, setPlayingVideo] = useState(null)
  
  // Separate photos and videos
  const photos = attachments.filter(att => att.type === 'photo')
  const videos = attachments.filter(att => att.type === 'video')
  
  // For grid display, show max 4 images
  const displayPhotos = photos.slice(0, 4)
  const remainingCount = photos.length - 4
  
  const openLightbox = (index) => {
    setCurrentIndex(index)
    setLightboxOpen(true)
  }
  
  const nextImage = () => {
    if (photos.length > 0) {
      setCurrentIndex((currentIndex + 1) % photos.length)
    }
  }
  
  const prevImage = () => {
    if (photos.length > 0) {
      setCurrentIndex((currentIndex - 1 + photos.length) % photos.length)
    }
  }
  
  const closeLightbox = () => {
    setLightboxOpen(false)
    setPlayingVideo(null)
  }
  
  // Helper to get grid class based on number of images
  const getGridClass = () => {
    const count = displayPhotos.length
    if (count === 1) return 'grid-cols-1'
    if (count === 2) return 'grid-cols-2'
    if (count === 3 || count === 4) return 'grid-cols-2'
    return 'grid-cols-2'
  }
  
  // Helper for row span (first image larger when 3 images)
  const getImageSpan = (index, total) => {
    if (total === 3 && index === 0) return 'row-span-2'
    return ''
  }
  
  // Handle video click
  const playVideo = (videoUrl, index) => {
    setPlayingVideo(videoUrl)
    setCurrentIndex(index)
    setLightboxOpen(true)
  }
  
  return (
    <div className="px-4 pb-2">
      {/* Videos Section */}
      {videos.length > 0 && (
        <div className="mb-2 space-y-2">
          {videos.slice(0, 1).map((video, idx) => (
            <div
              key={`video-${idx}`}
              className="relative bg-black rounded-lg overflow-hidden cursor-pointer group"
              onClick={() => playVideo(video.url, idx)}
            >
              {video.thumbnail ? (
                <img
                  src={video.thumbnail}
                  alt="Video thumbnail"
                  className="w-full aspect-video object-cover"
                />
              ) : (
                <div className="w-full aspect-video bg-gray-800 flex items-center justify-center">
                  <Play className="w-16 h-16 text-white opacity-50" />
                </div>
              )}
              <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                <div className="w-16 h-16 bg-white/90 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Play className="w-8 h-8 text-facebook ml-1" />
                </div>
              </div>
              {video.duration && (
                <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                  {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
                </div>
              )}
            </div>
          ))}
          {videos.length > 1 && (
            <div className="text-xs text-gray-500">
              +{videos.length - 1} more video{videos.length > 2 ? 's' : ''}
            </div>
          )}
        </div>
      )}
      
      {/* Photos Grid */}
      {photos.length === 1 && (
        <div className="rounded-lg overflow-hidden cursor-pointer" onClick={() => openLightbox(0)}>
          <img
            src={displayPhotos[0].url}
            alt="Post media"
            className="w-full max-h-[500px] object-cover hover:opacity-95 transition-opacity"
          />
        </div>
      )}
      
      {photos.length === 2 && (
        <div className="grid grid-cols-2 gap-0.5 rounded-lg overflow-hidden">
          {displayPhotos.map((photo, idx) => (
            <div key={idx} className="cursor-pointer aspect-square" onClick={() => openLightbox(idx)}>
              <img
                src={photo.url}
                alt={`Media ${idx + 1}`}
                className="w-full h-full object-cover hover:opacity-95 transition-opacity"
              />
            </div>
          ))}
        </div>
      )}
      
      {photos.length === 3 && (
        <div className="grid grid-cols-2 gap-0.5 rounded-lg overflow-hidden">
          <div className="row-span-2 cursor-pointer aspect-square" onClick={() => openLightbox(0)}>
            <img
              src={displayPhotos[0].url}
              alt="Media 1"
              className="w-full h-full object-cover hover:opacity-95 transition-opacity"
            />
          </div>
          <div className="cursor-pointer aspect-square" onClick={() => openLightbox(1)}>
            <img
              src={displayPhotos[1].url}
              alt="Media 2"
              className="w-full h-full object-cover hover:opacity-95 transition-opacity"
            />
          </div>
          <div className="cursor-pointer aspect-square" onClick={() => openLightbox(2)}>
            <img
              src={displayPhotos[2].url}
              alt="Media 3"
              className="w-full h-full object-cover hover:opacity-95 transition-opacity"
            />
          </div>
        </div>
      )}
      
      {photos.length >= 4 && (
        <div className="grid grid-cols-2 gap-0.5 rounded-lg overflow-hidden">
          {displayPhotos.map((photo, idx) => (
            <div
              key={idx}
              className="relative cursor-pointer aspect-square"
              onClick={() => openLightbox(idx)}
            >
              <img
                src={photo.url}
                alt={`Media ${idx + 1}`}
                className="w-full h-full object-cover hover:opacity-95 transition-opacity"
              />
              {idx === 3 && remainingCount > 0 && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                  <span className="text-white font-bold text-2xl">+{remainingCount}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {/* Lightbox Modal */}
      {lightboxOpen && (
        <div className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center" onClick={closeLightbox}>
          {/* Close button */}
          <button
            onClick={closeLightbox}
            className="absolute top-4 right-4 text-white hover:text-gray-300 transition-colors z-10"
          >
            <X className="w-8 h-8" />
          </button>
          
          {/* Navigation buttons (only for photos) */}
          {photos.length > 1 && !playingVideo && (
            <>
              <button
                onClick={(e) => { e.stopPropagation(); prevImage(); }}
                className="absolute left-4 text-white hover:text-gray-300 transition-colors z-10"
              >
                <ChevronLeft className="w-12 h-12" />
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); nextImage(); }}
                className="absolute right-4 text-white hover:text-gray-300 transition-colors z-10"
              >
                <ChevronRight className="w-12 h-12" />
              </button>
            </>
          )}
          
          {/* Content */}
          <div className="max-w-[90vw] max-h-[90vh] flex items-center justify-center" onClick={(e) => e.stopPropagation()}>
            {playingVideo ? (
              <div className="w-[80vw] h-[70vh]">
                <ReactPlayer
                  url={playingVideo}
                  playing={true}
                  controls={true}
                  width="100%"
                  height="100%"
                  config={{
                    file: {
                      attributes: {
                        controlsList: 'nodownload'
                      }
                    }
                  }}
                />
              </div>
            ) : (
              <img
                src={photos[currentIndex]?.url}
                alt="Full size"
                className="max-w-[90vw] max-h-[90vh] object-contain"
              />
            )}
          </div>
          
          {/* Counter */}
          {photos.length > 1 && !playingVideo && (
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-white text-sm bg-black/50 px-3 py-1 rounded-full">
              {currentIndex + 1} / {photos.length}
            </div>
          )}
        </div>
      )}
    </div>
  )
}