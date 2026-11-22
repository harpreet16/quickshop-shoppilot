'use client'

import { Flex } from '@chakra-ui/react'
import { Header, ChatInterface } from '@/components'
import { useChat } from '@/hooks/useChat'
import { useHealth } from '@/hooks/useHealth'

export default function Home() {
  const { messages, isLoading, liveToolCalls, sendMessage, clearMessages } = useChat()
  const health = useHealth()

  return (
    <Flex direction="column" minH="100vh">
      <Header onLogoClick={clearMessages} health={health} />
      <Flex as="main" direction="column" flex={1}>
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          liveToolCalls={liveToolCalls}
          onSendMessage={sendMessage}
        />
      </Flex>
    </Flex>
  )
}
