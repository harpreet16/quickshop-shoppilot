'use client'

import { Box, Flex, Text, SimpleGrid } from '@chakra-ui/react'
import { useRef, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { MessageBubble } from './MessageBubble'
import { ChatInput } from './ChatInput'
import { ThinkingIndicator } from './ThinkingIndicator'
import type { ChatMessage, ToolCall } from '@/types'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  isLoading: boolean
  liveToolCalls?: ToolCall[]
  onSendMessage: (message: string) => void
}

const suggestions = [
  { icon: '👗', text: 'Linen summer dress under $60', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { icon: '👖', text: 'Black jeans under $50', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { icon: '🧥', text: 'Wool coat for winter', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { icon: '👕', text: 'White cotton shirt under $40', color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
]

const features = [
  { icon: '🏪', title: 'Seller checks', desc: 'Every seller vetted' },
  { icon: '🧵', title: 'Fabric evidence', desc: 'Read from product pages' },
  { icon: '🛡️', title: 'Risk levels', desc: 'Low, medium or high' },
]

export function ChatInterface({ messages, isLoading, liveToolCalls = [], onSendMessage }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <Flex direction="column" flex={1} h="100%" overflow="hidden">
      <Box flex={1} overflowY="auto" px={{ base: 4, md: 6 }} py={6}>
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '70vh',
              padding: '2rem'
            }}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Box
                position="relative"
                mb={8}
              >
                <Box
                  position="absolute"
                  inset={-6}
                  bg="linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.1) 100%)"
                  borderRadius="full"
                  filter="blur(30px)"
                />
                <motion.div
                  animate={{ y: [0, -8, 0] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                >
                  <Box
                    w={24}
                    h={24}
                    bg="white"
                    borderRadius="32px"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    boxShadow="0 20px 60px rgba(102, 126, 234, 0.25), 0 8px 20px rgba(0,0,0,0.08)"
                    position="relative"
                    overflow="hidden"
                    _before={{
                      content: '""',
                      position: 'absolute',
                      inset: 0,
                      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%)',
                    }}
                  >
                    <Text fontSize="5xl">👗</Text>
                  </Box>
                </motion.div>
              </Box>
            </motion.div>

            <motion.div
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              style={{ textAlign: 'center', maxWidth: '600px' }}
            >
              <Text
                fontSize={{ base: '3xl', md: '5xl' }}
                fontWeight="800"
                mb={4}
                letterSpacing="-0.04em"
                lineHeight="1.1"
                fontFamily="var(--font-inter)"
              >
                Find your{' '}
                <Text
                  as="span"
                  fontFamily="var(--font-serif)"
                  fontStyle="italic"
                  fontWeight="400"
                  className="gradient-text"
                >
                  perfect
                </Text>
                {' '}style
              </Text>
              <Text
                color="gray.500"
                fontSize={{ base: 'md', md: 'lg' }}
                mb={10}
                lineHeight="1.7"
                fontWeight="400"
              >
                Describe the clothing you want. I compare retailers, check each seller, read the fabric details and rank the best matches with the evidence behind every score.
              </Text>
            </motion.div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.35 }}
              style={{ width: '100%', maxWidth: '500px', marginBottom: '3rem' }}
            >
              <Flex justifyContent="center" gap={6} flexWrap="wrap">
                {features.map((feature, i) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + i * 0.1 }}
                  >
                    <Flex
                      direction="column"
                      alignItems="center"
                      gap={1}
                      px={4}
                    >
                      <Text fontSize="2xl" mb={1}>{feature.icon}</Text>
                      <Text fontSize="sm" fontWeight="700" color="gray.800">{feature.title}</Text>
                      <Text fontSize="xs" color="gray.400">{feature.desc}</Text>
                    </Flex>
                  </motion.div>
                ))}
              </Flex>
            </motion.div>

            <SimpleGrid
              columns={{ base: 1, sm: 2 }}
              gap={4}
              w="100%"
              maxW="550px"
            >
              {suggestions.map((suggestion, i) => (
                <motion.button
                  key={suggestion.text}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.5 + i * 0.08 }}
                  whileHover={{ scale: 1.03, y: -4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onSendMessage(suggestion.text)}
                  style={{ all: 'unset', cursor: 'pointer', display: 'block' }}
                >
                  <Box
                    p={5}
                    bg="white"
                    borderRadius="20px"
                    boxShadow="0 4px 20px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06)"
                    borderWidth="1px"
                    borderColor="gray.100"
                    textAlign="left"
                    position="relative"
                    overflow="hidden"
                    _hover={{
                      boxShadow: '0 20px 40px rgba(102, 126, 234, 0.15), 0 8px 16px rgba(0,0,0,0.06)',
                      borderColor: 'transparent',
                    }}
                    css={{ transition: 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)' }}
                  >
                    <Box
                      position="absolute"
                      top={0}
                      left={0}
                      right={0}
                      h="3px"
                      bg={suggestion.color}
                      opacity={0}
                      css={{
                        transition: 'opacity 0.3s ease',
                        '.group:hover &': { opacity: 1 }
                      }}
                      className="suggestion-bar"
                    />
                    <Flex alignItems="center" gap={4}>
                      <Flex
                        w={14}
                        h={14}
                        borderRadius="16px"
                        bg={suggestion.color}
                        alignItems="center"
                        justifyContent="center"
                        boxShadow="0 8px 20px rgba(0,0,0,0.12)"
                      >
                        <Text fontSize="2xl">{suggestion.icon}</Text>
                      </Flex>
                      <Box>
                        <Text
                          color="gray.800"
                          fontSize="sm"
                          fontWeight="600"
                          mb={0.5}
                        >
                          {suggestion.text}
                        </Text>
                        <Text color="gray.400" fontSize="xs">
                          Tap to search
                        </Text>
                      </Box>
                    </Flex>
                  </Box>
                </motion.button>
              ))}
            </SimpleGrid>
          </motion.div>
        ) : (
          <Box maxW="4xl" mx="auto">
            <AnimatePresence>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </AnimatePresence>
          </Box>
        )}
        <AnimatePresence>
          {isLoading && (
            <Box maxW="4xl" mx="auto">
              <ThinkingIndicator toolCalls={liveToolCalls} />
            </Box>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </Box>
      <ChatInput onSend={onSendMessage} disabled={isLoading} />
    </Flex>
  )
}
