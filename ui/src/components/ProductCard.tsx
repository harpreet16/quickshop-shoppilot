'use client'

import { Box, Flex, Text, Image, Link } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import type { Product } from '@/types'

interface ProductCardProps {
  product: Product
  index: number
}

export function ProductCard({ product, index }: ProductCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -12, scale: 1.02 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: [0.22, 1, 0.36, 1] }}
      style={{ height: '100%' }}
    >
      <Link
        href={product.url}
        target="_blank"
        rel="noopener noreferrer"
        display="block"
        h="100%"
        _hover={{ textDecoration: 'none' }}
      >
        <Box
          h="100%"
          bg="white"
          borderRadius="24px"
          overflow="hidden"
          boxShadow="0 4px 20px rgba(0,0,0,0.06)"
          borderWidth="1px"
          borderColor="gray.100"
          _hover={{
            boxShadow: '0 25px 50px rgba(102, 126, 234, 0.15), 0 12px 24px rgba(0,0,0,0.08)',
            borderColor: 'transparent',
          }}
          css={{
            transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          }}
          position="relative"
        >
          <Box
            position="absolute"
            top={0}
            left={0}
            right={0}
            h="4px"
            bg="linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"
            opacity={0}
            css={{ transition: 'opacity 0.3s ease' }}
            _groupHover={{ opacity: 1 }}
            className="card-accent"
          />

          <Box position="relative" h={52} bg="gray.50" overflow="hidden">
            {product.image ? (
              <Image
                src={product.image}
                alt={product.title}
                objectFit="cover"
                w="100%"
                h="100%"
                css={{ transition: 'transform 0.4s ease' }}
                _hover={{ transform: 'scale(1.08)' }}
              />
            ) : (
              <Flex
                h="100%"
                alignItems="center"
                justifyContent="center"
                bg="linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(240, 147, 251, 0.05) 100%)"
              >
                <Text fontSize="5xl">👗</Text>
              </Flex>
            )}

            <Box
              position="absolute"
              top={3}
              left={3}
              bg="white"
              px={3}
              py={1.5}
              borderRadius="full"
              fontSize="xs"
              fontWeight="700"
              color="gray.700"
              boxShadow="0 2px 10px rgba(0,0,0,0.1)"
              textTransform="uppercase"
              letterSpacing="0.05em"
            >
              {product.source}
            </Box>

            {product.rating && (
              <Flex
                position="absolute"
                top={3}
                right={3}
                bg="white"
                px={2.5}
                py={1.5}
                borderRadius="full"
                alignItems="center"
                gap={1}
                boxShadow="0 2px 10px rgba(0,0,0,0.1)"
              >
                <Text color="yellow.500" fontSize="sm">★</Text>
                <Text fontSize="xs" fontWeight="700" color="gray.700">
                  {product.rating.toFixed(1)}
                </Text>
              </Flex>
            )}
          </Box>

          <Box p={5}>
            <Text
              fontWeight="600"
              fontSize="sm"
              color="gray.800"
              lineClamp={2}
              minH={10}
              mb={4}
              lineHeight="1.5"
            >
              {product.title}
            </Text>

            <Flex alignItems="center" justifyContent="space-between">
              <Box>
                <Text
                  fontSize="2xl"
                  fontWeight="800"
                  className="gradient-text"
                  lineHeight="1"
                >
                  ${product.price.toFixed(2)}
                </Text>
              </Box>
              <Flex
                alignItems="center"
                gap={2}
                px={4}
                py={2}
                bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                borderRadius="full"
                boxShadow="0 4px 15px rgba(102, 126, 234, 0.35)"
                color="white"
                fontSize="sm"
                fontWeight="600"
                _hover={{
                  transform: 'scale(1.05)',
                }}
                css={{ transition: 'transform 0.2s ease' }}
              >
                View
                <Text>→</Text>
              </Flex>
            </Flex>
          </Box>
        </Box>
      </Link>
    </motion.div>
  )
}
