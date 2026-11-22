export interface ToolMeta {
  label: string
  past: string
  icon: string
  color: string
}

export const TOOL_META: Record<string, ToolMeta> = {
  search_listings: { label: 'Searching stores', past: 'Searched stores', icon: '🔍', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  check_merchant: { label: 'Verifying seller', past: 'Verified sellers', icon: '🏪', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  fetch_product_evidence: { label: 'Reading product page', past: 'Read product pages', icon: '📄', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  score_product: { label: 'Scoring products', past: 'Scored products', icon: '⭐', color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
  ask_user: { label: 'Asking for details', past: 'Checked your details', icon: '💬', color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' },
  retrieve_context: { label: 'Gathering context', past: 'Gathered context', icon: '📚', color: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)' },
}

export function toolMeta(tool: string): ToolMeta {
  return (
    TOOL_META[tool] ?? {
      label: tool,
      past: tool,
      icon: '⚙️',
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }
  )
}
