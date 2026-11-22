'use client'

import { useMemo, useState } from 'react'
import { Box, Flex, SimpleGrid, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { SORT_OPTIONS, formatPrice, sortProducts, splitProducts, type SortKey } from '@/lib/results'
import { EASE, fonts, palette } from '@/theme/palette'
import { FlaggedList } from './FlaggedList'
import { ProductCard } from './ProductCard'
import type { ScoredProduct } from '@/types'

interface ResultsDashboardProps {
  products: ScoredProduct[]
}

interface StatProps {
  label: string
  value: string
  index: number
  last?: boolean
}

function Stat({ label, value, index, last }: StatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.07, ease: EASE }}
    >
      <Box
        px={{ base: 4, md: 6 }}
        py={5}
        borderRightWidth={{ base: index % 2 === 0 ? '1px' : 0, md: last ? 0 : '1px' }}
        borderBottomWidth={{ base: index < 2 ? '1px' : 0, md: 0 }}
        borderColor={palette.hairline}
        h="100%"
      >
        <Text fontSize="10.5px" fontWeight="700" letterSpacing="0.2em" textTransform="uppercase" color={palette.textSecondary}>
          {label}
        </Text>
        <Text mt={2} className="tabular" fontSize={{ base: '26px', md: '30px' }} fontWeight="500" letterSpacing="-0.03em" lineHeight="1" color={palette.ink}>
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

  const useFeatured = sort === 'best' && sorted.length > 0
  const featuredProduct = useFeatured ? sorted[0] : null
  const gridProducts = useFeatured ? sorted.slice(1) : sorted

  return (
    <Flex direction="column" gap={{ base: 8, md: 10 }} w="100%" minW={0}>
      <Box
        borderTopWidth="1px"
        borderBottomWidth="1px"
        borderColor={palette.ink}
        bg="rgba(255, 255, 255, 0.4)"
      >
        <SimpleGrid columns={{ base: 2, md: 4 }} gap={0}>
          <Stat index={0} label="Recommended" value={String(recommended.length)} />
          <Stat index={1} label="Not recommended" value={String(flagged.length)} />
          <Stat index={2} label="Lowest price" value={lowestPrice == null ? '—' : formatPrice(lowestPrice)} />
          <Stat index={3} label="Top score" value={topScore == null ? '—' : `${topScore.toFixed(1)} / 5`} last />
        </SimpleGrid>
      </Box>

      {recommended.length > 0 ? (
        <Flex direction="column" gap={6}>
          <Flex justifyContent="space-between" alignItems="flex-end" gap={5} flexWrap="wrap">
            <Box>
              <Text fontSize="11px" fontWeight="700" letterSpacing="0.26em" textTransform="uppercase" color={palette.brassText}>
                Results
              </Text>
              <Text as="h2" mt={2} fontFamily={fonts.display} fontSize={{ base: '32px', md: '42px' }} fontWeight="500" lineHeight="1.05" letterSpacing="-0.015em" color={palette.ink}>
                Recommended <Box as="span" fontStyle="italic">for you</Box>
              </Text>
            </Box>

            <Flex role="group" aria-label="Sort recommendations by" gap={{ base: 4, md: 6 }} flexWrap="wrap">
              {SORT_OPTIONS.map((option) => {
                const active = option.key === sort
                return (
                  <Box
                    key={option.key}
                    as="button"
                    onClick={() => setSort(option.key)}
                    aria-pressed={active}
                    pb={1.5}
                    fontSize="13px"
                    fontWeight={active ? 700 : 500}
                    color={active ? palette.ink : palette.textSecondary}
                    borderBottomWidth="2px"
                    borderColor={active ? palette.brass : 'transparent'}
                    cursor="pointer"
                    css={{ transition: 'color 0.2s ease, border-color 0.2s ease', '&:hover': { color: palette.ink } }}
                  >
                    {option.label}
                  </Box>
                )
              })}
            </Flex>
          </Flex>

          {featuredProduct && <ProductCard key={featuredProduct.url} product={featuredProduct} rank={0} featured />}

          {gridProducts.length > 0 && (
            <SimpleGrid columns={{ base: 1, md: 2 }} gap={5} alignItems="stretch">
              {gridProducts.map((product, index) => (
                <ProductCard key={product.url} product={product} rank={useFeatured ? index + 1 : index} featured={false} />
              ))}
            </SimpleGrid>
          )}
        </Flex>
      ) : (
        <Box bg={palette.cautionSoft} borderWidth="1px" borderColor="#e6d3a6" borderRadius="10px" px={6} py={5} role="status">
          <Text fontFamily={fonts.display} fontSize="24px" fontWeight="600" color={palette.caution}>No recommendation this time</Text>
          <Text mt={1.5} fontSize="14.5px" lineHeight="1.65" color={palette.caution}>
            Nothing passed the seller checks within your request. Try a higher budget or a different description.
          </Text>
        </Box>
      )}

      <FlaggedList products={flagged} />

      <Text fontSize="12.5px" color={palette.textSecondary} lineHeight="1.65" maxW="720px">
        Risk levels summarise the evidence found. They are not a guarantee that a seller or product is legitimate, so the final decision is yours.
      </Text>
    </Flex>
  )
}
