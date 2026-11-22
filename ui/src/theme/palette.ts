export const palette = {
  paper: '#f4efe6',
  paperDeep: '#ebe4d6',
  surface: '#fbf8f2',
  white: '#ffffff',
  ink: '#0f1b2d',
  inkSoft: '#26334a',
  text: '#232b3a',
  textSecondary: '#586072',
  textMuted: '#6c7384',
  hairline: '#ddd5c6',
  hairlineStrong: '#c7bda9',
  brass: '#b07d2b',
  brassText: '#855a12',
  amber: '#f0b35a',
  positive: '#2f6b4a',
  positiveSoft: '#e5eee7',
  caution: '#8a5d10',
  cautionSoft: '#f5ebd3',
  danger: '#8f2d2d',
  dangerSoft: '#f7e6e2',
  dangerBorder: '#e8c4bd',
} as const

export const fonts = {
  display: 'var(--font-display), "Cormorant Garamond", Georgia, serif',
  body: 'var(--font-body), system-ui, -apple-system, sans-serif',
} as const

export const EASE = [0.22, 1, 0.36, 1] as const
