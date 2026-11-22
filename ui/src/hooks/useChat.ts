'use client'

import { useState, useCallback, useRef } from 'react'
import { isScoredProduct } from '@/lib/results'
import type { ChatMessage, ChatState, ToolCall } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const INACTIVITY_TIMEOUT_MS = 60_000

interface SseEvent {
  event: string
  data: string
}

function parseSseBlock(block: string): SseEvent | null {
  let event = 'message'
  const dataLines: string[] = []

  for (const rawLine of block.split('\n')) {
    if (!rawLine || rawLine.startsWith(':')) continue
    const separator = rawLine.indexOf(':')
    const field = separator === -1 ? rawLine : rawLine.slice(0, separator)
    const value = separator === -1 ? '' : rawLine.slice(separator + 1).replace(/^ /, '')

    if (field === 'event') event = value
    else if (field === 'data') dataLines.push(value)
  }

  if (dataLines.length === 0) return null
  return { event, data: dataLines.join('\n') }
}

function mergeToolCall(calls: ToolCall[], incoming: ToolCall): ToolCall[] {
  const index = calls.findIndex((call) => call.tool === incoming.tool)
  if (index === -1) return [...calls, { ...incoming, count: 1 }]

  const next = [...calls]
  next[index] = {
    ...next[index],
    status: incoming.status,
    blocked: next[index].blocked || incoming.blocked,
    count: (next[index].count ?? 1) + 1,
  }
  return next
}

function errorMessage(content: string): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role: 'assistant',
    content,
    isError: true,
    timestamp: new Date(),
  }
}

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  sessionId: null,
  liveToolCalls: [],
}

export function useChat() {
  const [state, setState] = useState<ChatState>(initialState)
  const sessionIdRef = useRef<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const busyRef = useRef(false)

  const sendMessage = useCallback(async (content: string) => {
    if (busyRef.current) return
    busyRef.current = true

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
      liveToolCalls: [],
    }))

    const controller = new AbortController()
    abortRef.current = controller

    let timedOut = false
    let inactivityTimer: ReturnType<typeof setTimeout> | undefined
    const armTimer = () => {
      clearTimeout(inactivityTimer)
      inactivityTimer = setTimeout(() => {
        timedOut = true
        controller.abort()
      }, INACTIVITY_TIMEOUT_MS)
    }

    let toolCalls: ToolCall[] = []
    let finished = false
    let failure: string | null = null

    const handleEvent = (sse: SseEvent) => {
      let payload: Record<string, unknown>
      try {
        payload = JSON.parse(sse.data)
      } catch {
        failure = 'Received an unreadable response from the server.'
        return
      }

      if (sse.event === 'tool_call') {
        toolCalls = mergeToolCall(toolCalls, {
          tool: String(payload.tool),
          status: payload.status === 'error' ? 'running' : 'complete',
          blocked: Boolean(payload.blocked),
        })
        const snapshot = toolCalls
        setState((prev) => ({ ...prev, liveToolCalls: snapshot }))
      } else if (sse.event === 'question') {
        const questionMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: String(payload.question ?? ''),
          timestamp: new Date(),
        }
        setState((prev) => ({ ...prev, messages: [...prev.messages, questionMessage] }))
      } else if (sse.event === 'done') {
        finished = true
        const sessionId = typeof payload.session_id === 'string' ? payload.session_id : null
        sessionIdRef.current = sessionId
        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: String(payload.response ?? ''),
          toolCalls: toolCalls,
          products: Array.isArray(payload.products) ? payload.products.filter(isScoredProduct) : [],
          timestamp: new Date(),
        }
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, assistantMessage],
          sessionId,
        }))
      } else if (sse.event === 'error') {
        failure = String(payload.message ?? 'The assistant ran into a problem.')
      }
    }

    try {
      armTimer()

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: content, session_id: sessionIdRef.current }),
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`The server responded with status ${response.status}.`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('The server sent an empty response.')

      const decoder = new TextDecoder()
      let buffer = ''

      while (!failure) {
        const { done, value } = await reader.read()
        if (done) break
        armTimer()

        buffer = (buffer + decoder.decode(value, { stream: true })).replace(/\r\n/g, '\n')
        const blocks = buffer.split('\n\n')
        buffer = blocks.pop() ?? ''

        for (const block of blocks) {
          const sse = parseSseBlock(block)
          if (sse) handleEvent(sse)
          if (failure) break
        }
      }

      if (!failure && buffer.trim()) {
        const sse = parseSseBlock(buffer)
        if (sse) handleEvent(sse)
      }

      if (!failure && !finished) {
        failure = 'The connection closed before the assistant finished.'
      }
    } catch (error) {
      if (timedOut) {
        failure = 'The server stopped responding. Please try again.'
      } else if (controller.signal.aborted) {
        failure = null
        finished = true
      } else if (error instanceof TypeError) {
        failure = 'Could not reach the server. Check that the backend is running.'
      } else {
        failure = error instanceof Error ? error.message : 'Something went wrong.'
      }
    } finally {
      clearTimeout(inactivityTimer)
      abortRef.current = null
      busyRef.current = false
    }

    if (failure) {
      const message = errorMessage(failure)
      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, message],
        isLoading: false,
        liveToolCalls: [],
      }))
    } else {
      setState((prev) => ({ ...prev, isLoading: false, liveToolCalls: [] }))
    }
  }, [])

  const clearMessages = useCallback(() => {
    abortRef.current?.abort()
    sessionIdRef.current = null
    busyRef.current = false
    setState(initialState)
  }, [])

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    liveToolCalls: state.liveToolCalls,
    sessionId: state.sessionId,
    sendMessage,
    clearMessages,
  }
}
