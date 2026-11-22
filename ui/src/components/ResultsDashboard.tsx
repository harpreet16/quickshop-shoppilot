'use client'

import { useMemo, useState } from 'react'
import { Box, Flex, SimpleGrid, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { SORT_OPTIONS, formatPrice, sortProducts, splitProducts, type SortKey } from '@/lib/results'
import { FlaggedList } from './FlaggedList'
import { ProductCard } from './ProductCard'
import type { ScoredProduct } from '@/types'

interface ResultsDashboardProps {
  products: ScoredProduct[]
}

interface StatTileProps {
  label: string
  value: string
  accent: string
  index: number
}

function StatTile({ label, value, accent, index }: StatTileProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
    >
      <Box
        bg="white"
        borderRadius="20px"
        px={4}
        py={3.5}
        borderWidth="1px"
        borderColor="gray.100"
        boxShadow="0 4px 18px rgba(15, 23, 42, 0.05)"
        position="relative"
        overflow="hidden"
      >
        <Box position="absolute" left={0} top={0} bottom={0} w="4px" bg={accent} />
        <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="0.06em">
          {label}
        </Text>
        <Text fontSize="xl" fontWeight="800" color="gray.800" mt={1} lineHeight="1.1">
          {value}
        </Text>
      </Box>
    </motion.div>
  )
}

export function ResultsDashboard({ products }: ResultsDashboardProps) {
  const [sort, setSort] = useState<SortKey>('best')
  const { recommended, flagged } = useMemo(() => splitProducts(products), [products])
  const sorted = useMemo(() => sortProducts(recommended, sort), [recommended, sort])

  const prices = recommended.map((product) => product.price).filter((price): price is number => price != null)
  const overalls = recommended.map((product) => product.scores.overall).filter((value): value is number => value != null)
  const lowestPrice = prices.length > 0 ? Math.min(...prices) : null
  const topScore = overalls.length > 0 ? Math.max(...overalls) : null

  return (
    <Flex direction="column" gap={6} w="100%" minW={0}>
      <SimpleGrid columns={{ base: 2, md: 4 }} gap={3}>
        <StatTile index={0} label="Recommended" value={String(recommended.length)} accent="linear-gradient(180deg, #22c55e, #16a34a)" />
        <StatTile index={1} label="Flagged" value={String(flagged.length)} accent="linear-gradient(180deg, #f87171, #dc2626)" />
        <StatTile index={2} label="Lowest price" value={formatPrice(lowestPrice).replace('Price not listed', '—')} accent="linear-gradient(180deg, #667eea, #764ba2)" />
        <StatTile index={3} label="Top score" value={topScore == null ? '—' : `${topScore.toFixed(1)} / 5`} accent="linear-gradient(180deg, #fbbf24, #f59e0b)" />
      </SimpleGrid>

      {recommended.length > 0 ? (
        <Flex direction="column" gap={4}>
          <Flex justifyContent="space-between" alignItems="center" gap={3} flexWrap="wrap">
            <Flex alignItems="center" gap={3}>
              <Box w={1.5} h={6} bg="linear-gradient(180deg, #667eea 0%, #764ba2 100%)" borderRadius="full" />
              <Text fontSize="lg" fontWeight="700" color="gray.800" letterSpacing="-0.02em">
                Top picks for you
              </Text>
            </Flex>
            <Flex role="group" aria-label="Sort picks by" gap={1.5} flexWrap="wrap" bg="gray.100" p={1} borderRadius="full">
              {SORT_OPTIONS.map((option) => {
                const active = option.key === sort
                return (
                  <Box
                    key={option.key}
                    as="button"
                    onClick={() => setSort(option.key)}
                    aria-pressed={active}
                    px={3.5}
                    py={1.5}
                    borderRadius="full"
                    fontSize="xs"
                    fontWeight="700"
                    cursor="pointer"
                    color={active ? 'white' : 'gray.600'}
                    bg={active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent'}
                    boxShadow={active ? '0 4px 12px rgba(102, 126, 234, 0.35)' : 'none'}
                    css={{ transition: 'background 0.2s ease, color 0.2s ease' }}
                    _hover={{ color: active ? 'white' : 'gray.800' }}
                    _focusVisible={{ outline: '3px solid rgba(102, 126, 234, 0.5)', outlineOffset: '2px' }}
                  >
                    {option.label}
                  </Box>
                )
              })}
            </Flex>
          </Flex>

          <SimpleGrid columns={{ base: 1, md: 2 }} gap={5} alignItems="stretch">
            {sorted.map((product, index) => (
              <ProductCard key={product.url} product={product} rank={index} highlightTop={sort === 'best'} />
            ))}
          </SimpleGrid>
        </Flex>
      ) : (
        <Box bg="#fffbeb" borderWidth="1px" borderColor="#fde68a" borderRadius="20px" px={5} py={4} role="status">
          <Text fontSize="sm" fontWeight="700" color="#92400e">No recommendation this time</Text>
          <Text fontSize="sm" color="#92400e" mt={1}>
            Nothing passed the seller checks within your request. Try a higher budget or a different description.
          </Text>
        </Box>
      )}

      <FlaggedList products={flagged} />

      <Text fontSize="xs" color="gray.500" lineHeight="1.6">
        Risk levels summarise the evidence found. They are not a guarantee that a seller or product is legitimate, so the final decision is yours.
      </Text>
    </Flex>
  )
}
