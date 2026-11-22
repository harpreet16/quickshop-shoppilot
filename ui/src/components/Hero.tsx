'use client'

import { useState } from 'react'
import { Box, Flex, Text, chakra } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { EASE, fonts, palette } from '@/theme/palette'
import { Icon } from './Icon'

const EXAMPLES = [
  'Linen summer dress under $60',
  'Black jeans under $50',
  'Wool coat for winter',
  'White cotton shirt under $40',
]

interface HeroProps {
  onSend: (message: string) => void
}

const rise = (delay: number) => ({
  initial: { opacity: 0, y: 22 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.8, delay, ease: EASE },
})

export function Hero({ onSend }: HeroProps) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const canSend = value.trim().length > 0

  const submit = (event: React.FormEvent) => {
    event.preventDefault()
    const text = value.trim()
    if (!text) return
    onSend(text)
    setValue('')
  }

  return (
    <Box
      as="section"
      position="relative"
      isolation="isolate"
      overflow="hidden"
      color="white"
      minH={{ base: '640px', md: 'min(82vh, 760px)' }}
      display="flex"
      alignItems="center"
      css={{
        background:
          'radial-gradient(70% 55% at 50% 108%, rgba(255, 140, 40, 0.5) 0%, rgba(255, 120, 30, 0) 70%), linear-gradient(180deg, #080d19 0%, #0c1529 42%, #151a33 68%, #241a2b 88%, #2b1a22 100%)',
      }}
    >
      <motion.div
        aria-hidden="true"
        animate={{ opacity: [0.72, 1, 0.72], scaleY: [1, 1.08, 1] }}
        transition={{ duration: 9, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          position: 'absolute',
          left: '-6%',
          right: '-6%',
          bottom: '15%',
          height: 120,
          zIndex: 0,
          filter: 'blur(16px)',
          background:
            'linear-gradient(180deg, rgba(255,110,30,0) 0%, rgba(255,106,40,0.55) 24%, rgba(255,190,60,0.92) 52%, rgba(255,120,40,0.62) 78%, rgba(255,110,30,0) 100%)',
        }}
      />
      <Box aria-hidden="true" position="absolute" left={0} right={0} bottom={0} h="22%" zIndex={0} css={{ background: 'linear-gradient(180deg, rgba(20,12,24,0) 0%, rgba(20,12,24,0.72) 100%)' }} />
      <Box aria-hidden="true" position="absolute" left="7%" top="-22%" w="46%" h="150%" zIndex={0} css={{ background: 'linear-gradient(115deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0) 60%)', transform: 'skewX(-14deg)' }} />
      <Box className="hero-grain" zIndex={1} />

      <Flex
        position="relative"
        zIndex={2}
        direction="column"
        alignItems="center"
        textAlign="center"
        w="100%"
        maxW="900px"
        mx="auto"
        px={{ base: 5, md: 8 }}
        py={{ base: 16, md: 20 }}
      >
        <motion.div {...rise(0.05)}>
          <Flex alignItems="center" gap={4} mb={7}>
            <Box w="38px" h="1px" bg={palette.amber} opacity={0.7} />
            <Text fontSize="11px" fontWeight="600" letterSpacing="0.28em" textTransform="uppercase" color={palette.amber}>
              Clothing, vetted
            </Text>
            <Box w="38px" h="1px" bg={palette.amber} opacity={0.7} />
          </Flex>
        </motion.div>

        <motion.div {...rise(0.15)}>
          <Text
            as="h1"
            fontFamily={fonts.display}
            fontWeight="500"
            fontSize="clamp(2.7rem, 7.2vw, 5.4rem)"
            lineHeight="1.02"
            letterSpacing="-0.02em"
          >
            Clothing you can trust,
            <Box as="span" display="block" fontStyle="italic" color={palette.amber} fontWeight="500">
              in fabrics that last.
            </Box>
          </Text>
        </motion.div>

        <motion.div {...rise(0.3)}>
          <Text mt={7} maxW="560px" fontSize={{ base: '16px', md: '18px' }} lineHeight="1.65" color="rgba(255, 255, 255, 0.74)">
            Describe what you are looking for. QuickShop searches retailers, vets each seller, reads the fabric details and ranks what is worth buying, with the evidence behind every score.
          </Text>
        </motion.div>

        <motion.div {...rise(0.45)} style={{ width: '100%' }}>
          <chakra.form onSubmit={submit} mt={10} w="100%" maxW="680px" mx="auto">
            <Flex
              alignItems="center"
              bg="rgba(251, 248, 242, 0.97)"
              borderRadius="14px"
              pl={{ base: 4, md: 6 }}
              pr={2}
              h={{ base: '60px', md: '68px' }}
              css={{
                transition: 'box-shadow 0.3s ease',
                boxShadow: focused
                  ? '0 0 0 4px rgba(240, 179, 90, 0.42), 0 24px 60px rgba(0, 0, 0, 0.45)'
                  : '0 0 0 1px rgba(255, 255, 255, 0.18), 0 24px 60px rgba(0, 0, 0, 0.4)',
              }}
            >
              <Box color={palette.textSecondary} mr={3} display={{ base: 'none', sm: 'block' }}>
                <Icon name="search" size={20} />
              </Box>
              <chakra.input
                value={value}
                onChange={(event) => setValue(event.target.value)}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                placeholder="Describe a garment, a budget, a fabric…"
                aria-label="Describe the clothing you are looking for"
                flex={1}
                minW={0}
                bg="transparent"
                border="none"
                outline="none"
                color={palette.ink}
                fontSize="17px"
                fontWeight="500"
                css={{
                  '&::placeholder': {
                    fontFamily: 'var(--font-display), Georgia, serif',
                    fontStyle: 'italic',
                    fontSize: '1.2rem',
                    color: '#7b8091',
                    fontWeight: 400,
                  },
                  '&:focus-visible': { outline: 'none' },
                }}
              />
              <chakra.button
                type="submit"
                disabled={!canSend}
                aria-label="Search"
                w={{ base: '46px', md: '52px' }}
                h={{ base: '46px', md: '52px' }}
                borderRadius="10px"
                display="flex"
                alignItems="center"
                justifyContent="center"
                color={canSend ? palette.paper : palette.textMuted}
                bg={canSend ? palette.ink : palette.paperDeep}
                cursor={canSend ? 'pointer' : 'not-allowed'}
                css={{ transition: 'background 0.25s ease, transform 0.25s ease', '&:hover:not(:disabled)': { background: '#1d2d49', transform: 'translateY(-1px)' } }}
              >
                <Icon name="arrowUp" size={20} strokeWidth={1.8} />
              </chakra.button>
            </Flex>
          </chakra.form>

          <Flex mt={6} justifyContent="center" alignItems="center" gap={{ base: 2, md: 3 }} flexWrap="wrap">
            <Text fontSize="11px" fontWeight="600" letterSpacing="0.2em" textTransform="uppercase" color="rgba(255,255,255,0.55)" mr={1}>
              Try
            </Text>
            {EXAMPLES.map((example) => (
              <chakra.button
                key={example}
                type="button"
                onClick={() => onSend(example)}
                px={3.5}
                py={1.5}
                borderRadius="full"
                borderWidth="1px"
                borderColor="rgba(255, 255, 255, 0.24)"
                color="rgba(255, 255, 255, 0.86)"
                fontSize="13px"
                fontWeight="500"
                cursor="pointer"
                css={{
                  transition: 'background 0.25s ease, border-color 0.25s ease, color 0.25s ease',
                  '&:hover': { background: 'rgba(240, 179, 90, 0.14)', borderColor: 'rgba(240, 179, 90, 0.7)', color: '#fff' },
                  '&:focus-visible': { outline: `2px solid ${palette.amber}`, outlineOffset: '3px' },
                }}
              >
                {example}
              </chakra.button>
            ))}
          </Flex>
        </motion.div>
      </Flex>
    </Box>
  )
}
