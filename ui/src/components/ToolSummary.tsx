'use client'

import { Flex, Text } from '@chakra-ui/react'
import { methodPhrases } from '@/lib/tools'
import { palette } from '@/theme/palette'
import type { ToolCall } from '@/types'

interface ToolSummaryProps {
  toolCalls: ToolCall[]
}

export function ToolSummary({ toolCalls }: ToolSummaryProps) {
  const phrases = methodPhrases(toolCalls)
  if (phrases.length === 0) return null

  return (
    <Flex alignItems="baseline" gap={3} flexWrap="wrap" aria-label="How these results were assembled" role="group">
      <Text fontSize="10.5px" fontWeight="700" letterSpacing="0.2em" textTransform="uppercase" color={palette.textSecondary}>
        Method
      </Text>
      <Text className="tabular" fontSize="13px" color={palette.textSecondary} lineHeight="1.7">
        {phrases.join('  ·  ')}
      </Text>
    </Flex>
  )
}
