'use client'

import { SimpleGrid, Box, Text, Flex } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { ProductCard } from './ProductCard'
import type { Product } from '@/types'

interface ProductGridProps {
  products: Product[]
}

export function ProductGrid({ products }: ProductGridProps) {
  if (products.length === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Flex alignItems="center" gap={3} mb={5}>
        <Box
          w={1.5}
          h={6}
          bg="linear-gradient(180deg, #667eea 0%, #764ba2 100%)"
          borderRadius="full"
        />
        <Text
          fontSize="sm"
          fontWeight="700"
          color="gray.700"
          textTransform="uppercase"
          letterSpacing="0.05em"
        >
          {products.length} item{products.length !== 1 ? 's' : ''} found
        </Text>
      </Flex>
      <SimpleGrid
        columns={{ base: 1, sm: 2, lg: 3 }}
        gap={5}
      >
        {products.map((product, index) => (
          <ProductCard key={`${product.url}-${index}`} product={product} index={index} />
        ))}
      </SimpleGrid>
    </motion.div>
  )
}
