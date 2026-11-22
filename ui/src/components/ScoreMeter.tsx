'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { meterColor } from '@/lib/results'
import { EASE, palette } from '@/theme/palette'

interface ScoreMeterProps {
  label: string
  value: number | null
  delay?: number
}

const SEGMENTS = [1, 2, 3, 4, 5]

export function ScoreMeter({ label, value, delay = 0 }: ScoreMeterProps) {
  const color = meterColor(value)
  const description = value == null ? `${label} not available` : `${label} ${value} out of 5`

  return (
    <Flex alignItems="center" gap={3} role="img" aria-label={description}>
      <Text w="84px" flexShrink={0} fontSize="12.5px" fontWeight="500" color={palette.textSecondary}>
        {label}
      </Text>
      <Flex flex={1} gap="3px" aria-hidden="true">
        {SEGMENTS.map((segment) => {
          const filled = value != null && segment <= Math.round(value)
          return (
            <Box key={segment} flex={1} h="5px" borderRadius="1px" bg={palette.hairline} overflow="hidden">
              {filled && (
                <motion.div
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ duration: 0.5, delay: delay + segment * 0.06, ease: EASE }}
                  style={{ width: '100%', height: '100%', background: color, transformOrigin: 'left' }}
                />
              )}
            </Box>
          )
        })}
      </Flex>
      <Text w="28px" textAlign="right" className="tabular" fontSize="12.5px" fontWeight="700" color={palette.ink}>
        {value == null ? 'n/a' : `${value}/5`}
      </Text>
    </Flex>
  )
}
