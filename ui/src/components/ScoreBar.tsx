'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { scoreColor } from '@/lib/results'

interface ScoreBarProps {
  label: string
  value: number | null
  delay?: number
}

export function ScoreBar({ label, value, delay = 0 }: ScoreBarProps) {
  const percent = value == null ? 0 : Math.max(0, Math.min(100, (value / 5) * 100))
  const description = value == null ? `${label} not available` : `${label} ${value} out of 5`

  return (
    <Box role="img" aria-label={description}>
      <Flex justifyContent="space-between" alignItems="baseline" mb={1}>
        <Text fontSize="xs" fontWeight="600" color="gray.600">{label}</Text>
        <Text fontSize="xs" fontWeight="700" color="gray.800">{value == null ? 'n/a' : `${value}/5`}</Text>
      </Flex>
      <Box h="6px" bg="#e8ecf4" borderRadius="full" overflow="hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
          style={{ height: '100%', borderRadius: 9999, background: scoreColor(value) }}
        />
      </Box>
    </Box>
  )
}
