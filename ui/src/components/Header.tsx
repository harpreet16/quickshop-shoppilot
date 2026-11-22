'use client'

import { Box, Flex, Heading, Text, Link } from '@chakra-ui/react'
import { motion } from 'framer-motion'
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
  bg: string
  border: string
  fg: string
}

function describeHealth(health: HealthState): HealthView {
  if (health.status === 'online') {
    return {
      label: 'Online',
      detail: health.model,
      title: `Backend online. Model: ${health.model}. API version ${health.version}.`,
      dot: '#22c55e',
      bg: 'rgba(34, 197, 94, 0.1)',
      border: 'rgba(34, 197, 94, 0.25)',
      fg: '#15803d',
    }
  }
  if (health.status === 'degraded') {
    const missing = health.missing.join(', ')
    return {
      label: 'Degraded',
      detail: missing ? `Missing: ${missing}` : 'Some services unavailable',
      title: `Backend reachable, but not fully configured. ${missing ? `Missing: ${missing}.` : ''}`,
      dot: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.12)',
      border: 'rgba(245, 158, 11, 0.3)',
      fg: '#b45309',
    }
  }
  if (health.status === 'offline') {
    return {
      label: 'Offline',
      detail: 'Backend not reachable',
      title: 'The backend did not answer. Check that it is running.',
      dot: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.1)',
      border: 'rgba(239, 68, 68, 0.28)',
      fg: '#b91c1c',
    }
  }
  return {
    label: 'Checking',
    detail: 'Contacting backend',
    title: 'Checking the backend.',
    dot: '#94a3b8',
    bg: 'rgba(148, 163, 184, 0.12)',
    border: 'rgba(148, 163, 184, 0.3)',
    fg: '#475569',
  }
}

export function Header({ onLogoClick, health }: HeaderProps) {
  const view = describeHealth(health)

  return (
    <motion.header
      initial={{ y: -30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    >
      <Flex
        px={{ base: 4, md: 8 }}
        py={4}
        className="glass-strong"
        borderBottomWidth="1px"
        borderColor="rgba(0, 0, 0, 0.04)"
        alignItems="center"
        justifyContent="space-between"
        position="sticky"
        top={0}
        zIndex={100}
        boxShadow="0 4px 30px rgba(0, 0, 0, 0.03)"
      >
        <Link
          onClick={onLogoClick}
          _hover={{ textDecoration: 'none' }}
          _focusVisible={{ outline: '3px solid rgba(102, 126, 234, 0.5)', outlineOffset: '4px', borderRadius: '16px' }}
          cursor="pointer"
          aria-label="QuickShop home"
        >
          <Flex alignItems="center" gap={3}>
            <motion.div whileHover={{ scale: 1.05, rotate: 5 }} whileTap={{ scale: 0.95 }}>
              <Box
                w={12}
                h={12}
                bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                borderRadius="16px"
                display="flex"
                alignItems="center"
                justifyContent="center"
                boxShadow="0 8px 30px rgba(102, 126, 234, 0.35)"
                position="relative"
                overflow="hidden"
                _before={{
                  content: '""',
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 50%)',
                }}
              >
                <Text fontSize="xl" fontWeight="700" color="white" fontFamily="var(--font-serif)" fontStyle="italic">
                  Q
                </Text>
              </Box>
            </motion.div>
            <Box>
              <Heading
                size="md"
                fontWeight="700"
                letterSpacing="-0.03em"
                className="gradient-text"
                fontFamily="var(--font-inter)"
              >
                QuickShop
              </Heading>
              <Text fontSize="11px" color="gray.500" letterSpacing="0.08em" textTransform="uppercase" fontWeight="600">
                Clothing Assistant
              </Text>
            </Box>
          </Flex>
        </Link>

        <motion.div
          key={health.status}
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Flex
            role="status"
            aria-live="polite"
            title={view.title}
            alignItems="center"
            gap={2}
            px={4}
            py={2}
            borderRadius="full"
            bg={view.bg}
            borderWidth="1px"
            borderColor={view.border}
          >
            <Box w={2} h={2} borderRadius="full" bg={view.dot} boxShadow={`0 0 10px ${view.dot}`} flexShrink={0} />
            <Text fontSize="xs" fontWeight="700" color={view.fg}>{view.label}</Text>
            <Text fontSize="xs" fontWeight="500" color={view.fg} opacity={0.75} display={{ base: 'none', md: 'inline' }}>
              {view.detail}
            </Text>
          </Flex>
        </motion.div>
      </Flex>
    </motion.header>
  )
}
