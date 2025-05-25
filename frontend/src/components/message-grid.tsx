'use client'

import { motion } from 'framer-motion'
import { Clock, User, Tag, Heart, MessageCircle } from 'lucide-react'
import { Message } from '@/types'
import { formatDate, getCategoryColor, getCategoryIcon } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface MessageGridProps {
  messages: Message[]
  isLoading: boolean
  error: Error | null
}

export function MessageGrid({ messages, isLoading, error }: MessageGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="glass border border-white/10 rounded-xl p-6 animate-pulse">
            <div className="space-y-4">
              <div className="h-4 bg-white/10 rounded w-3/4"></div>
              <div className="h-3 bg-white/10 rounded w-1/2"></div>
              <div className="h-20 bg-white/10 rounded"></div>
            </div>
          </div>
        ))}
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

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {messages.map((message, index) => (
        <motion.div
          key={message.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="glass border border-white/10 rounded-xl p-6 hover:border-purple-500/30 transition-all duration-300 group hover:scale-105"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-300 font-medium">{message.sender_name}</span>
            </div>
            <div className="flex items-center space-x-1 text-xs text-gray-400">
              <Clock className="w-3 h-3" />
              <span>{formatDate(message.timestamp)}</span>
            </div>
          </div>

          {/* Content */}
          <div className="mb-4">
            <p className="text-white leading-relaxed line-clamp-4">
              {message.content}
            </p>
          </div>

          {/* Summary */}
          {message.summary && message.summary !== message.content && (
            <div className="mb-4 p-3 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs text-purple-300 mb-1">AI Summary</div>
              <p className="text-sm text-gray-300">{message.summary}</p>
            </div>
          )}

          {/* Categories */}
          {message.categories.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {message.categories.map((category) => (
                <span
                  key={category}
                  className={cn(
                    "inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium",
                    `bg-gradient-to-r ${getCategoryColor(category)} text-white`
                  )}
                >
                  <span>{getCategoryIcon(category)}</span>
                  <span>{category.replace('-', ' ')}</span>
                </span>
              ))}
            </div>
          )}

          {/* Tags */}
          {message.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-4">
              {message.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center space-x-1 px-2 py-1 bg-white/10 rounded-full text-xs text-gray-300"
                >
                  <Tag className="w-3 h-3" />
                  <span>{tag}</span>
                </span>
              ))}
              {message.tags.length > 3 && (
                <span className="text-xs text-gray-400">+{message.tags.length - 3} more</span>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-white/10">
            <div className="flex items-center space-x-2">
              <Heart className={cn(
                "w-4 h-4",
                message.sentiment > 0.3 ? "text-green-400" :
                message.sentiment < -0.3 ? "text-red-400" : "text-gray-400"
              )} />
              <span className="text-xs text-gray-400">
                {message.sentiment > 0.3 ? 'Positive' :
                 message.sentiment < -0.3 ? 'Negative' : 'Neutral'}
              </span>
            </div>
            
            <div className="flex items-center space-x-2 text-xs text-gray-400">
              <span className={cn(
                "w-2 h-2 rounded-full",
                message.has_embedding ? "bg-green-400" : "bg-gray-400"
              )}></span>
              <span>{message.has_embedding ? 'Indexed' : 'Processing'}</span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )
} 