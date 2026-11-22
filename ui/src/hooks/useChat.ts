'use client'

import { useState, useCallback, useRef } from 'react'
import type { ChatMessage, ToolCall } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  sessionId: string | null
}

export function useChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    sessionId: null,
  })

  const toolCallsRef = useRef<ToolCall[]>([])

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }))

    toolCallsRef.current = []

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content,
          session_id: state.sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('event:')) {
            const eventType = line.slice(6).trim()
            continue
          }

          if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim()
            if (!dataStr) continue

            try {
              const data = JSON.parse(dataStr)

              if (data.event === 'thinking') {
                // Already showing loading state
              } else if (data.event === 'tool_call') {
                const toolData = data.data || data
                const toolCall: ToolCall = {
                  tool: toolData.tool as ToolCall['tool'],
                  status: toolData.status === 'complete' ? 'complete' : 'running',
                }

                const existingIndex = toolCallsRef.current.findIndex(t => t.tool === toolCall.tool)
                if (existingIndex >= 0) {
                  toolCallsRef.current[existingIndex] = toolCall
                } else {
                  toolCallsRef.current.push(toolCall)
                }
              } else if (data.event === 'question') {
                const questionData = data.data || data
                const questionMessage: ChatMessage = {
                  id: crypto.randomUUID(),
                  role: 'assistant',
                  content: questionData.question,
                  toolCalls: [...toolCallsRef.current],
                  timestamp: new Date(),
                }
                setState((prev) => ({
                  ...prev,
                  messages: [...prev.messages, questionMessage],
                  isLoading: false,
                }))
              } else if (data.event === 'done') {
                const doneData = data.data || data
                const assistantMessage: ChatMessage = {
                  id: crypto.randomUUID(),
                  role: 'assistant',
                  content: doneData.response,
                  toolCalls: [...toolCallsRef.current],
                  timestamp: new Date(),
                }
                setState((prev) => ({
                  ...prev,
                  messages: [...prev.messages, assistantMessage],
                  isLoading: false,
                  sessionId: doneData.session_id,
                }))
              } else if (data.event === 'error') {
                const errorData = data.data || data
                throw new Error(errorData.message || 'Unknown error')
              }
            } catch (parseError) {
              // Skip malformed JSON
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error)

      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false,
      }))
    }
  }, [state.sessionId])

  const clearMessages = useCallback(() => {
    setState({
      messages: [],
      isLoading: false,
      sessionId: null,
    })
    toolCallsRef.current = []
  }, [])

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    sessionId: state.sessionId,
    sendMessage,
    clearMessages,
  }
}
