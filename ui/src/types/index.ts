export type RiskLevel = 'low' | 'medium' | 'high'

export interface ProductScores {
  price: number | null
  quality: number | null
  legitimacy: number | null
  overall: number | null
}

export interface ScoredProduct {
  title: string
  merchant: string
  price: number | null
  rating: number | null
  reviews: number | null
  url: string
  scores: ProductScores
  eligible: boolean
  risk: RiskLevel | null
  evidence: string[]
  natural_fiber_pct: number | null
  composition: Record<string, number> | null
}

export interface ToolCall {
  tool: string
  status: 'running' | 'complete'
  count?: number
  blocked?: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  toolCalls?: ToolCall[]
  products?: ScoredProduct[]
  isError?: boolean
  timestamp: Date
}

export interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  sessionId: string | null
  liveToolCalls: ToolCall[]
}
