'use client'

import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { TrendingUp, MessageSquare, Heart, Tag } from 'lucide-react'
import { Message } from '@/types'
import { getCategoryColor } from '@/lib/utils'

interface AnalyticsProps {
  messages: Message[]
}

export function Analytics({ messages }: AnalyticsProps) {
  const analytics = useMemo(() => {
    // Category distribution
    const categoryStats = new Map<string, number>()
    messages.forEach(message => {
      if (message.categories.length === 0) {
        categoryStats.set('uncategorized', (categoryStats.get('uncategorized') || 0) + 1)
      } else {
        message.categories.forEach(category => {
          categoryStats.set(category, (categoryStats.get(category) || 0) + 1)
        })
      }
    })

    const categoryData = Array.from(categoryStats.entries()).map(([category, count]) => ({
      category: category.replace('-', ' '),
      count,
      color: getCategoryColor(category)
    }))

    // Sentiment over time
    const sentimentData = messages
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .map((message, index) => ({
        index: index + 1,
        sentiment: message.sentiment,
        date: new Date(message.timestamp).toLocaleDateString()
      }))

    // Daily message count
    const dailyStats = new Map<string, number>()
    messages.forEach(message => {
      const date = new Date(message.timestamp).toLocaleDateString()
      dailyStats.set(date, (dailyStats.get(date) || 0) + 1)
    })

    const dailyData = Array.from(dailyStats.entries()).map(([date, count]) => ({
      date,
      count
    })).slice(-7) // Last 7 days

    // Top tags
    const tagStats = new Map<string, number>()
    messages.forEach(message => {
      message.tags.forEach(tag => {
        tagStats.set(tag, (tagStats.get(tag) || 0) + 1)
      })
    })

    const topTags = Array.from(tagStats.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([tag, count]) => ({ tag, count }))

    return {
      categoryData,
      sentimentData,
      dailyData,
      topTags,
      totalMessages: messages.length,
      avgSentiment: messages.length > 0 ? messages.reduce((sum, m) => sum + m.sentiment, 0) / messages.length : 0,
      processedMessages: messages.filter(m => m.processed).length,
      categorizedMessages: messages.filter(m => m.categories.length > 0).length
    }
  }, [messages])

  const COLORS = ['#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#3B82F6', '#EF4444', '#6B7280']

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass border border-white/10 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Messages</p>
              <p className="text-2xl font-bold text-white">{analytics.totalMessages}</p>
            </div>
            <MessageSquare className="w-8 h-8 text-purple-400" />
          </div>
        </div>

        <div className="glass border border-white/10 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Avg Sentiment</p>
              <p className="text-2xl font-bold text-white">{analytics.avgSentiment.toFixed(2)}</p>
            </div>
            <Heart className={`w-8 h-8 ${analytics.avgSentiment > 0 ? 'text-green-400' : 'text-red-400'}`} />
          </div>
        </div>

        <div className="glass border border-white/10 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Processed</p>
              <p className="text-2xl font-bold text-white">{analytics.processedMessages}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-400" />
          </div>
        </div>

        <div className="glass border border-white/10 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Categorized</p>
              <p className="text-2xl font-bold text-white">{analytics.categorizedMessages}</p>
            </div>
            <Tag className="w-8 h-8 text-yellow-400" />
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <div className="glass border border-white/10 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Category Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analytics.categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {analytics.categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Daily Messages */}
        <div className="glass border border-white/10 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Daily Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.dailyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Bar dataKey="count" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Trend */}
        <div className="glass border border-white/10 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Sentiment Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.sentimentData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis dataKey="index" stroke="#9CA3AF" />
              <YAxis domain={[-1, 1]} stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="sentiment" 
                stroke="#EC4899" 
                strokeWidth={2}
                dot={{ fill: '#EC4899', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Tags */}
        <div className="glass border border-white/10 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Top Tags</h3>
          <div className="space-y-3">
            {analytics.topTags.map((item, index) => (
              <div key={item.tag} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-xs text-white font-bold">
                    {index + 1}
                  </div>
                  <span className="text-white">{item.tag}</span>
                </div>
                <span className="text-gray-400 bg-white/10 px-2 py-1 rounded-full text-sm">
                  {item.count}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 