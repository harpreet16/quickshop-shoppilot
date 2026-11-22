import { createSystem, defaultConfig, defineConfig } from '@chakra-ui/react'

const config = defineConfig({
  theme: {
    tokens: {
      colors: {
        brand: {
          50: { value: '#fdf4ff' },
          100: { value: '#fae8ff' },
          200: { value: '#f5d0fe' },
          300: { value: '#f0abfc' },
          400: { value: '#e879f9' },
          500: { value: '#d946ef' },
          600: { value: '#c026d3' },
          700: { value: '#a21caf' },
          800: { value: '#86198f' },
          900: { value: '#701a75' },
        },
        surface: {
          50: { value: '#18181b' },
          100: { value: '#1f1f23' },
          200: { value: '#27272a' },
          300: { value: '#3f3f46' },
          400: { value: '#52525b' },
          500: { value: '#71717a' },
          600: { value: '#a1a1aa' },
          700: { value: '#d4d4d8' },
          800: { value: '#e4e4e7' },
          900: { value: '#fafafa' },
        },
      },
    },
  },
})

export const system = createSystem(defaultConfig, config)
