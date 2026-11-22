'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { scoreColor } from '@/lib/results'

interface ScoreRingProps {
  value: number | null
  size?: number
}

export function ScoreRing({ value, size = 76 }: ScoreRingProps) {
  const stroke = 7
  const center = size / 2
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const fraction = value == null ? 0 : Math.max(0, Math.min(1, value / 5))
  const color = scoreColor(value)
  const label = value == null ? 'Overall score not available' : `Overall score ${value.toFixed(1)} out of 5`

  return (
    <Box position="relative" w={`${size}px`} h={`${size}px`} flexShrink={0} role="img" aria-label={label}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }} aria-hidden="true">
        <circle cx={center} cy={center} r={radius} fill="none" stroke="#e8ecf4" strokeWidth={stroke} />
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference * (1 - fraction) }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <Flex position="absolute" inset={0} direction="column" alignItems="center" justifyContent="center">
        <Text fontSize="lg" fontWeight="800" lineHeight="1" color="gray.800">
          {value == null ? '–' : value.toFixed(1)}
        </Text>
        <Text fontSize="10px" color="gray.500" fontWeight="600" mt={0.5}>of 5</Text>
      </Flex>
    </Box>
  )
}
