'use client'

import { Flex, Text, Box } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { ToolProgress } from './ToolProgress'
import type { ToolCall } from '@/types'

const MotionBox = motion.create(Box)

interface ThinkingIndicatorProps {
  toolCalls?: ToolCall[]
}

export function ThinkingIndicator({ toolCalls = [] }: ThinkingIndicatorProps) {
  const hasProgress = toolCalls.length > 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      style={{ padding: '0.5rem 0' }}
    >
      <Flex alignItems="flex-end" gap={3}>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          <Box
            w={10}
            h={10}
            borderRadius="14px"
            bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            display="flex"
            alignItems="center"
            justifyContent="center"
            boxShadow="0 6px 20px rgba(102, 126, 234, 0.35)"
          >
            <Text fontSize="sm" fontFamily="var(--font-serif)" fontStyle="italic" color="white" fontWeight="600">Q</Text>
          </Box>
        </motion.div>
        <Box
          bg="white"
          borderRadius="24px"
          borderTopLeftRadius="6px"
          px={6}
          py={4}
          boxShadow="0 4px 20px rgba(0,0,0,0.06)"
          borderWidth="1px"
          borderColor="gray.100"
        >
          <Flex alignItems="center" gap={4}>
            <Flex gap={1.5}>
              {[0, 1, 2].map((i) => (
                <MotionBox
                  key={i}
                  w={2.5}
                  h={2.5}
                  bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                  borderRadius="full"
                  animate={{ y: [0, -8, 0], scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
                />
              ))}
            </Flex>
            <Text fontSize="sm" color="gray.500" fontWeight="500">
              {hasProgress ? 'Working on it, this can take a couple of minutes...' : 'Finding the best deals...'}
            </Text>
          </Flex>
        </Box>
      </Flex>

      {hasProgress && (
        <Flex direction="column" gap={2} mt={4} ml={14} maxW="sm">
          {toolCalls.map((toolCall) => (
            <ToolProgress key={toolCall.tool} toolCall={toolCall} />
          ))}
        </Flex>
      )}
    </motion.div>
  )
}
