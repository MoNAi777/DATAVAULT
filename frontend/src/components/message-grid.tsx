'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Clock, User, Tag, MessageCircle, Bot, Smartphone, MessageSquare, Calendar, TrendingUp, ChevronDown, ChevronUp, ExternalLink, X, Copy, Share2, Download } from 'lucide-react'
import { Message } from '@/types'
import { getCategoryColor, getCategoryIcon } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface MessageGridProps {
  messages: Message[]
  isLoading: boolean
  error: Error | null
}

// Helper function to convert URLs in text to clickable links
const linkifyText = (text: string) => {
  // More robust regex to match URLs including most protocols and formats
  const urlRegex = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/g
  
  // Split text by URLs
  const parts = text.split(urlRegex)
  
  // Find all URLs in the text
  const urls = text.match(urlRegex) || []
  
  // Build result with text and link components
  const result: React.ReactNode[] = []
  
  parts.forEach((part, i) => {
    // Add the text part
    if (part) {
      result.push(part)
    }
    
    // Add the URL part (if exists)
    if (urls[i]) {
      // Ensure URL has proper protocol for href
      const url = urls[i].startsWith('http') ? urls[i] : `https://${urls[i]}`
      const displayUrl = urls[i].length > 30 ? `${urls[i].substring(0, 27)}...` : urls[i]
      
      result.push(
        <a 
          key={i} 
          href={url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-400 hover:underline inline-flex items-center"
          onClick={(e) => e.stopPropagation()}
        >
          {displayUrl}
          <ExternalLink className="w-3 h-3 ml-1" />
        </a>
      )
    }
  })
  
  return result
}

const getSourceIcon = (sourceType: string) => {
  switch (sourceType) {
    case 'telegram':
      return <MessageSquare className="w-4 h-4 text-blue-400" />
    case 'whatsapp':
      return <MessageCircle className="w-4 h-4 text-green-400" />
    default:
      return <Smartphone className="w-4 h-4 text-gray-400" />
  }
}

const getSentimentColor = (sentiment: number) => {
  if (sentiment > 0.3) return 'text-green-400 bg-green-400/10'
  if (sentiment < -0.3) return 'text-red-400 bg-red-400/10'
  return 'text-yellow-400 bg-yellow-400/10'
}

const getSentimentLabel = (sentiment: number) => {
  if (sentiment > 0.3) return 'Positive'
  if (sentiment < -0.3) return 'Negative'
  return 'Neutral'
}

// Message Modal Component
const MessageModal = ({ message, onClose }: { message: Message | null, onClose: () => void }) => {
  if (!message) return null;
  
  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gray-900 rounded-2xl border border-white/10 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-gray-900/95 backdrop-blur-sm border-b border-white/10 p-4 flex justify-between items-center">
            <div className="flex items-center space-x-3">
              {getSourceIcon(message.source_type)}
              <h3 className="text-lg font-semibold text-white">
                Message from {message.sender_name}
              </h3>
            </div>
            <div className="flex space-x-2">
              <button 
                onClick={() => navigator.clipboard.writeText(message.content)}
                className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white"
                title="Copy message"
              >
                <Copy size={18} />
              </button>
              <button 
                onClick={() => {
                  const blob = new Blob([message.content], { type: 'text/plain' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `message-${message.id}.txt`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                }}
                className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white"
                title="Download as text"
              >
                <Download size={18} />
              </button>
              <button 
                onClick={onClose} 
                className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white"
                title="Close"
              >
                <X size={18} />
              </button>
            </div>
          </div>
          
          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Message Info */}
            <div className="bg-gray-800/50 rounded-xl p-4 flex flex-wrap gap-4">
              <div>
                <div className="text-xs text-gray-400 mb-1">Sender</div>
                <div className="text-white font-medium flex items-center">
                  <User className="w-4 h-4 mr-2 text-gray-400" />
                  {message.sender_name}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Source</div>
                <div className="text-white font-medium flex items-center">
                  {getSourceIcon(message.source_type)}
                  <span className="ml-2 capitalize">{message.source_type}</span>
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Time</div>
                <div className="text-white font-medium flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-gray-400" />
                  {new Date(message.timestamp).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Sentiment</div>
                <div className={cn(
                  "flex items-center px-2 py-1 rounded-full text-xs",
                  getSentimentColor(message.sentiment)
                )}>
                  <TrendingUp className="w-3 h-3 mr-1" />
                  {getSentimentLabel(message.sentiment)}
                </div>
              </div>
            </div>
            
            {/* Message Content */}
            <div className="bg-gray-800/30 rounded-xl p-6">
              <h4 className="text-sm text-gray-400 mb-3 flex items-center">
                <MessageSquare className="w-4 h-4 mr-2" /> 
                Message Content
              </h4>
              <div className="text-white text-base leading-relaxed whitespace-pre-wrap">
                {linkifyText(message.content)}
              </div>
            </div>
            
            {/* AI Summary */}
            {message.summary && message.summary !== message.content && (
              <div className="bg-gradient-to-r from-purple-500/20 to-blue-500/10 rounded-xl p-6">
                <h4 className="text-sm text-purple-300 mb-3 flex items-center">
                  <Bot className="w-4 h-4 mr-2" /> 
                  AI Summary
                </h4>
                <div className="text-gray-200 text-base leading-relaxed">
                  {linkifyText(message.summary)}
                </div>
              </div>
            )}
            
            {/* Categories & Tags */}
            <div className="flex flex-col md:flex-row gap-6">
              {/* Categories */}
              {message.categories.length > 0 && (
                <div className="flex-1">
                  <h4 className="text-sm text-gray-400 mb-3">Categories</h4>
                  <div className="flex flex-wrap gap-2">
                    {message.categories.map((category) => (
                      <span
                        key={category}
                        className={cn(
                          "inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm",
                          `bg-gradient-to-r ${getCategoryColor(category)} text-white`
                        )}
                      >
                        <span className="text-xs">{getCategoryIcon(category)}</span>
                        <span>{category.replace('-', ' ')}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Tags */}
              {message.tags.length > 0 && (
                <div className="flex-1">
                  <h4 className="text-sm text-gray-400 mb-3">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {message.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center space-x-1 px-3 py-1 bg-white/10 rounded-full text-sm text-gray-300"
                      >
                        <Tag className="w-3 h-3" />
                        <span>{tag}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export function MessageGrid({ messages, isLoading, error }: MessageGridProps) {
  const [expandedMessages, setExpandedMessages] = useState<Set<number>>(new Set())
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)

  const toggleMessageExpansion = (id: number) => {
    setExpandedMessages(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="glass border border-white/10 rounded-xl p-5 animate-pulse">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <div className="h-4 bg-white/10 rounded w-24"></div>
                  <div className="h-3 bg-white/10 rounded w-16"></div>
                </div>
                <div className="h-3 bg-white/10 rounded w-20"></div>
                <div className="space-y-2">
                  <div className="h-3 bg-white/10 rounded"></div>
                  <div className="h-3 bg-white/10 rounded w-4/5"></div>
                  <div className="h-3 bg-white/10 rounded w-3/5"></div>
                </div>
                <div className="flex gap-2">
                  <div className="h-6 bg-white/10 rounded-full w-16"></div>
                  <div className="h-6 bg-white/10 rounded-full w-20"></div>
                </div>
              </div>
            </div>
          ))}
          </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass border border-red-500/20 rounded-xl p-8 text-center">
        <div className="text-red-400 text-lg font-medium mb-2">Failed to load messages</div>
        <div className="text-gray-400">Please check your connection and try again</div>
      </div>
    )
  }

  if (messages.length === 0) {
    return (
      <div className="glass border border-white/10 rounded-xl p-12 text-center">
        <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <div className="text-xl font-medium text-white mb-2">No messages found</div>
        <div className="text-gray-400">Try adjusting your search or category filter</div>
      </div>
    )
  }

  // Group messages by date for better organization
  const groupedMessages = messages.reduce((groups: { [key: string]: Message[] }, message) => {
    const date = new Date(message.timestamp).toDateString()
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(message)
    return groups
  }, {})

  return (
    <div className="space-y-8">
      {/* Modal for full message view */}
      {selectedMessage && (
        <MessageModal 
          message={selectedMessage} 
          onClose={() => setSelectedMessage(null)} 
        />
      )}
      
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="glass border border-white/10 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-white">{messages.length}</div>
          <div className="text-sm text-gray-400">Total Messages</div>
        </div>
        <div className="glass border border-white/10 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400">
            {messages.filter(m => m.source_type === 'whatsapp').length}
          </div>
          <div className="text-sm text-gray-400">WhatsApp</div>
        </div>
        <div className="glass border border-white/10 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">
            {messages.filter(m => m.source_type === 'telegram').length}
          </div>
          <div className="text-sm text-gray-400">Telegram</div>
        </div>
        <div className="glass border border-white/10 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-400">
            {messages.filter(m => m.has_embedding).length}
          </div>
          <div className="text-sm text-gray-400">AI Processed</div>
        </div>
      </div>

      {/* Messages grouped by date */}
      {Object.entries(groupedMessages)
        .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
        .map(([date, dateMessages]) => (
          <div key={date} className="space-y-4">
            {/* Date Header */}
            <div className="flex items-center space-x-3 mb-4">
              <Calendar className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">
                {new Date(date).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </h3>
              <div className="flex-1 h-px bg-gradient-to-r from-purple-500/50 to-transparent"></div>
              <span className="text-sm text-gray-400">{dateMessages.length} messages</span>
            </div>

            {/* Messages Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {dateMessages.map((message, index) => (
        <motion.div
          key={message.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="glass border border-white/10 rounded-xl p-5 hover:border-purple-500/30 transition-all duration-300 group hover:scale-[1.02] hover:shadow-xl cursor-pointer"
                  onClick={() => setSelectedMessage(message)}
        >
                  {/* Header with Source and Time */}
                  <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
                      {getSourceIcon(message.source_type)}
                      <span className="text-xs font-medium text-gray-300 capitalize">
                        {message.source_type}
                      </span>
            </div>
            <div className="flex items-center space-x-1 text-xs text-gray-400">
              <Clock className="w-3 h-3" />
                      <span>{new Date(message.timestamp).toLocaleTimeString('en-US', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}</span>
            </div>
          </div>

                  {/* Sender */}
                  <div className="flex items-center space-x-2 mb-3">
                    <User className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-white truncate">
                      {message.sender_name}
                    </span>
                  </div>

          {/* Content */}
          <div className="mb-4">
                    <p className={cn(
                      "text-gray-200 text-sm leading-relaxed",
                      !expandedMessages.has(message.id) && "line-clamp-3"
                    )}>
              {linkifyText(message.content)}
            </p>
            {message.content.length > 150 && (
              <button 
                onClick={(e) => {
                  e.stopPropagation(); // Prevent opening modal when clicking the expand button
                  toggleMessageExpansion(message.id);
                }}
                className="flex items-center text-xs text-purple-400 hover:text-purple-300 mt-2"
              >
                {expandedMessages.has(message.id) ? (
                  <>
                    <ChevronUp className="w-3 h-3 mr-1" />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3 mr-1" />
                    Show more
                  </>
                )}
              </button>
            )}
          </div>

                  {/* AI Summary */}
          {message.summary && message.summary !== message.content && (
                    <div className="mb-4 p-3 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-500/20">
                      <div className="flex items-center space-x-1 mb-1">
                        <Bot className="w-3 h-3 text-purple-400" />
                        <span className="text-xs font-medium text-purple-300">AI Summary</span>
                      </div>
                      <p className={cn(
                        "text-xs text-gray-300",
                        !expandedMessages.has(message.id * -1) && "line-clamp-2"
                      )}>
                        {linkifyText(message.summary)}
                      </p>
                      {message.summary.length > 100 && (
                        <button 
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent opening modal when clicking the expand button
                            toggleMessageExpansion(message.id * -1);
                          }}
                          className="flex items-center text-xs text-purple-400 hover:text-purple-300 mt-1"
                        >
                          {expandedMessages.has(message.id * -1) ? (
                            <>
                              <ChevronUp className="w-3 h-3 mr-1" />
                              Show less
                            </>
                          ) : (
                            <>
                              <ChevronDown className="w-3 h-3 mr-1" />
                              Show more
                            </>
                          )}
                        </button>
                      )}
            </div>
          )}

          {/* Categories */}
          {message.categories.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {message.categories.slice(0, 2).map((category) => (
                <span
                  key={category}
                  className={cn(
                    "inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium",
                    `bg-gradient-to-r ${getCategoryColor(category)} text-white`
                  )}
                >
                          <span className="text-xs">{getCategoryIcon(category)}</span>
                  <span>{category.replace('-', ' ')}</span>
                </span>
              ))}
                      {message.categories.length > 2 && (
                        <span className="text-xs text-gray-400 px-2 py-1">
                          +{message.categories.length - 2}
                        </span>
                      )}
            </div>
          )}

          {/* Tags */}
          {message.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {message.tags.slice(0, 2).map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center space-x-1 px-2 py-1 bg-white/10 rounded-full text-xs text-gray-300"
                >
                          <Tag className="w-2 h-2" />
                          <span className="truncate max-w-16">{tag}</span>
                </span>
              ))}
                      {message.tags.length > 2 && (
                        <span className="text-xs text-gray-400 px-2 py-1">
                          +{message.tags.length - 2}
                        </span>
              )}
            </div>
          )}

                  {/* Footer with Sentiment and Status */}
                  <div className="flex items-center justify-between pt-3 border-t border-white/10">
            <div className="flex items-center space-x-2">
                      <div className={cn(
                        "flex items-center space-x-1 px-2 py-1 rounded-full text-xs",
                        getSentimentColor(message.sentiment)
                      )}>
                        <TrendingUp className="w-3 h-3" />
                        <span>{getSentimentLabel(message.sentiment)}</span>
                      </div>
            </div>
            
                    <div className="flex items-center space-x-1">
                      <div className={cn(
                "w-2 h-2 rounded-full",
                        message.has_embedding ? "bg-green-400" : "bg-yellow-400"
                      )}></div>
                      <span className="text-xs text-gray-400">
                        {message.has_embedding ? 'Indexed' : 'Processing'}
                      </span>
            </div>
          </div>
        </motion.div>
              ))}
            </div>
          </div>
      ))}
    </div>
  )
} 