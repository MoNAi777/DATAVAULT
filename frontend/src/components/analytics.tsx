'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { messageApi } from '@/lib/api'
import { Message } from '@/types'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts'
import {
  MessageSquare,
  TrendingUp,
  Users,
  Hash,
  Heart,
  Brain,
  Clock,
  BarChart3,
  PieChart as PieChartIcon
} from 'lucide-react'

const COLORS = {
  whatsapp: '#25D366',
  telegram: '#0088cc',
  positive: '#10b981',
  neutral: '#6b7280',
  negative: '#ef4444',
  primary: '#8b5cf6',
  secondary: '#06b6d4'
}

const CATEGORY_COLORS = [
  '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444',
  '#ec4899', '#84cc16', '#f97316', '#6366f1', '#14b8a6'
]

export function Analytics() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d')
  
  const { data: messages = [], isLoading } = useQuery({
    queryKey: ['messages'],
    queryFn: messageApi.getMessages,
  })

  const analytics = useMemo(() => {
    if (!messages.length) return null

    // Filter by time range
    const now = new Date()
    const cutoffDate = timeRange === 'all' ? new Date(0) : 
      new Date(now.getTime() - (timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90) * 24 * 60 * 60 * 1000)
    
    const filteredMessages = messages.filter((msg: Message) => 
      new Date(msg.timestamp) >= cutoffDate
    )

    // Basic stats
    const totalMessages = filteredMessages.length
    const whatsappCount = filteredMessages.filter((m: Message) => m.source_type === 'whatsapp').length
    const telegramCount = filteredMessages.filter((m: Message) => m.source_type === 'telegram').length
    const aiProcessedCount = filteredMessages.filter((m: Message) => m.processed).length

    // Sentiment analysis
    const sentimentData = filteredMessages.reduce((acc, msg: Message) => {
      if (msg.sentiment !== null && msg.sentiment !== undefined) {
        if (msg.sentiment > 0.1) acc.positive++
        else if (msg.sentiment < -0.1) acc.negative++
        else acc.neutral++
      }
      return acc
    }, { positive: 0, neutral: 0, negative: 0 })

    const avgSentiment = filteredMessages.reduce((sum, msg: Message) => 
      sum + (msg.sentiment || 0), 0) / filteredMessages.length

    // Messages by date
    const messagesByDate = filteredMessages.reduce((acc, msg: Message) => {
      const date = new Date(msg.timestamp).toISOString().split('T')[0]
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const dateData = Object.entries(messagesByDate)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, count]) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        count,
        fullDate: date
      }))

    // Messages by hour
    const messagesByHour = filteredMessages.reduce((acc, msg: Message) => {
      const hour = new Date(msg.timestamp).getHours()
      acc[hour] = (acc[hour] || 0) + 1
      return acc
    }, {} as Record<number, number>)

    const hourData = Array.from({ length: 24 }, (_, hour) => ({
      hour: `${hour.toString().padStart(2, '0')}:00`,
      count: messagesByHour[hour] || 0
    }))

    // Category distribution
    const categoryCount = filteredMessages.reduce((acc, msg: Message) => {
      if (msg.categories) {
        msg.categories.forEach((cat: string) => {
          acc[cat] = (acc[cat] || 0) + 1
        })
      }
      return acc
    }, {} as Record<string, number>)

    const categoryData = Object.entries(categoryCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 8)
      .map(([name, value], index) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
        color: CATEGORY_COLORS[index % CATEGORY_COLORS.length]
      }))

    // Source distribution
    const sourceData = [
      { name: 'WhatsApp', value: whatsappCount, color: COLORS.whatsapp },
      { name: 'Telegram', value: telegramCount, color: COLORS.telegram }
    ].filter(item => item.value > 0)

    // Top senders
    const senderCount = filteredMessages.reduce((acc, msg: Message) => {
      const sender = msg.sender_name || 'Unknown'
      acc[sender] = (acc[sender] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const topSenders = Object.entries(senderCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([name, count]) => ({ name, count }))

    // Message types
    const typeCount = filteredMessages.reduce((acc, msg: Message) => {
      const type = msg.message_type || 'text'
      acc[type] = (acc[type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const typeData = Object.entries(typeCount).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value
    }))

    return {
      totalMessages,
      whatsappCount,
      telegramCount,
      aiProcessedCount,
      avgSentiment,
      sentimentData,
      dateData,
      hourData,
      categoryData,
      sourceData,
      topSenders,
      typeData
    }
  }, [messages, timeRange])

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-white/10 rounded w-48 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-white/10 rounded-lg"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-80 bg-white/10 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="p-6 text-center">
        <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">No Data Available</h3>
        <p className="text-gray-400">Import some messages to see analytics</p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
          <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Analytics Dashboard</h1>
          <p className="text-gray-400">Insights from your message data</p>
        </div>
        
        {/* Time Range Selector */}
        <div className="flex bg-white/10 rounded-lg p-1">
          {(['7d', '30d', '90d', 'all'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded text-sm font-medium transition-all ${
                timeRange === range
                  ? 'bg-purple-500 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              {range === 'all' ? 'All Time' : range.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-dark p-4 rounded-lg border border-white/10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{analytics.totalMessages}</p>
              <p className="text-sm text-gray-400">Total Messages</p>
            </div>
          </div>
        </div>

        <div className="glass-dark p-4 rounded-lg border border-white/10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{analytics.aiProcessedCount}</p>
              <p className="text-sm text-gray-400">AI Processed</p>
            </div>
          </div>
        </div>

        <div className="glass-dark p-4 rounded-lg border border-white/10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <Heart className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {analytics.avgSentiment > 0 ? '+' : ''}{analytics.avgSentiment.toFixed(2)}
              </p>
              <p className="text-sm text-gray-400">Avg Sentiment</p>
            </div>
          </div>
        </div>

        <div className="glass-dark p-4 rounded-lg border border-white/10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{analytics.topSenders.length}</p>
              <p className="text-sm text-gray-400">Active Senders</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Messages Over Time */}
        <div className="glass-dark p-6 rounded-lg border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            Messages Over Time
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={analytics.dateData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#fff'
                }} 
              />
              <Area 
                type="monotone" 
                dataKey="count" 
                stroke={COLORS.primary} 
                fill={COLORS.primary}
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution */}
        <div className="glass-dark p-6 rounded-lg border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <PieChartIcon className="w-5 h-5 mr-2" />
            Category Distribution
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={analytics.categoryData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {analytics.categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Messages by Hour */}
        <div className="glass-dark p-6 rounded-lg border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Activity by Hour
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={analytics.hourData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="hour" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar dataKey="count" fill={COLORS.secondary} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Analysis */}
        <div className="glass-dark p-6 rounded-lg border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Heart className="w-5 h-5 mr-2" />
            Sentiment Analysis
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-green-400">Positive</span>
              <span className="text-white font-semibold">{analytics.sentimentData.positive}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-green-400 h-2 rounded-full" 
                style={{ 
                  width: `${(analytics.sentimentData.positive / analytics.totalMessages) * 100}%` 
                }}
              ></div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Neutral</span>
              <span className="text-white font-semibold">{analytics.sentimentData.neutral}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gray-400 h-2 rounded-full" 
                style={{ 
                  width: `${(analytics.sentimentData.neutral / analytics.totalMessages) * 100}%` 
                }}
              ></div>
      </div>

            <div className="flex items-center justify-between">
              <span className="text-red-400">Negative</span>
              <span className="text-white font-semibold">{analytics.sentimentData.negative}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-red-400 h-2 rounded-full" 
                style={{ 
                  width: `${(analytics.sentimentData.negative / analytics.totalMessages) * 100}%` 
                }}
              ></div>
            </div>
          </div>
        </div>
        </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Senders */}
        <div className="glass-dark p-6 rounded-lg border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Users className="w-5 h-5 mr-2" />
            Top Senders
          </h3>
          <div className="space-y-3">
            {analytics.topSenders.map((sender) => (
              <div key={sender.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                    {sender.name.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-white">{sender.name}</span>
                </div>
                <span className="text-gray-400">{sender.count} messages</span>
              </div>
            ))}
          </div>
        </div>

        {/* Source Distribution */}
        <div className="glass-dark p-6 rounded-lg border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Hash className="w-5 h-5 mr-2" />
            Message Sources
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={analytics.sourceData}
                cx="50%"
                cy="50%"
                outerRadius={60}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {analytics.sourceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#fff'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
} 