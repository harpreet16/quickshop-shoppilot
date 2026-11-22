'use client'

import { Box, Flex, Heading, Text, Link } from '@chakra-ui/react'
import { motion } from 'framer-motion'

interface HeaderProps {
  onLogoClick?: () => void
}

export function Header({ onLogoClick }: HeaderProps) {
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
          cursor="pointer"
        >
          <Flex alignItems="center" gap={3}>
            <motion.div
              whileHover={{ scale: 1.05, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
            >
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
                <Text
                  fontSize="xl"
                  fontWeight="700"
                  color="white"
                  fontFamily="var(--font-serif)"
                  fontStyle="italic"
                >
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
              <Text
                fontSize="11px"
                color="gray.500"
                letterSpacing="0.08em"
                textTransform="uppercase"
                fontWeight="600"
              >
                AI Shopping
              </Text>
            </Box>
          </Flex>
        </Link>

        <Flex alignItems="center" gap={3}>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Flex
              alignItems="center"
              gap={2}
              px={4}
              py={2}
              borderRadius="full"
              bg="rgba(34, 197, 94, 0.1)"
              borderWidth="1px"
              borderColor="rgba(34, 197, 94, 0.2)"
            >
              <Box
                w={2}
                h={2}
                borderRadius="full"
                bg="#22c55e"
                boxShadow="0 0 10px rgba(34, 197, 94, 0.5)"
              />
              <Text fontSize="xs" fontWeight="600" color="green.600">Online</Text>
            </Flex>
          </motion.div>
        </Flex>
      </Flex>
    </motion.header>
  )
}
