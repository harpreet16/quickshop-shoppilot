import type { RiskLevel, ScoredProduct } from '@/types'

export type SortKey = 'best' | 'price' | 'quality' | 'trust'

export const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: 'best', label: 'Best match' },
  { key: 'price', label: 'Lowest price' },
  { key: 'quality', label: 'Fabric quality' },
  { key: 'trust', label: 'Most trusted' },
]

export type EvidenceTone = 'good' | 'warn' | 'unknown' | 'bad' | 'neutral'

export function isScoredProduct(value: unknown): value is ScoredProduct {
  if (typeof value !== 'object' || value === null) return false
  const candidate = value as Record<string, unknown>
  const scores = candidate.scores as Record<string, unknown> | undefined
  return (
    typeof candidate.title === 'string' &&
    typeof candidate.url === 'string' &&
    typeof candidate.eligible === 'boolean' &&
    typeof scores === 'object' &&
    scores !== null &&
    Array.isArray(candidate.evidence)
  )
}

export function splitProducts(products: ScoredProduct[]) {
  return {
    recommended: products.filter((product) => product.eligible),
    flagged: products.filter((product) => !product.eligible),
  }
}

const orElse = (value: number | null | undefined, fallback: number) => (value == null ? fallback : value)

export function sortProducts(products: ScoredProduct[], key: SortKey): ScoredProduct[] {
  const copy = [...products]
  const byOverall = (a: ScoredProduct, b: ScoredProduct) => orElse(b.scores.overall, -1) - orElse(a.scores.overall, -1)

  if (key === 'price') {
    copy.sort((a, b) => orElse(a.price, Infinity) - orElse(b.price, Infinity) || byOverall(a, b))
  } else if (key === 'quality') {
    copy.sort((a, b) => orElse(b.scores.quality, -1) - orElse(a.scores.quality, -1) || byOverall(a, b))
  } else if (key === 'trust') {
    copy.sort((a, b) => orElse(b.scores.legitimacy, -1) - orElse(a.scores.legitimacy, -1) || byOverall(a, b))
  } else {
    copy.sort(byOverall)
  }
  return copy
}

export function formatPrice(price: number | null | undefined): string {
  return price == null ? 'Price not listed' : `$${price.toFixed(2)}`
}

export function fabricLabel(product: ScoredProduct): string {
  const composition = product.composition
  if (composition && Object.keys(composition).length > 0) {
    return Object.entries(composition)
      .sort((a, b) => b[1] - a[1])
      .map(([fiber, share]) => `${Math.round(share)}% ${fiber}`)
      .join(', ')
  }
  if (product.natural_fiber_pct != null) return `${Math.round(product.natural_fiber_pct)}% natural fiber`
  return 'Fabric not confirmed'
}

export function parseEvidence(line: string): { tone: EvidenceTone; text: string } {
  const trimmed = line.trim()
  if (/^INELIGIBLE/i.test(trimmed)) {
    return { tone: 'bad', text: trimmed.replace(/^INELIGIBLE:?\s*/i, 'Ineligible: ') }
  }
  if (trimmed.startsWith('✓')) return { tone: 'good', text: trimmed.slice(1).trim() }
  if (trimmed.startsWith('⚠')) return { tone: 'warn', text: trimmed.slice(1).trim() }
  if (trimmed.startsWith('?')) return { tone: 'unknown', text: trimmed.slice(1).trim() }
  return { tone: 'neutral', text: trimmed }
}

export function flaggedReasons(product: ScoredProduct): string[] {
  return product.evidence
    .map(parseEvidence)
    .filter((entry) => entry.tone === 'warn' || entry.tone === 'unknown' || entry.tone === 'bad')
    .map((entry) => entry.text)
}

export function scoreColor(value: number | null | undefined): string {
  if (value == null) return '#94a3b8'
  if (value >= 4) return '#16a34a'
  if (value >= 3) return '#d97706'
  return '#dc2626'
}

export interface RiskMeta {
  label: string
  bg: string
  fg: string
  border: string
  dot: string
}

export function riskMeta(risk: RiskLevel | null | undefined): RiskMeta {
  if (risk === 'low') return { label: 'Low risk', bg: '#ecfdf3', fg: '#166534', border: '#bbf7d0', dot: '#16a34a' }
  if (risk === 'medium') return { label: 'Medium risk', bg: '#fffbeb', fg: '#92400e', border: '#fde68a', dot: '#d97706' }
  if (risk === 'high') return { label: 'High risk', bg: '#fef2f2', fg: '#991b1b', border: '#fecaca', dot: '#dc2626' }
  return { label: 'Risk unknown', bg: '#f1f5f9', fg: '#475569', border: '#e2e8f0', dot: '#94a3b8' }
}
