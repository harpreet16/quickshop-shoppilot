export interface Product {
  title: string
  price: number
  rating?: number
  image?: string
  url: string
  source: string
}

export interface ToolCall {
  tool: 'web_search' | 'scrape_url' | 'compare_products' | 'get_asu_deals' | 'finalize_recommendation'
  status: 'running' | 'complete'
  result?: unknown
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
  currentTool?: ToolCall
}
