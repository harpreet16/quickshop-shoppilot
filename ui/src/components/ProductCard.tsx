'use client'

import { useState } from 'react'
import { Box, Flex, Link, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { fabricLabel, formatPrice, parseEvidence, type EvidenceTone } from '@/lib/results'
import { RiskPill } from './RiskPill'
import { ScoreBar } from './ScoreBar'
import { ScoreRing } from './ScoreRing'
import type { ScoredProduct } from '@/types'

const CHIP_STYLE: Record<EvidenceTone, { bg: string; fg: string; border: string; icon: string }> = {
  good: { bg: '#ecfdf3', fg: '#166534', border: '#bbf7d0', icon: '✓' },
  warn: { bg: '#fffbeb', fg: '#92400e', border: '#fde68a', icon: '!' },
  unknown: { bg: '#f1f5f9', fg: '#475569', border: '#e2e8f0', icon: '?' },
  bad: { bg: '#fef2f2', fg: '#991b1b', border: '#fecaca', icon: '×' },
  neutral: { bg: '#f5f6ff', fg: '#3f4cb8', border: '#dfe3ff', icon: '•' },
}

const VISIBLE_EVIDENCE = 4

interface ProductCardProps {
  product: ScoredProduct
  rank: number
  highlightTop: boolean
}

export function ProductCard({ product, rank, highlightTop }: ProductCardProps) {
  const [showAll, setShowAll] = useState(false)
  const evidence = product.evidence.map(parseEvidence)
  const visible = showAll ? evidence : evidence.slice(0, VISIBLE_EVIDENCE)
  const hiddenCount = evidence.length - VISIBLE_EVIDENCE
  const isTop = highlightTop && rank === 0
  const ratingText =
    product.rating != null
      ? `${product.rating.toFixed(1)} rating${product.reviews != null ? ` · ${product.reviews.toLocaleString()} reviews` : ''}`
      : null

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.45, delay: Math.min(rank, 5) * 0.07, ease: [0.22, 1, 0.36, 1] }}
      style={{ height: '100%' }}
      aria-label={`${product.title}, ${formatPrice(product.price)}, sold by ${product.merchant}`}
    >
      <Flex
        direction="column"
        h="100%"
        bg="white"
        borderRadius="24px"
        p={5}
        gap={4}
        borderWidth="1px"
        borderColor={isTop ? 'rgba(102, 126, 234, 0.45)' : 'gray.100'}
        boxShadow={isTop ? '0 18px 45px rgba(102, 126, 234, 0.18)' : '0 4px 20px rgba(15, 23, 42, 0.06)'}
        position="relative"
        overflow="hidden"
        minW={0}
        css={{ transition: 'box-shadow 0.3s ease, border-color 0.3s ease' }}
        _hover={{ boxShadow: '0 22px 50px rgba(102, 126, 234, 0.2)', borderColor: 'rgba(102, 126, 234, 0.35)' }}
      >
        {isTop && <Box position="absolute" top={0} left={0} right={0} h="4px" bg="linear-gradient(90deg, #667eea, #764ba2, #f093fb)" />}

        <Flex justifyContent="space-between" alignItems="center" gap={2} flexWrap="wrap">
          <Flex alignItems="center" gap={2}>
            <Flex
              w={7}
              h={7}
              borderRadius="full"
              alignItems="center"
              justifyContent="center"
              fontSize="xs"
              fontWeight="800"
              color={isTop ? 'white' : 'gray.600'}
              bg={isTop ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'gray.100'}
              aria-hidden="true"
            >
              {rank + 1}
            </Flex>
            {isTop && (
              <Text fontSize="xs" fontWeight="700" color="#5b6ee1" textTransform="uppercase" letterSpacing="0.06em">
                Best match
              </Text>
            )}
          </Flex>
          <RiskPill risk={product.risk} />
        </Flex>

        <Box minW={0}>
          <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="0.06em" mb={1}>
            {product.merchant}
          </Text>
          <Text fontSize="md" fontWeight="700" color="gray.800" lineHeight="1.4" lineClamp={2} overflowWrap="anywhere">
            {product.title}
          </Text>
        </Box>

        <Flex alignItems="baseline" justifyContent="space-between" gap={3} flexWrap="wrap">
          <Text fontSize="2xl" fontWeight="800" lineHeight="1" className="gradient-text">
            {formatPrice(product.price)}
          </Text>
          {ratingText && (
            <Text fontSize="xs" color="gray.500" fontWeight="500">
              <Text as="span" color="#d97706" aria-hidden="true">★ </Text>
              {ratingText}
            </Text>
          )}
        </Flex>

        <Flex alignItems="center" gap={5} py={4} borderTopWidth="1px" borderBottomWidth="1px" borderColor="gray.100">
          <ScoreRing value={product.scores.overall} />
          <Flex direction="column" gap={2.5} flex={1} minW={0}>
            <ScoreBar label="Price" value={product.scores.price} delay={0.1} />
            <ScoreBar label="Quality" value={product.scores.quality} delay={0.2} />
            <ScoreBar label="Seller trust" value={product.scores.legitimacy} delay={0.3} />
          </Flex>
        </Flex>

        <Flex alignItems="center" gap={2} fontSize="sm" color="gray.600" fontWeight="500">
          <Text aria-hidden="true">🧵</Text>
          <Text>{fabricLabel(product)}</Text>
        </Flex>

        {evidence.length > 0 && (
          <Flex direction="column" gap={2}>
            <Text fontSize="xs" fontWeight="700" color="gray.500" textTransform="uppercase" letterSpacing="0.06em">
              Why this score
            </Text>
            <Flex gap={1.5} flexWrap="wrap" as="ul" listStyleType="none" p={0} m={0}>
              {visible.map((entry, index) => {
                const style = CHIP_STYLE[entry.tone]
                return (
                  <Flex
                    as="li"
                    key={`${entry.text}-${index}`}
                    alignItems="flex-start"
                    gap={1.5}
                    px={2.5}
                    py={1}
                    borderRadius="12px"
                    borderWidth="1px"
                    bg={style.bg}
                    color={style.fg}
                    borderColor={style.border}
                    fontSize="xs"
                    fontWeight="600"
                    lineHeight="1.4"
                    minW={0}
                  >
                    <Text as="span" aria-hidden="true" fontWeight="800">{style.icon}</Text>
                    <Text as="span" overflowWrap="anywhere">{entry.text}</Text>
                  </Flex>
                )
              })}
            </Flex>
            {hiddenCount > 0 && (
              <Box
                as="button"
                onClick={() => setShowAll((value) => !value)}
                alignSelf="flex-start"
                fontSize="xs"
                fontWeight="700"
                color="#5b6ee1"
                px={1}
                py={0.5}
                borderRadius="md"
                cursor="pointer"
                aria-expanded={showAll}
                _hover={{ textDecoration: 'underline' }}
                _focusVisible={{ outline: '3px solid rgba(102, 126, 234, 0.5)', outlineOffset: '2px' }}
              >
                {showAll ? 'Show fewer' : `Show ${hiddenCount} more`}
              </Box>
            )}
          </Flex>
        )}

        <Link
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`View listing for ${product.title} (opens in a new tab)`}
          mt="auto"
          display="flex"
          alignItems="center"
          justifyContent="center"
          gap={2}
          py={3}
          borderRadius="14px"
          bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          color="white"
          fontSize="sm"
          fontWeight="700"
          boxShadow="0 8px 20px rgba(102, 126, 234, 0.3)"
          _hover={{ textDecoration: 'none', opacity: 0.92, transform: 'translateY(-1px)' }}
          _focusVisible={{ outline: '3px solid rgba(102, 126, 234, 0.5)', outlineOffset: '2px' }}
          css={{ transition: 'transform 0.2s ease, opacity 0.2s ease' }}
        >
          View listing
          <Text as="span" aria-hidden="true">↗</Text>
        </Link>
      </Flex>
    </motion.article>
  )
}
