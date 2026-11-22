'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { motion, AnimatePresence } from 'framer-motion'
import { toolMeta } from '@/lib/tools'
import type { ToolCall } from '@/types'

const MotionBox = motion.create(Box)

interface ToolProgressProps {
  toolCall: ToolCall
}

export function ToolProgress({ toolCall }: ToolProgressProps) {
  const { label, icon, color } = toolMeta(toolCall.tool)
  const isComplete = toolCall.status === 'complete'

  return (
    <AnimatePresence mode="wait">
      <MotionBox
        key={`${toolCall.tool}-${isComplete}`}
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
            <Text fontSize="lg" color="white">{isComplete ? '✓' : icon}</Text>
          </Flex>
          <Box flex={1}>
            <Text fontSize="sm" fontWeight="600" color={isComplete ? 'green.600' : 'gray.700'}>
              {label}
              {toolCall.count && toolCall.count > 1 ? ` × ${toolCall.count}` : ''}
            </Text>
            {!isComplete && (
              <Box h={1.5} bg="gray.100" borderRadius="full" mt={2} overflow="hidden">
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
