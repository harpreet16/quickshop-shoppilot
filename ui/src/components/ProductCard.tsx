'use client'

import { useState } from 'react'
import { Box, Flex, Link, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { evidenceGlyph, fabricLabel, formatPrice, parseEvidence } from '@/lib/results'
import { EASE, fonts, palette } from '@/theme/palette'
import { Icon } from './Icon'
import { RiskTag } from './RiskTag'
import { ScoreMeter } from './ScoreMeter'
import type { ScoredProduct } from '@/types'

const VISIBLE_EVIDENCE = 3

interface ProductCardProps {
  product: ScoredProduct
  rank: number
  featured: boolean
}

export function ProductCard({ product, rank, featured }: ProductCardProps) {
  const [showAll, setShowAll] = useState(false)
  const evidence = product.evidence.map(parseEvidence)
  const visible = showAll ? evidence : evidence.slice(0, VISIBLE_EVIDENCE)
  const hiddenCount = evidence.length - VISIBLE_EVIDENCE
  const overall = product.scores.overall
  const ratingText =
    product.rating != null
      ? `${product.rating.toFixed(1)}${product.reviews != null ? ` · ${product.reviews.toLocaleString()} reviews` : ''}`
      : null

  const cta = (
    <Link
      href={product.url}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`View listing for ${product.title} (opens in a new tab)`}
      display="inline-flex"
      alignItems="center"
      justifyContent="center"
      gap={2.5}
      w={featured ? 'auto' : '100%'}
      px={6}
      py={3.5}
      borderRadius="8px"
      borderWidth="1px"
      borderColor={palette.ink}
      color={palette.ink}
      fontSize="14px"
      fontWeight="700"
      letterSpacing="0.02em"
      css={{
        transition: 'background 0.25s ease, color 0.25s ease',
        '&:hover': { background: palette.ink, color: palette.paper, textDecoration: 'none' },
        '&:focus-visible': { outline: `2px solid ${palette.ink}`, outlineOffset: '3px' },
      }}
    >
      View listing
      <Icon name="arrowUpRight" size={16} strokeWidth={1.8} />
    </Link>
  )

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 26 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -3 }}
      transition={{ duration: 0.6, delay: Math.min(rank, 5) * 0.08, ease: EASE }}
      style={{ height: '100%' }}
      aria-label={`${product.title}, ${formatPrice(product.price)}, sold by ${product.merchant}`}
    >
      <Flex
        direction={featured ? { base: 'column', md: 'row' } : 'column'}
        h="100%"
        bg={palette.surface}
        borderWidth="1px"
        borderColor={featured ? palette.ink : palette.hairline}
        borderRadius="10px"
        overflow="hidden"
        position="relative"
        minW={0}
        css={{
          transition: 'box-shadow 0.35s ease, border-color 0.35s ease',
          '&:hover': { boxShadow: '0 22px 48px rgba(15, 27, 45, 0.11)', borderColor: palette.ink },
        }}
      >
        {featured && <Box position="absolute" top={0} left={0} right={0} h="3px" bg={palette.brass} />}

        <Flex direction="column" gap={5} p={{ base: 5, md: featured ? 8 : 6 }} flex={featured ? '1.15' : undefined} minW={0}>
          <Flex justifyContent="space-between" alignItems="center" gap={3}>
            <Flex alignItems="baseline" gap={3}>
              <Text fontFamily={fonts.display} fontStyle="italic" fontSize="34px" fontWeight="500" lineHeight="1" color={palette.brass}>
                {String(rank + 1).padStart(2, '0')}
              </Text>
              {featured && (
                <Text fontSize="10.5px" fontWeight="700" letterSpacing="0.22em" textTransform="uppercase" color={palette.brassText}>
                  Our pick
                </Text>
              )}
            </Flex>
            <RiskTag risk={product.risk} />
          </Flex>

          <Box minW={0}>
            <Text fontSize="11px" fontWeight="700" letterSpacing="0.18em" textTransform="uppercase" color={palette.textSecondary}>
              {product.merchant}
            </Text>
            <Text
              as="h3"
              mt={2}
              fontFamily={fonts.display}
              fontSize={featured ? { base: '27px', md: '33px' } : '24px'}
              fontWeight="500"
              lineHeight="1.15"
              letterSpacing="-0.01em"
              color={palette.ink}
              lineClamp={3}
              overflowWrap="anywhere"
            >
              {product.title}
            </Text>
          </Box>

          <Flex alignItems="baseline" gap={4} flexWrap="wrap">
            <Text className="tabular" fontSize="26px" fontWeight="600" letterSpacing="-0.02em" color={palette.ink} lineHeight="1">
              {formatPrice(product.price)}
            </Text>
            {ratingText && (
              <Text className="tabular" fontSize="13px" color={palette.textSecondary}>
                <Text as="span" color={palette.brass} aria-hidden="true">★ </Text>
                {ratingText}
              </Text>
            )}
          </Flex>

          <Flex alignItems="center" gap={2.5} color={palette.textSecondary} fontSize="14px">
            <Icon name="layers" size={17} />
            <Text fontWeight="500">{fabricLabel(product)}</Text>
          </Flex>

          {featured && <Box mt={{ base: 1, md: 'auto' }}>{cta}</Box>}
        </Flex>

        <Flex
          direction="column"
          gap={5}
          p={{ base: 5, md: featured ? 8 : 6 }}
          pt={{ base: 5, md: featured ? 8 : 5 }}
          flex={featured ? 1 : 1}
          minW={0}
          borderTopWidth={{ base: '1px', md: featured ? 0 : '1px' }}
          borderLeftWidth={{ base: 0, md: featured ? '1px' : 0 }}
          borderColor={palette.hairline}
          bg={featured ? 'rgba(255, 255, 255, 0.55)' : 'transparent'}
        >
          <Flex alignItems="flex-end" justifyContent="space-between" gap={4}>
            <Text fontSize="10.5px" fontWeight="700" letterSpacing="0.2em" textTransform="uppercase" color={palette.textSecondary}>
              Overall score
            </Text>
            <Flex alignItems="baseline" gap={1.5} role="img" aria-label={overall == null ? 'Overall score not available' : `Overall score ${overall.toFixed(1)} out of 5`}>
              <Text className="tabular" fontSize="46px" fontWeight="300" letterSpacing="-0.04em" lineHeight="0.9" color={palette.ink}>
                {overall == null ? '–' : overall.toFixed(1)}
              </Text>
              <Text fontSize="14px" color={palette.textMuted}>/ 5</Text>
            </Flex>
          </Flex>

          <Flex direction="column" gap={3}>
            <ScoreMeter label="Price" value={product.scores.price} delay={0.1} />
            <ScoreMeter label="Quality" value={product.scores.quality} delay={0.2} />
            <ScoreMeter label="Seller trust" value={product.scores.legitimacy} delay={0.3} />
          </Flex>

          {evidence.length > 0 && (
            <Box>
              <Text fontSize="10.5px" fontWeight="700" letterSpacing="0.2em" textTransform="uppercase" color={palette.textSecondary} mb={3}>
                Evidence
              </Text>
              <Flex as="ul" direction="column" listStyleType="none" m={0} p={0}>
                {visible.map((entry, index) => {
                  const glyph = evidenceGlyph(entry.tone)
                  return (
                    <Flex
                      as="li"
                      key={`${entry.text}-${index}`}
                      gap={3}
                      alignItems="flex-start"
                      py={2.5}
                      borderTopWidth={index === 0 ? 0 : '1px'}
                      borderColor={palette.hairline}
                    >
                      <Box color={glyph.color} mt="2px">
                        <Icon name={glyph.icon} size={15} strokeWidth={2} />
                      </Box>
                      <Text fontSize="13.5px" lineHeight="1.55" color={palette.text} overflowWrap="anywhere">
                        {entry.text}
                      </Text>
                    </Flex>
                  )
                })}
              </Flex>
              {hiddenCount > 0 && (
                <Box
                  as="button"
                  onClick={() => setShowAll((value) => !value)}
                  mt={2}
                  display="inline-flex"
                  alignItems="center"
                  gap={1.5}
                  fontSize="12.5px"
                  fontWeight="700"
                  color={palette.brassText}
                  cursor="pointer"
                  aria-expanded={showAll}
                  css={{ '&:hover': { textDecoration: 'underline', textUnderlineOffset: '3px' } }}
                >
                  <Icon name={showAll ? 'minus' : 'plus'} size={13} strokeWidth={2} />
                  {showAll ? 'Show less' : `Show ${hiddenCount} more`}
                </Box>
              )}
            </Box>
          )}

          {!featured && <Box mt="auto" pt={1}>{cta}</Box>}
        </Flex>
      </Flex>
    </motion.article>
  )
}
