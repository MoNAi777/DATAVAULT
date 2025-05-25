'use client'

import { Brain, BarChart3, MessageSquare, Sparkles, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'

interface HeaderProps {
  view: 'messages' | 'analytics'
  setView: (view: 'messages' | 'analytics') => void
  isRefreshing?: boolean
}

export function Header({ view, setView, isRefreshing = false }: HeaderProps) {
  return (
    <header className="glass-dark border-b border-white/10 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center animate-glow">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <Sparkles className="w-4 h-4 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                DataVault
              </h1>
              <p className="text-sm text-purple-300">AI Message Intelligence</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-2">
            <button
              onClick={() => setView('messages')}
              className={cn(
                "flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200",
                view === 'messages'
                  ? "bg-purple-500/20 text-purple-200 border border-purple-500/30"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              )}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Messages</span>
            </button>
            
            <button
              onClick={() => setView('analytics')}
              className={cn(
                "flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200",
                view === 'analytics'
                  ? "bg-purple-500/20 text-purple-200 border border-purple-500/30"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              )}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </button>
          </nav>

          {/* Status Indicator */}
          <div className="flex items-center space-x-3">
            {isRefreshing && (
              <div className="flex items-center space-x-2">
                <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />
                <span className="text-sm text-blue-400">Syncing...</span>
              </div>
            )}
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-300">Live</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
} 