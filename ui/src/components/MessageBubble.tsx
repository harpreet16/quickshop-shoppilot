'use client'

import { useState } from 'react'
import { Box, Flex, Text } from '@chakra-ui/react'
import { AnimatePresence, motion } from 'framer-motion'
import { Markdown, leadText } from './Markdown'
import { ResultsDashboard } from './ResultsDashboard'
import { ToolSummary } from './ToolSummary'
import type { ChatMessage } from '@/types'

interface MessageBubbleProps {
  message: ChatMessage
}

function Avatar({ isUser }: { isUser: boolean }) {
  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.1, type: 'spring', stiffness: 300 }}
    >
      <Box
        w={10}
        h={10}
        borderRadius="14px"
        bg={isUser ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}
        display="flex"
        alignItems="center"
        justifyContent="center"
        flexShrink={0}
        boxShadow={isUser ? '0 6px 20px rgba(240, 147, 251, 0.35)' : '0 6px 20px rgba(102, 126, 234, 0.35)'}
        aria-hidden="true"
      >
        {isUser ? (
          <Text fontSize="md">👤</Text>
        ) : (
          <Text fontSize="sm" fontFamily="var(--font-serif)" fontStyle="italic" color="white" fontWeight="600">Q</Text>
        )}
      </Box>
    </motion.div>
  )
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [summaryOpen, setSummaryOpen] = useState(false)
  const products = message.products ?? []
  const hasProducts = !isUser && products.length > 0
  const bubbleText = hasProducts ? leadText(message.content) : message.content

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      style={{ width: '100%', marginBottom: '1.75rem' }}
    >
      <Flex justifyContent={isUser ? 'flex-end' : 'flex-start'}>
        <Box maxW={hasProducts ? '100%' : { base: '92%', md: '78%' }} w={hasProducts ? '100%' : undefined} minW={0}>
          {(!hasProducts || bubbleText) && (
            <Flex alignItems="flex-end" gap={3} flexDirection={isUser ? 'row-reverse' : 'row'}>
              <Avatar isUser={isUser} />
              <Box
                bg={isUser ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : message.isError ? 'red.50' : 'white'}
                color={isUser ? 'white' : message.isError ? 'red.700' : 'gray.800'}
                role={message.isError ? 'alert' : undefined}
                px={5}
                py={4}
                minW={0}
                borderRadius="24px"
                borderTopRightRadius={isUser ? '6px' : '24px'}
                borderTopLeftRadius={isUser ? '24px' : '6px'}
                boxShadow={isUser ? '0 8px 30px rgba(102, 126, 234, 0.3)' : '0 4px 20px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04)'}
                borderWidth={isUser ? 0 : '1px'}
                borderColor={message.isError ? 'red.200' : 'gray.100'}
              >
                {isUser || message.isError ? (
                  <Text fontSize="sm" lineHeight="1.8" whiteSpace="pre-wrap" overflowWrap="anywhere" fontWeight="500">
                    {message.content}
                  </Text>
                ) : (
                  <Markdown text={bubbleText} />
                )}
              </Box>
            </Flex>
          )}

          {hasProducts && (
            <Flex direction="column" gap={5} mt={bubbleText ? 5 : 0}>
              <ResultsDashboard products={products} />

              {message.toolCalls && message.toolCalls.length > 0 && <ToolSummary toolCalls={message.toolCalls} />}

              <Box bg="white" borderRadius="20px" borderWidth="1px" borderColor="gray.100" overflow="hidden">
                <Flex
                  as="button"
                  onClick={() => setSummaryOpen((value) => !value)}
                  w="100%"
                  alignItems="center"
                  justifyContent="space-between"
                  px={5}
                  py={3.5}
                  cursor="pointer"
                  textAlign="left"
                  aria-expanded={summaryOpen}
                  aria-controls={`summary-${message.id}`}
                  _focusVisible={{ outline: '3px solid rgba(102, 126, 234, 0.5)', outlineOffset: '-3px' }}
                >
                  <Text fontSize="sm" fontWeight="700" color="gray.700">Full written summary</Text>
                  <Text as="span" color="gray.500" aria-hidden="true">{summaryOpen ? '−' : '+'}</Text>
                </Flex>
                <AnimatePresence initial={false}>
                  {summaryOpen && (
                    <motion.div
                      id={`summary-${message.id}`}
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                      style={{ overflow: 'hidden' }}
                    >
                      <Box px={5} pb={5} pt={1} borderTopWidth="1px" borderColor="gray.100">
                        <Box pt={4}>
                          <Markdown text={message.content} />
                        </Box>
                      </Box>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Box>
            </Flex>
          )}

          {!hasProducts && !isUser && message.toolCalls && message.toolCalls.length > 0 && (
            <Box mt={4}>
              <ToolSummary toolCalls={message.toolCalls} />
            </Box>
          )}
        </Box>
      </Flex>
    </motion.div>
  )
}
