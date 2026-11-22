export interface Product {
  title: string
  price: number
  rating?: number
  image?: string
  url: string
  source: string
}

export interface ToolCall {
  tool: 'search_listings' | 'check_merchant' | 'fetch_product_evidence' | 'score_product' | 'ask_user'
  status: 'running' | 'complete'
  blocked?: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  toolCalls?: ToolCall[]
  products?: Product[]
  timestamp: Date
}

export interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  sessionId: string | null
}
