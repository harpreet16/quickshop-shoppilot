'use client'

import { ChakraProvider as Provider } from '@chakra-ui/react'
import { MotionConfig } from 'framer-motion'
import { system } from '@/theme'

export function ChakraProvider({ children }: { children: React.ReactNode }) {
  return (
    <Provider value={system}>
      <MotionConfig reducedMotion="user">{children}</MotionConfig>
    </Provider>
  )
}
