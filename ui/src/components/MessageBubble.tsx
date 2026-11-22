'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { ProductGrid } from './ProductGrid'
import { ToolProgress } from './ToolProgress'
import type { ChatMessage } from '@/types'

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      style={{ width: '100%', marginBottom: '1.5rem' }}
    >
      <Flex justifyContent={isUser ? 'flex-end' : 'flex-start'}>
        <Box maxW={{ base: '90%', md: '75%' }}>
          <Flex alignItems="flex-end" gap={3} flexDirection={isUser ? 'row-reverse' : 'row'}>
            {!isUser && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: "spring", stiffness: 300 }}
              >
                <Box
                  w={10}
                  h={10}
                  borderRadius="14px"
                  bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  flexShrink={0}
                  boxShadow="0 6px 20px rgba(102, 126, 234, 0.35)"
                >
                  <Text fontSize="sm" fontFamily="var(--font-serif)" fontStyle="italic" color="white" fontWeight="600">Q</Text>
                </Box>
              </motion.div>
            )}
            <Box
              bg={isUser ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white'}
              color={isUser ? 'white' : 'gray.800'}
              px={5}
              py={4}
              borderRadius="24px"
              borderTopRightRadius={isUser ? '6px' : '24px'}
              borderTopLeftRadius={isUser ? '24px' : '6px'}
              boxShadow={isUser
                ? '0 8px 30px rgba(102, 126, 234, 0.3)'
                : '0 4px 20px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04)'}
              borderWidth={isUser ? 0 : '1px'}
              borderColor="gray.100"
            >
              <Text
                fontSize="sm"
                lineHeight="1.8"
                whiteSpace="pre-wrap"
                fontWeight="500"
              >
                {message.content}
              </Text>
            </Box>
            {isUser && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: "spring", stiffness: 300 }}
              >
                <Box
                  w={10}
                  h={10}
                  borderRadius="14px"
                  bg="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  flexShrink={0}
                  boxShadow="0 6px 20px rgba(240, 147, 251, 0.35)"
                >
                  <Text fontSize="md">👤</Text>
                </Box>
              </motion.div>
            )}
          </Flex>

          {message.toolCalls && message.toolCalls.length > 0 && (
            <Box mt={4} ml={14}>
              <Flex direction="column" gap={2}>
                {message.toolCalls.map((toolCall, index) => (
                  <ToolProgress key={`${toolCall.tool}-${index}`} toolCall={toolCall} />
                ))}
              </Flex>
            </Box>
          )}

          {message.products && message.products.length > 0 && (
            <Box mt={5} ml={14}>
              <ProductGrid products={message.products} />
            </Box>
          )}
        </Box>
      </Flex>
    </motion.div>
  )
}
