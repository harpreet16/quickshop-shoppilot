'use client'

import { useEffect, useRef } from 'react'
import { Box, Flex } from '@chakra-ui/react'
import { AnimatePresence, motion } from 'framer-motion'
import { ChatInput } from './ChatInput'
import { Hero } from './Hero'
import { HowItWorks } from './HowItWorks'
import { MessageBubble } from './MessageBubble'
import { ThinkingIndicator } from './ThinkingIndicator'
import type { ChatMessage, ToolCall } from '@/types'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  isLoading: boolean
  liveToolCalls?: ToolCall[]
  onSendMessage: (message: string) => void
}

export function ChatInterface({ messages, isLoading, liveToolCalls = [], onSendMessage }: ChatInterfaceProps) {
  const endRef = useRef<HTMLDivElement>(null)
  const lastMessage = messages[messages.length - 1]
  const lastId = lastMessage?.id
  const lastRole = lastMessage?.role

  useEffect(() => {
    if (!lastId) return
    if (lastRole === 'assistant') {
      document.getElementById(`msg-${lastId}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } else {
      endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [lastId, lastRole])

  if (messages.length === 0 && !isLoading) {
    return (
      <Flex direction="column" flex={1}>
        <Hero onSend={onSendMessage} />
        <HowItWorks />
      </Flex>
    )
  }

  return (
    <Flex direction="column" flex={1}>
      <Box flex={1} px={{ base: 5, md: 10 }} pt={{ base: 8, md: 12 }} pb={{ base: 12, md: 16 }}>
        <Box maxW="1120px" mx="auto">
          {messages.map((message, index) => (
            <MessageBubble key={message.id} message={message} first={index === 0} />
          ))}
          <AnimatePresence>
            {isLoading && <ThinkingIndicator key="progress" toolCalls={liveToolCalls} />}
          </AnimatePresence>
          <motion.div ref={endRef} style={{ height: 1 }} />
        </Box>
      </Box>
      <ChatInput onSend={onSendMessage} disabled={isLoading} />
    </Flex>
  )
}
