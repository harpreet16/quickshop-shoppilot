'use client'

import { Box, Flex } from '@chakra-ui/react'
import { Header, ChatInterface } from '@/components'
import { useChat } from '@/hooks/useChat'
import { useHealth } from '@/hooks/useHealth'

export default function Home() {
  const { messages, isLoading, liveToolCalls, sendMessage, clearMessages } = useChat()
  const health = useHealth()

  return (
    <Flex direction="column" minH="100vh" bg="transparent">
      <Header onLogoClick={clearMessages} health={health} />
      <Box flex={1} display="flex" flexDirection="column">
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          liveToolCalls={liveToolCalls}
          onSendMessage={sendMessage}
        />
      </Box>
    </Flex>
  )
}
