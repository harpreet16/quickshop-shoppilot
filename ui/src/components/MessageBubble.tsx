'use client'

import { useState } from 'react'
import { Box, Flex, Text } from '@chakra-ui/react'
import { AnimatePresence, motion } from 'framer-motion'
import { EASE, fonts, palette } from '@/theme/palette'
import { Icon } from './Icon'
import { Markdown, leadText } from './Markdown'
import { ResultsDashboard } from './ResultsDashboard'
import { ToolSummary } from './ToolSummary'
import type { ChatMessage } from '@/types'

interface MessageBubbleProps {
  message: ChatMessage
  first?: boolean
}

export function MessageBubble({ message, first = false }: MessageBubbleProps) {
  const [summaryOpen, setSummaryOpen] = useState(false)
  const isUser = message.role === 'user'
  const products = message.products ?? []
  const hasProducts = !isUser && products.length > 0
  const bubbleText = hasProducts ? leadText(message.content) : message.content

  if (isUser) {
    return (
      <motion.section
        id={`msg-${message.id}`}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: EASE }}
        style={{ scrollMarginTop: 92 }}
      >
        <Box pt={first ? 0 : 10} mt={first ? 0 : 12} borderTopWidth={first ? 0 : '1px'} borderColor={palette.hairline}>
          <Text fontSize="10.5px" fontWeight="700" letterSpacing="0.24em" textTransform="uppercase" color={palette.brassText}>
            Your request
          </Text>
          <Text
            as="h2"
            mt={3}
            fontFamily={fonts.display}
            fontSize={{ base: '32px', md: '46px' }}
            fontWeight="500"
            lineHeight="1.1"
            letterSpacing="-0.015em"
            color={palette.ink}
            overflowWrap="anywhere"
          >
            <Box as="span" color={palette.brass} aria-hidden="true">“</Box>
            {message.content}
            <Box as="span" color={palette.brass} aria-hidden="true">”</Box>
          </Text>
        </Box>
      </motion.section>
    )
  }

  return (
    <motion.section
      id={`msg-${message.id}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: EASE }}
      style={{ scrollMarginTop: 92, marginTop: '2rem' }}
    >
      {message.isError ? (
        <Flex
          role="alert"
          gap={4}
          alignItems="flex-start"
          bg={palette.dangerSoft}
          borderWidth="1px"
          borderColor={palette.dangerBorder}
          borderRadius="10px"
          px={{ base: 5, md: 6 }}
          py={5}
          maxW="760px"
        >
          <Box color={palette.danger} mt="2px">
            <Icon name="alert" size={20} />
          </Box>
          <Box minW={0}>
            <Text fontFamily={fonts.display} fontSize="22px" fontWeight="600" lineHeight="1.15" color={palette.danger}>
              Something went wrong
            </Text>
            <Text mt={1.5} fontSize="14.5px" lineHeight="1.65" color={palette.danger} overflowWrap="anywhere">
              {message.content}
            </Text>
          </Box>
        </Flex>
      ) : (
        <Flex direction="column" gap={hasProducts ? 8 : 5}>
          {bubbleText && (
            <Box maxW="760px" borderLeftWidth="2px" borderColor={palette.brass} pl={{ base: 4, md: 6 }}>
              <Markdown text={bubbleText} />
            </Box>
          )}

          {hasProducts && (
            <>
              <ResultsDashboard products={products} />

              {message.toolCalls && message.toolCalls.length > 0 && <ToolSummary toolCalls={message.toolCalls} />}

              <Box borderTopWidth="1px" borderBottomWidth="1px" borderColor={palette.hairline}>
                <Flex
                  as="button"
                  onClick={() => setSummaryOpen((value) => !value)}
                  w="100%"
                  alignItems="center"
                  justifyContent="space-between"
                  gap={4}
                  py={4}
                  textAlign="left"
                  cursor="pointer"
                  aria-expanded={summaryOpen}
                  aria-controls={`summary-${message.id}`}
                >
                  <Text fontSize="14px" fontWeight="700" color={palette.ink}>
                    Read the full written summary
                  </Text>
                  <Box color={palette.textSecondary}>
                    <Icon name={summaryOpen ? 'minus' : 'plus'} size={18} />
                  </Box>
                </Flex>
                <AnimatePresence initial={false}>
                  {summaryOpen && (
                    <motion.div
                      id={`summary-${message.id}`}
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.35, ease: EASE }}
                      style={{ overflow: 'hidden' }}
                    >
                      <Box pb={7} pt={2} maxW="760px">
                        <Markdown text={message.content} />
                      </Box>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Box>
            </>
          )}

          {!hasProducts && message.toolCalls && message.toolCalls.length > 0 && <ToolSummary toolCalls={message.toolCalls} />}
        </Flex>
      )}
    </motion.section>
  )
}
