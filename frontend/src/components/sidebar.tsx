'use client'

import { useMemo } from 'react'
import { Filter, Hash } from 'lucide-react'
import { Message } from '@/types'
import { getCategoryColor, getCategoryIcon } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface SidebarProps {
  messages: Message[]
  selectedCategory: string
  setSelectedCategory: (category: string) => void
}

export function Sidebar({ messages, selectedCategory, setSelectedCategory }: SidebarProps) {
  const categoryStats = useMemo(() => {
    const stats = new Map<string, { count: number; sentiment: number }>()
    
    messages.forEach(message => {
      if (message.categories.length === 0) {
        const uncategorized = stats.get('uncategorized') || { count: 0, sentiment: 0 }
        stats.set('uncategorized', {
          count: uncategorized.count + 1,
          sentiment: uncategorized.sentiment + message.sentiment
        })
      } else {
        message.categories.forEach(category => {
          const existing = stats.get(category) || { count: 0, sentiment: 0 }
          stats.set(category, {
            count: existing.count + 1,
            sentiment: existing.sentiment + message.sentiment
          })
        })
      }
    })

    return Array.from(stats.entries()).map(([category, data]) => ({
      category,
      count: data.count,
      sentiment: data.count > 0 ? data.sentiment / data.count : 0
    })).sort((a, b) => b.count - a.count)
  }, [messages])

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 glass-dark border-r border-white/10 p-6 overflow-y-auto">
      <div className="space-y-6">
        {/* Filter Header */}
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-purple-400" />
          <h2 className="text-lg font-semibold text-white">Categories</h2>
        </div>

        {/* All Messages */}
        <button
          onClick={() => setSelectedCategory('all')}
          className={cn(
            "w-full flex items-center justify-between p-3 rounded-lg transition-all duration-200",
            selectedCategory === 'all'
              ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30"
              : "hover:bg-white/5 border border-transparent"
          )}
        >
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Hash className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-medium">All Messages</span>
          </div>
          <span className="text-sm text-gray-400 bg-white/10 px-2 py-1 rounded-full">
            {messages.length}
          </span>
        </button>

        {/* Category List */}
        <div className="space-y-2">
          {categoryStats.map(({ category, count, sentiment }) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={cn(
                "w-full flex items-center justify-between p-3 rounded-lg transition-all duration-200 group",
                selectedCategory === category
                  ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30"
                  : "hover:bg-white/5 border border-transparent"
              )}
            >
              <div className="flex items-center space-x-3">
                <div className={cn(
                  "w-8 h-8 bg-gradient-to-r rounded-lg flex items-center justify-center text-sm",
                  `bg-gradient-to-r ${getCategoryColor(category)}`
                )}>
                  {getCategoryIcon(category)}
                </div>
                <div className="text-left">
                  <div className="text-white font-medium capitalize">
                    {category.replace('-', ' ')}
                  </div>
                  <div className="text-xs text-gray-400">
                    Sentiment: {sentiment > 0 ? '😊' : sentiment < 0 ? '😔' : '😐'} {sentiment.toFixed(1)}
                  </div>
                </div>
              </div>
              <span className="text-sm text-gray-400 bg-white/10 px-2 py-1 rounded-full group-hover:bg-white/20 transition-colors">
                {count}
              </span>
            </button>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="glass border border-white/10 rounded-lg p-4 space-y-3">
          <h3 className="text-sm font-medium text-purple-300">Quick Stats</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Messages</span>
              <span className="text-white font-medium">{messages.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Categories</span>
              <span className="text-white font-medium">{categoryStats.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Sentiment</span>
              <span className="text-white font-medium">
                {messages.length > 0 
                  ? (messages.reduce((sum, m) => sum + m.sentiment, 0) / messages.length).toFixed(1)
                  : '0.0'
                }
              </span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
} 