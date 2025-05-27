'use client'

import { useMemo, useState } from 'react'
import { Filter, Hash, MessageSquare, MessageCircle, Calendar, TrendingUp, BarChart3 } from 'lucide-react'
import { Message } from '@/types'
import { getCategoryColor, getCategoryIcon } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface SidebarProps {
  messages: Message[]
  selectedCategory: string
  setSelectedCategory: (category: string) => void
}

export function Sidebar({ messages, selectedCategory, setSelectedCategory }: SidebarProps) {
  const [selectedSource, setSelectedSource] = useState<string>('all')

  const categoryStats = useMemo(() => {
    const filteredMessages = selectedSource === 'all' 
      ? messages 
      : messages.filter(m => m.source_type === selectedSource)

    const stats = new Map<string, { count: number; sentiment: number }>()
    
    filteredMessages.forEach(message => {
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
  }, [messages, selectedSource])

  const sourceStats = useMemo(() => {
    const whatsappCount = messages.filter(m => m.source_type === 'whatsapp').length
    const telegramCount = messages.filter(m => m.source_type === 'telegram').length
    const otherCount = messages.filter(m => !['whatsapp', 'telegram'].includes(m.source_type)).length

    return [
      { source: 'all', count: messages.length, icon: Hash, color: 'from-purple-500 to-pink-500' },
      { source: 'whatsapp', count: whatsappCount, icon: MessageCircle, color: 'from-green-500 to-emerald-500' },
      { source: 'telegram', count: telegramCount, icon: MessageSquare, color: 'from-blue-500 to-cyan-500' },
      ...(otherCount > 0 ? [{ source: 'other', count: otherCount, icon: Hash, color: 'from-gray-500 to-slate-500' }] : [])
    ]
  }, [messages])

  const recentStats = useMemo(() => {
    const now = new Date()
    const today = messages.filter(m => {
      const msgDate = new Date(m.timestamp)
      return msgDate.toDateString() === now.toDateString()
    }).length

    const thisWeek = messages.filter(m => {
      const msgDate = new Date(m.timestamp)
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      return msgDate >= weekAgo
    }).length

    const avgSentiment = messages.length > 0 
      ? messages.reduce((sum, m) => sum + m.sentiment, 0) / messages.length 
      : 0

    return { today, thisWeek, avgSentiment }
  }, [messages])

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 glass-dark border-r border-white/10 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Source Filter */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-white">Sources</h3>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {sourceStats.map(({ source, count, icon: Icon, color }) => (
              <button
                key={source}
                onClick={() => setSelectedSource(source)}
                className={cn(
                  "p-3 rounded-lg transition-all duration-200 text-center",
                  selectedSource === source
                    ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30"
                    : "hover:bg-white/5 border border-white/10"
                )}
              >
                <div className={cn(
                  "w-8 h-8 bg-gradient-to-r rounded-lg flex items-center justify-center mx-auto mb-2",
                  color
                )}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
                <div className="text-xs text-white font-medium capitalize">{source}</div>
                <div className="text-xs text-gray-400">{count}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="glass border border-white/10 rounded-lg p-4 space-y-3">
        <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-white">Overview</h3>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center">
              <div className="text-lg font-bold text-green-400">{recentStats.today}</div>
              <div className="text-xs text-gray-400">Today</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-400">{recentStats.thisWeek}</div>
              <div className="text-xs text-gray-400">This Week</div>
            </div>
            <div className="text-center col-span-2">
              <div className={cn(
                "text-lg font-bold",
                recentStats.avgSentiment > 0.3 ? "text-green-400" :
                recentStats.avgSentiment < -0.3 ? "text-red-400" : "text-yellow-400"
              )}>
                {recentStats.avgSentiment > 0 ? '😊' : recentStats.avgSentiment < 0 ? '😔' : '😐'} 
                {recentStats.avgSentiment.toFixed(1)}
              </div>
              <div className="text-xs text-gray-400">Avg Sentiment</div>
            </div>
          </div>
        </div>

        {/* Categories Filter */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-white">Categories</h3>
            <span className="text-xs text-gray-400">({categoryStats.length})</span>
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
              <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-md flex items-center justify-center">
                <Hash className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm text-white font-medium">All</span>
            </div>
            <span className="text-xs text-gray-400 bg-white/10 px-2 py-1 rounded-full">
              {selectedSource === 'all' 
                ? messages.length 
                : messages.filter(m => m.source_type === selectedSource).length
              }
          </span>
        </button>

        {/* Category List */}
          <div className="space-y-1 max-h-64 overflow-y-auto">
          {categoryStats.map(({ category, count, sentiment }) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={cn(
                  "w-full flex items-center justify-between p-2.5 rounded-lg transition-all duration-200 group",
                selectedCategory === category
                  ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30"
                  : "hover:bg-white/5 border border-transparent"
              )}
            >
                <div className="flex items-center space-x-2.5">
                <div className={cn(
                    "w-6 h-6 bg-gradient-to-r rounded-md flex items-center justify-center text-xs",
                  `bg-gradient-to-r ${getCategoryColor(category)}`
                )}>
                  {getCategoryIcon(category)}
                </div>
                <div className="text-left">
                    <div className="text-sm text-white font-medium capitalize truncate max-w-24">
                    {category.replace('-', ' ')}
                  </div>
                  <div className="text-xs text-gray-400">
                      {sentiment > 0.2 ? '😊' : sentiment < -0.2 ? '😔' : '😐'} {sentiment.toFixed(1)}
                    </div>
                  </div>
                </div>
                <span className="text-xs text-gray-400 bg-white/10 px-2 py-1 rounded-full group-hover:bg-white/20 transition-colors">
                {count}
              </span>
            </button>
          ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="glass border border-white/10 rounded-lg p-4 space-y-3">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-white">Activity</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Total Messages</span>
              <span className="text-white font-medium">{messages.length}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">AI Processed</span>
              <span className="text-green-400 font-medium">
                {messages.filter(m => m.has_embedding).length}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Categories</span>
              <span className="text-purple-400 font-medium">{categoryStats.length}</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
} 