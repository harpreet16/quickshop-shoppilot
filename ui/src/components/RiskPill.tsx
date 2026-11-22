'use client'

import { Box, Flex } from '@chakra-ui/react'
import { riskMeta } from '@/lib/results'
import type { RiskLevel } from '@/types'

interface RiskPillProps {
  risk: RiskLevel | null
}

export function RiskPill({ risk }: RiskPillProps) {
  const meta = riskMeta(risk)

  return (
    <Flex
      as="span"
      display="inline-flex"
      alignItems="center"
      gap={1.5}
      px={2.5}
      py={1}
      borderRadius="full"
      bg={meta.bg}
      color={meta.fg}
      borderWidth="1px"
      borderColor={meta.border}
      fontSize="xs"
      fontWeight="700"
      whiteSpace="nowrap"
    >
      <Box w="6px" h="6px" borderRadius="full" bg={meta.dot} />
      {meta.label}
    </Flex>
  )
}
