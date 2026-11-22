const PATHS = {
  search: ['M11 4a7 7 0 1 0 0 14a7 7 0 0 0 0-14z', 'M20 20l-3.8-3.8'],
  arrowUp: ['M12 19V5', 'M6 11l6-6 6 6'],
  arrowUpRight: ['M7 17L17 7', 'M8 7h9v9'],
  check: ['M5 12.5l4.5 4.5L19 7.5'],
  x: ['M6 6l12 12', 'M18 6L6 18'],
  plus: ['M12 5v14', 'M5 12h14'],
  minus: ['M5 12h14'],
  chevronDown: ['M6 9l6 6 6-6'],
  alert: ['M12 4l9 16H3L12 4z', 'M12 10v4', 'M12 17.2v.01'],
  shield: ['M12 3l7 3v5.5c0 4.3-2.9 7.7-7 9.5-4.1-1.8-7-5.2-7-9.5V6l7-3z', 'M9 12l2.2 2.2L15.5 10'],
  store: ['M4 9l1.2-5h13.6L20 9', 'M4 9v11h16V9', 'M4 9h16', 'M9.5 20v-5h5v5'],
  layers: ['M12 3l9 5-9 5-9-5 9-5z', 'M3 13l9 5 9-5'],
  help: ['M12 3a9 9 0 1 0 0 18a9 9 0 0 0 0-18z', 'M9.7 9.5a2.4 2.4 0 1 1 3.4 2.2c-.7.4-1.1.9-1.1 1.8', 'M12 16.8v.01'],
  leaf: ['M5 19c0-8 4-13 14-14 0 10-5 14-13 14', 'M5 19c3-4 6-7 10-9'],
} as const

export type IconName = keyof typeof PATHS

interface IconProps {
  name: IconName
  size?: number
  strokeWidth?: number
}

export function Icon({ name, size = 18, strokeWidth = 1.6 }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      style={{ flexShrink: 0 }}
    >
      {PATHS[name].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  )
}
