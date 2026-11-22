import type { ToolCall } from '@/types'

export interface Stage {
  tool: string
  title: string
  summary: (count: number) => string
}

const plural = (count: number, one: string, many: string) => `${count} ${count === 1 ? one : many}`

export const STAGES: Stage[] = [
  { tool: 'search_listings', title: 'Searching retailers', summary: (n) => `${plural(n, 'search', 'searches')} run` },
  { tool: 'check_merchant', title: 'Vetting sellers', summary: (n) => `${plural(n, 'seller', 'sellers')} checked` },
  { tool: 'fetch_product_evidence', title: 'Reading fabric details', summary: (n) => `${plural(n, 'product page', 'product pages')} read` },
  { tool: 'score_product', title: 'Scoring and ranking', summary: (n) => `${plural(n, 'item', 'items')} scored` },
]

export type StageState = 'done' | 'active' | 'pending'

export interface StageView {
  stage: Stage
  state: StageState
  count: number
  detail: string
}

function countFor(toolCalls: ToolCall[], tool: string): number {
  return toolCalls.filter((call) => call.tool === tool).reduce((total, call) => total + (call.count ?? 1), 0)
}

export function stageViews(toolCalls: ToolCall[]): StageView[] {
  const counts = STAGES.map((stage) => countFor(toolCalls, stage.tool))
  let latest = -1
  counts.forEach((count, index) => {
    if (count > 0) latest = index
  })
  const active = latest === -1 ? 0 : latest

  return STAGES.map((stage, index) => {
    const count = counts[index]
    const state: StageState = index < active ? 'done' : index === active ? 'active' : 'pending'
    let detail = 'Waiting'
    if (count > 0) detail = stage.summary(count)
    else if (state === 'done') detail = 'Not needed'
    else if (state === 'active') detail = 'In progress'
    return { stage, state, count, detail }
  })
}

export function methodPhrases(toolCalls: ToolCall[]): string[] {
  return STAGES.map((stage) => ({ stage, count: countFor(toolCalls, stage.tool) }))
    .filter((entry) => entry.count > 0)
    .map((entry) => entry.stage.summary(entry.count))
}
