'use client'

import { useState } from 'react'
import { Box, Flex, Text, chakra } from '@chakra-ui/react'
import { palette } from '@/theme/palette'
import { Icon } from './Icon'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [focused, setFocused] = useState(false)
  const canSend = message.trim().length > 0 && !disabled

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    if (!canSend) return
    onSend(message.trim())
    setMessage('')
  }

  return (
    <Box
      position="sticky"
      bottom={0}
      zIndex={60}
      bg="rgba(244, 239, 230, 0.94)"
      backdropFilter="blur(12px)"
      borderTopWidth="1px"
      borderColor={palette.hairline}
      pt={4}
      pb={4}
      px={{ base: 4, md: 8 }}
    >
      <chakra.form onSubmit={handleSubmit} maxW="900px" mx="auto">
        <Flex
          alignItems="center"
          bg={palette.white}
          borderWidth="1px"
          borderColor={focused ? palette.ink : palette.hairlineStrong}
          borderRadius="12px"
          pl={{ base: 4, md: 5 }}
          pr={1.5}
          h="58px"
          opacity={disabled ? 0.7 : 1}
          css={{
            transition: 'border-color 0.25s ease, box-shadow 0.25s ease',
            boxShadow: focused ? '0 0 0 3px rgba(15, 27, 45, 0.1)' : 'none',
          }}
        >
          <chakra.input
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            disabled={disabled}
            placeholder={disabled ? 'Researching, one moment…' : 'Ask for another garment, or refine this one…'}
            aria-label="Describe the clothing you are looking for"
            flex={1}
            minW={0}
            bg="transparent"
            border="none"
            outline="none"
            color={palette.ink}
            fontSize="16px"
            fontWeight="500"
            css={{
              '&::placeholder': {
                fontFamily: 'var(--font-display), Georgia, serif',
                fontStyle: 'italic',
                fontSize: '1.12rem',
                color: '#7b8091',
                fontWeight: 400,
              },
              '&:focus-visible': { outline: 'none' },
            }}
          />
          <chakra.button
            type="submit"
            disabled={!canSend}
            aria-label="Send"
            w="46px"
            h="46px"
            borderRadius="9px"
            display="flex"
            alignItems="center"
            justifyContent="center"
            color={canSend ? palette.paper : palette.textMuted}
            bg={canSend ? palette.ink : palette.paperDeep}
            cursor={canSend ? 'pointer' : 'not-allowed'}
            css={{ transition: 'background 0.25s ease', '&:hover:not(:disabled)': { background: '#1d2d49' } }}
          >
            <Icon name="arrowUp" size={19} strokeWidth={1.8} />
          </chakra.button>
        </Flex>
      </chakra.form>
      <Text mt={2.5} textAlign="center" fontSize="11.5px" color={palette.textMuted}>
        Clothing only · Risk levels are guidance, not a guarantee
      </Text>
    </Box>
  )
}
