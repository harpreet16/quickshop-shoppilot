'use client'

import { Flex, Text } from '@chakra-ui/react'
import { toolMeta } from '@/lib/tools'
import type { ToolCall } from '@/types'

interface ToolSummaryProps {
  toolCalls: ToolCall[]
}

export function ToolSummary({ toolCalls }: ToolSummaryProps) {
  const shown = toolCalls.filter((call) => call.tool !== 'ask_user' && call.tool !== 'retrieve_context')
  if (shown.length === 0) return null

  return (
    <Flex alignItems="center" gap={2} flexWrap="wrap" aria-label="How these results were checked" role="group">
      <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="0.06em" mr={1}>
        How I checked
      </Text>
      {shown.map((call) => {
        const meta = toolMeta(call.tool)
        return (
          <Flex
            key={call.tool}
            alignItems="center"
            gap={1.5}
            px={3}
            py={1}
            borderRadius="full"
            bg="white"
            borderWidth="1px"
            borderColor="gray.200"
            fontSize="xs"
            fontWeight="600"
            color="gray.600"
          >
            <Text as="span" aria-hidden="true">{meta.icon}</Text>
            {meta.past}
            {call.count && call.count > 1 ? ` × ${call.count}` : ''}
          </Flex>
        )
      })}
    </Flex>
  )
}
