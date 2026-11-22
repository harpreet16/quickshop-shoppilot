'use client'

import { Flex } from '@chakra-ui/react'
import { riskMeta } from '@/lib/results'
import type { RiskLevel } from '@/types'

interface RiskTagProps {
  risk: RiskLevel | null
}

export function RiskTag({ risk }: RiskTagProps) {
  const meta = riskMeta(risk)

  return (
    <Flex
      as="span"
      display="inline-flex"
      alignItems="center"
      px={2.5}
      py="3px"
      borderRadius="4px"
      bg={meta.bg}
      color={meta.fg}
      borderWidth="1px"
      borderColor={meta.border}
      fontSize="10.5px"
      fontWeight="700"
      letterSpacing="0.1em"
      textTransform="uppercase"
      whiteSpace="nowrap"
    >
      {meta.label}
    </Flex>
  )
}
