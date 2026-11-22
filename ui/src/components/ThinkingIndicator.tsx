'use client'

import { useEffect, useState } from 'react'
import { Box, Flex, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { EASE, fonts, palette } from '@/theme/palette'
import { stageViews, type StageState } from '@/lib/tools'
import { Icon } from './Icon'
import type { ToolCall } from '@/types'

interface ThinkingIndicatorProps {
  toolCalls?: ToolCall[]
}

function formatElapsed(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${minutes}:${String(seconds).padStart(2, '0')}`
}

function Marker({ state }: { state: StageState }) {
  if (state === 'done') {
    return (
      <Flex w="26px" h="26px" borderRadius="full" bg={palette.ink} color={palette.paper} alignItems="center" justifyContent="center">
        <Icon name="check" size={14} strokeWidth={2.2} />
      </Flex>
    )
  }
  if (state === 'active') {
    return (
      <Flex w="26px" h="26px" borderRadius="full" borderWidth="1.5px" borderColor={palette.brass} bg={palette.surface} alignItems="center" justifyContent="center">
        <motion.span
          aria-hidden="true"
          animate={{ scale: [1, 1.5, 1], opacity: [1, 0.55, 1] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
          style={{ width: 9, height: 9, borderRadius: 9999, background: palette.brass, display: 'block' }}
        />
      </Flex>
    )
  }
  return <Box w="26px" h="26px" borderRadius="full" borderWidth="1.5px" borderColor={palette.hairlineStrong} bg={palette.surface} />
}

export function ThinkingIndicator({ toolCalls = [] }: ThinkingIndicatorProps) {
  const [seconds, setSeconds] = useState(0)
  const views = stageViews(toolCalls)
  const current = views.find((view) => view.state === 'active')

  useEffect(() => {
    const id = setInterval(() => setSeconds((value) => value + 1), 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.5, ease: EASE }}
      style={{ marginTop: '2rem' }}
      aria-label="Research in progress"
    >
      <Box
        position="relative"
        overflow="hidden"
        maxW="620px"
        bg={palette.surface}
        borderWidth="1px"
        borderColor={palette.hairline}
        borderRadius="12px"
        px={{ base: 5, md: 7 }}
        pt={7}
        pb={4}
      >
        <Box position="absolute" top={0} left={0} right={0} h="2px" bg={palette.hairline} overflow="hidden">
          <motion.div
            aria-hidden="true"
            animate={{ x: ['-100%', '340%'] }}
            transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
            style={{ width: '30%', height: '100%', background: palette.brass }}
          />
        </Box>

        <Flex justifyContent="space-between" alignItems="baseline" gap={4}>
          <Text as="h3" fontFamily={fonts.display} fontSize="26px" fontWeight="500" lineHeight="1.1" color={palette.ink}>
            Researching your request
          </Text>
          <Text aria-hidden="true" className="tabular" fontSize="13px" fontWeight="600" color={palette.textSecondary}>
            {formatElapsed(seconds)}
          </Text>
        </Flex>
        <Text mt={1.5} fontSize="13.5px" color={palette.textSecondary}>
          A thorough search usually takes one to two minutes.
        </Text>

        <Box as="ol" listStyleType="none" mt={6} role="status" aria-live="polite">
          <Text as="span" position="absolute" w="1px" h="1px" overflow="hidden" css={{ clip: 'rect(0 0 0 0)' }}>
            {current ? `${current.stage.title}. ${current.detail}.` : ''}
          </Text>
          {views.map((view, index) => (
            <Box as="li" key={view.stage.tool} position="relative" pl="46px" pb={index === views.length - 1 ? 2 : 6}>
              {index < views.length - 1 && (
                <Box position="absolute" left="12.5px" top="30px" bottom="2px" w="1px" bg={view.state === 'done' ? palette.ink : palette.hairline} />
              )}
              <Box position="absolute" left={0} top="0">
                <Marker state={view.state} />
              </Box>
              <Flex justifyContent="space-between" alignItems="baseline" gap={3} wrap="wrap">
                <Text
                  fontSize="15px"
                  fontWeight={view.state === 'pending' ? 500 : 700}
                  color={view.state === 'pending' ? palette.textMuted : palette.ink}
                >
                  {view.stage.title}
                </Text>
                <Text className="tabular" fontSize="13px" color={view.state === 'active' ? palette.brassText : palette.textSecondary} fontWeight={view.state === 'active' ? 600 : 400}>
                  {view.detail}
                </Text>
              </Flex>
            </Box>
          ))}
        </Box>
      </Box>
    </motion.section>
  )
}
