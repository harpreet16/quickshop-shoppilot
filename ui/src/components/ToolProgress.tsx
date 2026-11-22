'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { motion, AnimatePresence } from 'framer-motion'
import type { ToolCall } from '@/types'

const MotionBox = motion.create(Box)

const toolLabels: Record<string, { label: string; icon: string; color: string }> = {
  search_listings: { label: 'Searching stores', icon: '🔍', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  check_merchant: { label: 'Checking seller', icon: '🏪', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  fetch_product_evidence: { label: 'Reading product page', icon: '📄', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  score_product: { label: 'Scoring products', icon: '⭐', color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
  ask_user: { label: 'Asking for details', icon: '💬', color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' },
}

interface ToolProgressProps {
  toolCall: ToolCall
}

export function ToolProgress({ toolCall }: ToolProgressProps) {
  const config = toolLabels[toolCall.tool] || { label: toolCall.tool, icon: '⚙️', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }
  const { label, icon, color } = config
  const isComplete = toolCall.status === 'complete'

  return (
    <AnimatePresence mode="wait">
      <MotionBox
        key={toolCall.tool}
        initial={{ opacity: 0, x: -20, scale: 0.95 }}
        animate={{ opacity: 1, x: 0, scale: 1 }}
        exit={{ opacity: 0, x: 20, scale: 0.95 }}
        transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
        bg="white"
        borderRadius="16px"
        px={4}
        py={3}
        boxShadow="0 4px 15px rgba(0,0,0,0.04)"
        borderWidth="1px"
        borderColor={isComplete ? 'green.200' : 'gray.100'}
      >
        <Flex alignItems="center" gap={3}>
          <Flex
            w={10}
            h={10}
            borderRadius="12px"
            bg={isComplete ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' : color}
            alignItems="center"
            justifyContent="center"
            boxShadow="0 4px 12px rgba(0,0,0,0.1)"
          >
            <Text fontSize="lg">{isComplete ? '✓' : icon}</Text>
          </Flex>
          <Box flex={1}>
            <Text
              fontSize="sm"
              fontWeight="600"
              color={isComplete ? 'green.600' : 'gray.700'}
            >
              {label}
            </Text>
            {!isComplete && (
              <Box
                h={1.5}
                bg="gray.100"
                borderRadius="full"
                mt={2}
                overflow="hidden"
              >
                <MotionBox
                  h="100%"
                  bg={color}
                  borderRadius="full"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
                  w="50%"
                />
              </Box>
            )}
          </Box>
        </Flex>
      </MotionBox>
    </AnimatePresence>
  )
}
