'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { EASE, fonts, palette } from '@/theme/palette'
import type { HealthState } from '@/hooks/useHealth'

interface HeaderProps {
  onLogoClick?: () => void
  health: HealthState
}

interface HealthView {
  label: string
  detail: string
  title: string
  dot: string
}

function describeHealth(health: HealthState): HealthView {
  if (health.status === 'online') {
    return {
      label: 'Online',
      detail: health.model,
      title: `Backend online. Model: ${health.model}. API version ${health.version}.`,
      dot: palette.positive,
    }
  }
  if (health.status === 'degraded') {
    const missing = health.missing.join(', ')
    return {
      label: 'Degraded',
      detail: missing ? `Missing: ${missing}` : 'Some services unavailable',
      title: `Backend reachable, but not fully configured. ${missing ? `Missing: ${missing}.` : ''}`,
      dot: palette.brass,
    }
  }
  if (health.status === 'offline') {
    return {
      label: 'Offline',
      detail: 'Backend not reachable',
      title: 'The backend did not answer. Check that it is running.',
      dot: palette.danger,
    }
  }
  return { label: 'Checking', detail: 'Contacting backend', title: 'Checking the backend.', dot: palette.hairlineStrong }
}

export function Header({ onLogoClick, health }: HeaderProps) {
  const view = describeHealth(health)

  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: EASE }}
      style={{ position: 'sticky', top: 0, zIndex: 100 }}
    >
      <Flex
        px={{ base: 5, md: 10 }}
        h="68px"
        bg="rgba(244, 239, 230, 0.92)"
        backdropFilter="blur(12px)"
        borderBottomWidth="1px"
        borderColor={palette.hairline}
        alignItems="center"
        justifyContent="space-between"
      >
        <Box
          as="button"
          onClick={onLogoClick}
          aria-label="QuickShop home"
          textAlign="left"
          cursor="pointer"
          borderRadius="8px"
          _focusVisible={{ outline: `2px solid ${palette.ink}`, outlineOffset: '6px' }}
        >
          <Flex alignItems="center" gap={3.5}>
            <Flex
              w="36px"
              h="36px"
              borderRadius="full"
              borderWidth="1.5px"
              borderColor={palette.ink}
              alignItems="center"
              justifyContent="center"
              color={palette.ink}
              fontFamily={fonts.display}
              fontStyle="italic"
              fontSize="22px"
              fontWeight="600"
              lineHeight="1"
              pb="2px"
              aria-hidden="true"
            >
              Q
            </Flex>
            <Box>
              <Text fontFamily={fonts.display} fontSize="27px" fontWeight="600" lineHeight="1" letterSpacing="-0.01em" color={palette.ink}>
                QuickShop
              </Text>
              <Text
                display={{ base: 'none', sm: 'block' }}
                fontSize="9.5px"
                fontWeight="600"
                letterSpacing="0.24em"
                textTransform="uppercase"
                color={palette.textSecondary}
                mt="3px"
              >
                Clothing assistant
              </Text>
            </Box>
          </Flex>
        </Box>

        <Flex role="status" aria-live="polite" title={view.title} alignItems="center" gap={2.5} key={health.status}>
          <Box w="7px" h="7px" borderRadius="full" bg={view.dot} flexShrink={0} />
          <Text fontSize="12px" fontWeight="600" letterSpacing="0.06em" textTransform="uppercase" color={palette.ink}>
            {view.label}
          </Text>
          <Text display={{ base: 'none', md: 'block' }} fontSize="12px" color={palette.textSecondary}>
            {view.detail}
          </Text>
        </Flex>
      </Flex>
    </motion.header>
  )
}
