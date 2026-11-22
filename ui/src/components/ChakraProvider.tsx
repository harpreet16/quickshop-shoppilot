'use client'

import { ChakraProvider as Provider } from '@chakra-ui/react'
import { system } from '@/theme'

export function ChakraProvider({ children }: { children: React.ReactNode }) {
  return <Provider value={system}>{children}</Provider>
}
