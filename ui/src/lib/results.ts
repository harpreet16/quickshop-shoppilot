import type { IconName } from '@/components/Icon'
import { palette } from '@/theme/palette'
import type { RiskLevel, ScoredProduct } from '@/types'

export type SortKey = 'best' | 'price' | 'quality' | 'trust'

export const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: 'best', label: 'Best match' },
  { key: 'price', label: 'Lowest price' },
  { key: 'quality', label: 'Fabric quality' },
  { key: 'trust', label: 'Seller trust' },
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

export function evidenceGlyph(tone: EvidenceTone): { icon: IconName; color: string } {
  if (tone === 'good') return { icon: 'check', color: palette.positive }
  if (tone === 'warn') return { icon: 'alert', color: palette.caution }
  if (tone === 'bad') return { icon: 'x', color: palette.danger }
  if (tone === 'unknown') return { icon: 'help', color: palette.textMuted }
  return { icon: 'minus', color: palette.hairlineStrong }
}

export function meterColor(value: number | null | undefined): string {
  if (value == null) return palette.hairlineStrong
  if (value >= 4) return palette.positive
  if (value >= 3) return palette.brass
  return palette.danger
}

export interface RiskMeta {
  label: string
  bg: string
  fg: string
  border: string
}

export function riskMeta(risk: RiskLevel | null | undefined): RiskMeta {
  if (risk === 'low') return { label: 'Low risk', bg: palette.positiveSoft, fg: palette.positive, border: '#c3d8c9' }
  if (risk === 'medium') return { label: 'Medium risk', bg: palette.cautionSoft, fg: palette.caution, border: '#e6d3a6' }
  if (risk === 'high') return { label: 'High risk', bg: palette.dangerSoft, fg: palette.danger, border: palette.dangerBorder }
  return { label: 'Risk unknown', bg: palette.paperDeep, fg: palette.textSecondary, border: palette.hairline }
}
