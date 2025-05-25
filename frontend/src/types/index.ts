export interface Message {
  id: number
  content: string
  message_type: string
  sender_name: string
  sender_id?: string
  source_type: string
  source_chat_id?: string
  source_message_id?: string
  timestamp: string
  created_at: string
  categories: string[]
  tags: string[]
  sentiment: number
  summary: string
  file_path?: string
  file_type?: string
  file_size?: number
  processed: boolean
  has_embedding: boolean
}

export interface SearchQuery {
  query: string
  limit?: number
  categories?: string[]
  sentiment_range?: [number, number]
  date_range?: [string, string]
}

export interface QueryResponse {
  answer: string
  relevant_messages: Message[]
  sources: string[]
}

export interface CategoryStats {
  category: string
  count: number
  sentiment_avg: number
  recent_count: number
} 