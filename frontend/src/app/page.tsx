'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { messageApi } from '@/lib/api'
import { Header } from '@/components/header'
import { Sidebar } from '@/components/sidebar'
import { MessageGrid } from '@/components/message-grid'
import { AIChat } from '@/components/ai-chat'
import { Analytics } from '@/components/analytics'
import { SearchBar } from '@/components/search-bar'
import { Message } from '@/types'

export default function Dashboard() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [view, setView] = useState<'messages' | 'analytics'>('messages')

  const { data: messages = [], isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['messages'],
    queryFn: messageApi.getMessages,
    refetchInterval: 5000, // Refresh every 5 seconds
    refetchIntervalInBackground: true, // Keep refreshing even when tab is not active
  })

  // Also refresh when component mounts or view changes
  useEffect(() => {
    refetch()
  }, [view, refetch])

  const filteredMessages = messages.filter((message: Message) => {
    const matchesCategory = selectedCategory === 'all' || 
      message.categories.includes(selectedCategory)
    const matchesSearch = searchQuery === '' || 
      message.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      message.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    
    return matchesCategory && matchesSearch
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <Header view={view} setView={setView} isRefreshing={isFetching} />
      
      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          messages={messages}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
        />
        
        {/* Main Content */}
        <main className="flex-1 p-6 ml-64">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Search Bar */}
            <SearchBar 
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              onRefresh={refetch}
              isRefreshing={isFetching}
            />
            
            {/* Content Area */}
            {view === 'messages' ? (
              <MessageGrid 
                messages={filteredMessages}
                isLoading={isLoading}
                error={error}
              />
            ) : (
              <Analytics messages={messages} />
            )}
          </div>
        </main>
      </div>
      
      {/* Floating AI Chat */}
      <AIChat />
    </div>
  )
}
