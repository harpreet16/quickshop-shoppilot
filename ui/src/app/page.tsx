'use client'

import { Box, Flex } from '@chakra-ui/react'
import { Header, ChatInterface } from '@/components'
import { useChat } from '@/hooks/useChat'

export default function Home() {
  const { messages, isLoading, sendMessage, clearMessages } = useChat()

  const handleLogoClick = () => {
    clearMessages()
  }

  return (
    <Flex direction="column" minH="100vh" bg="transparent">
      <Header onLogoClick={handleLogoClick} />
      <Box flex={1} display="flex" flexDirection="column">
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onSendMessage={sendMessage}
        />
      </Box>
    </Flex>
  )
}
