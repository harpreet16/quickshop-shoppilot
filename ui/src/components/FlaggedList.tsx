'use client'

import { useState } from 'react'
import { Box, Flex, Text } from '@chakra-ui/react'
import { AnimatePresence, motion } from 'framer-motion'
import { flaggedReasons, formatPrice } from '@/lib/results'
import { EASE, fonts, palette } from '@/theme/palette'
import { Icon } from './Icon'
import { RiskTag } from './RiskTag'
import type { ScoredProduct } from '@/types'

interface FlaggedListProps {
  products: ScoredProduct[]
}

export function FlaggedList({ products }: FlaggedListProps) {
  const [open, setOpen] = useState(true)
  if (products.length === 0) return null

  return (
    <Box bg="#fbf1ee" borderWidth="1px" borderColor={palette.dangerBorder} borderRadius="10px" overflow="hidden">
      <Flex
        as="button"
        onClick={() => setOpen((value) => !value)}
        w="100%"
        alignItems="center"
        justifyContent="space-between"
        gap={4}
        px={{ base: 5, md: 7 }}
        py={5}
        textAlign="left"
        cursor="pointer"
        aria-expanded={open}
        aria-controls="flagged-list"
      >
        <Flex alignItems="center" gap={4}>
          <Box color={palette.danger}>
            <Icon name="alert" size={22} />
          </Box>
          <Box>
            <Text as="h3" fontFamily={fonts.display} fontSize="26px" fontWeight="600" lineHeight="1.1" color={palette.danger}>
              Not recommended <Box as="span" fontWeight="500">({products.length})</Box>
            </Text>
            <Text mt={1} fontSize="13.5px" color={palette.danger} opacity={0.88}>
              These sellers failed the seller checks, so they are not offered as picks.
            </Text>
          </Box>
        </Flex>
        <Box color={palette.danger} css={{ transition: 'transform 0.3s ease', transform: open ? 'rotate(180deg)' : 'none' }}>
          <Icon name="chevronDown" size={20} />
        </Box>
      </Flex>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id="flagged-list"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.35, ease: EASE }}
            style={{ overflow: 'hidden' }}
          >
            <Flex as="ul" direction="column" listStyleType="none" m={0} p={0}>
              {products.map((product, index) => {
                const reasons = flaggedReasons(product)
                return (
                  <Box
                    as="li"
                    key={`${product.url}-${index}`}
                    px={{ base: 5, md: 7 }}
                    py={5}
                    borderTopWidth="1px"
                    borderColor={palette.dangerBorder}
                  >
                    <Flex justifyContent="space-between" alignItems="flex-start" gap={4} flexWrap="wrap">
                      <Box minW={0} flex={1}>
                        <Text fontSize="15px" fontWeight="700" color={palette.ink} overflowWrap="anywhere" lineHeight="1.4">
                          {product.title}
                        </Text>
                        <Text className="tabular" fontSize="13px" color={palette.textSecondary} mt={1}>
                          {product.merchant} · {formatPrice(product.price)}
                        </Text>
                      </Box>
                      <RiskTag risk={product.risk} />
                    </Flex>
                    {reasons.length > 0 && (
                      <Flex as="ul" direction="column" listStyleType="none" m={0} p={0} gap={1} mt={3}>
                        {reasons.map((reason) => (
                          <Flex as="li" key={reason} gap={2.5} alignItems="flex-start" fontSize="13px" lineHeight="1.55" color={palette.danger}>
                            <Box mt="3px">
                              <Icon name="x" size={13} strokeWidth={2.2} />
                            </Box>
                            {reason}
                          </Flex>
                        ))}
                      </Flex>
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
