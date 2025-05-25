'use client'

import { Search, X, RefreshCw } from 'lucide-react'

interface SearchBarProps {
  searchQuery: string
  setSearchQuery: (query: string) => void
  onRefresh?: () => void
  isRefreshing?: boolean
}

export function SearchBar({ searchQuery, setSearchQuery, onRefresh, isRefreshing = false }: SearchBarProps) {
  return (
    <div className="relative">
      <div className="glass border border-white/20 rounded-xl p-4">
        <div className="relative flex items-center space-x-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search messages, tags, or ask AI anything..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-10 py-3 bg-transparent text-white placeholder-gray-400 border-none outline-none text-lg"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
          
          {/* Manual Refresh Button */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="flex items-center space-x-2 px-4 py-3 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg transition-all duration-200 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 text-purple-200 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span className="text-purple-200 text-sm">Refresh</span>
            </button>
          )}
        </div>
        
        {/* Search suggestions */}
        {searchQuery && (
          <div className="mt-3 pt-3 border-t border-white/10">
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-gray-400">Quick filters:</span>
              {['crypto', 'ai-tools', 'positive', 'recent'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSearchQuery(filter)}
                  className="px-3 py-1 text-xs bg-purple-500/20 text-purple-200 rounded-full hover:bg-purple-500/30 transition-colors"
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 