import { createSystem, defaultConfig, defineConfig } from '@chakra-ui/react'

const config = defineConfig({
  theme: {
    tokens: {
      fonts: {
        body: { value: 'var(--font-body), system-ui, -apple-system, sans-serif' },
        heading: { value: 'var(--font-display), "Cormorant Garamond", Georgia, serif' },
      },
    },
  },
})

export const system = createSystem(defaultConfig, config)
