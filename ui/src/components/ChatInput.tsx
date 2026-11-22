'use client'

import { Box, Flex, Input, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { useState } from 'react'

const MotionBox = motion.create(Box)

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage('')
    }
  }

  return (
    <Box
      position="sticky"
      bottom={0}
      className="glass-strong"
      borderTopWidth="1px"
      borderColor="rgba(0, 0, 0, 0.04)"
      pt={4}
      pb={6}
      px={{ base: 4, md: 6 }}
    >
      <form onSubmit={handleSubmit}>
        <MotionBox
          maxW="3xl"
          mx="auto"
          animate={{
            boxShadow: isFocused
              ? '0 0 0 4px rgba(102, 126, 234, 0.15), 0 20px 50px rgba(102, 126, 234, 0.15)'
              : '0 4px 30px rgba(0, 0, 0, 0.08)',
          }}
          transition={{ duration: 0.3 }}
          bg="white"
          borderRadius="24px"
          borderWidth="2px"
          borderColor={isFocused ? 'rgba(102, 126, 234, 0.5)' : 'transparent'}
          overflow="hidden"
          position="relative"
        >
          <Flex alignItems="center">
            <Box pl={5} color="gray.400">
              <motion.div
                animate={{ rotate: isFocused ? 360 : 0 }}
                transition={{ duration: 0.5 }}
              >
                <Text fontSize="xl">✨</Text>
              </motion.div>
            </Box>
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="What are you looking for today?"
              size="lg"
              border="none"
              bg="transparent"
              color="gray.800"
              _placeholder={{ color: 'gray.400' }}
              _focus={{ outline: 'none', boxShadow: 'none' }}
              disabled={disabled}
              flex={1}
              px={4}
              py={5}
              fontSize="md"
              fontWeight="500"
            />
            <motion.button
              type="submit"
              disabled={!message.trim() || disabled}
              whileHover={{ scale: message.trim() ? 1.05 : 1 }}
              whileTap={{ scale: message.trim() ? 0.95 : 1 }}
              style={{
                background: message.trim()
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : 'linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%)',
                border: 'none',
                borderRadius: '16px',
                width: '52px',
                height: '52px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: message.trim() && !disabled ? 'pointer' : 'not-allowed',
                marginRight: '8px',
                boxShadow: message.trim() ? '0 8px 20px rgba(102, 126, 234, 0.35)' : 'none',
                transition: 'all 0.3s ease',
              }}
            >
              <Text fontSize="xl" color="white">↑</Text>
            </motion.button>
          </Flex>
        </MotionBox>
      </form>

      <Flex justifyContent="center" mt={4} gap={4} flexWrap="wrap">
        <Text fontSize="xs" color="gray.400" fontWeight="500">
          Powered by AI
        </Text>
        <Text fontSize="xs" color="gray.300">•</Text>
        <Text fontSize="xs" color="gray.400" fontWeight="500">
          100+ Stores
        </Text>
        <Text fontSize="xs" color="gray.300">•</Text>
        <Text fontSize="xs" color="gray.400" fontWeight="500">
          Real-time Prices
        </Text>
      </Flex>
    </Box>
  )
}
