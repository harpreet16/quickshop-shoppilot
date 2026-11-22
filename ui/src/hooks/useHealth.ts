'use client'

import { useEffect, useState } from 'react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const POLL_INTERVAL_MS = 30_000
const REQUEST_TIMEOUT_MS = 5_000

const SERVICE_LABELS: Record<string, string> = {
  serpapi: 'Product search',
  firecrawl: 'Page reader',
  model: 'AI model',
}

interface HealthResponse {
  status: 'ok' | 'degraded'
  version: string
  model: string
  services: Record<string, boolean>
}

export type HealthState =
  | { status: 'checking' }
  | { status: 'offline' }
  | { status: 'online' | 'degraded'; model: string; version: string; missing: string[] }

function isHealthResponse(value: unknown): value is HealthResponse {
  if (typeof value !== 'object' || value === null) return false
  const candidate = value as Record<string, unknown>
  return (
    (candidate.status === 'ok' || candidate.status === 'degraded') &&
    typeof candidate.model === 'string' &&
    typeof candidate.version === 'string' &&
    typeof candidate.services === 'object' &&
    candidate.services !== null
  )
}

export function useHealth(): HealthState {
  const [state, setState] = useState<HealthState>({ status: 'checking' })

  useEffect(() => {
    let cancelled = false

    const check = async () => {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
      try {
        const response = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal, cache: 'no-store' })
        if (!response.ok) throw new Error(`health returned ${response.status}`)
        const data: unknown = await response.json()
        if (!isHealthResponse(data)) throw new Error('unexpected health payload')
        if (cancelled) return
        setState({
          status: data.status === 'ok' ? 'online' : 'degraded',
          model: data.model,
          version: data.version,
          missing: Object.entries(data.services)
            .filter(([, available]) => !available)
            .map(([name]) => SERVICE_LABELS[name] ?? name),
        })
      } catch {
        if (!cancelled) setState({ status: 'offline' })
      } finally {
        clearTimeout(timeout)
      }
    }

    check()
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') check()
    }, POLL_INTERVAL_MS)
    const onFocus = () => check()
    window.addEventListener('focus', onFocus)

    return () => {
      cancelled = true
      clearInterval(interval)
      window.removeEventListener('focus', onFocus)
    }
  }, [])

  return state
}
