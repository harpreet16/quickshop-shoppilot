'use client'

import { useState } from 'react'
import { Box, Flex, Text } from '@chakra-ui/react'
import { AnimatePresence, motion } from 'framer-motion'
import { flaggedReasons, formatPrice } from '@/lib/results'
import { RiskPill } from './RiskPill'
import type { ScoredProduct } from '@/types'

interface FlaggedListProps {
  products: ScoredProduct[]
}

export function FlaggedList({ products }: FlaggedListProps) {
  const [open, setOpen] = useState(true)
  if (products.length === 0) return null

  return (
    <Box bg="#fff8f6" borderRadius="24px" borderWidth="1px" borderColor="#fecaca" overflow="hidden">
      <Flex
        as="button"
        onClick={() => setOpen((value) => !value)}
        w="100%"
        alignItems="center"
        justifyContent="space-between"
        gap={3}
        px={5}
        py={4}
        textAlign="left"
        cursor="pointer"
        aria-expanded={open}
        aria-controls="flagged-list"
        _focusVisible={{ outline: '3px solid rgba(220, 38, 38, 0.4)', outlineOffset: '-3px' }}
      >
        <Flex alignItems="center" gap={3}>
          <Flex w={9} h={9} borderRadius="12px" bg="#fee2e2" alignItems="center" justifyContent="center" color="#b91c1c" fontWeight="800" aria-hidden="true">
            !
          </Flex>
          <Box>
            <Text fontSize="sm" fontWeight="700" color="#7f1d1d">
              Not recommended ({products.length})
            </Text>
            <Text fontSize="xs" color="#991b1b" opacity={0.85}>
              These sellers failed the seller checks, so they are not offered as picks.
            </Text>
          </Box>
        </Flex>
        <Text as="span" fontSize="sm" color="#991b1b" aria-hidden="true">{open ? '−' : '+'}</Text>
      </Flex>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id="flagged-list"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
            style={{ overflow: 'hidden' }}
          >
            <Flex direction="column" as="ul" listStyleType="none" m={0} p={0}>
              {products.map((product, index) => {
                const reasons = flaggedReasons(product)
                return (
                  <Box
                    as="li"
                    key={`${product.url}-${index}`}
                    px={5}
                    py={4}
                    borderTopWidth="1px"
                    borderColor="#fde2e0"
                  >
                    <Flex justifyContent="space-between" alignItems="flex-start" gap={3} flexWrap="wrap">
                      <Box minW={0} flex={1}>
                        <Text fontSize="sm" fontWeight="700" color="gray.800" overflowWrap="anywhere">
                          {product.title}
                        </Text>
                        <Text fontSize="xs" color="gray.500" mt={0.5}>
                          {product.merchant} · {formatPrice(product.price)}
                        </Text>
                      </Box>
                      <RiskPill risk={product.risk} />
                    </Flex>
                    {reasons.length > 0 && (
                      <Text fontSize="xs" color="#7f1d1d" mt={2} lineHeight="1.6">
                        {reasons.join(' · ')}
                      </Text>
                    )}
                  </Box>
                )
              })}
            </Flex>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  )
}
