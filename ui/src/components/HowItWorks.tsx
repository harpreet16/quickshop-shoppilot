'use client'

import { Box, Flex, SimpleGrid, Text } from '@chakra-ui/react'
import { motion } from 'framer-motion'
import { EASE, fonts, palette } from '@/theme/palette'
import { Icon, type IconName } from './Icon'

const STEPS = [
  { title: 'Search retailers', body: 'Finds listings that match your request and your budget across online stores.' },
  { title: 'Vet the seller', body: 'Checks brand recognition, how long the site has existed, outside reviews and the return policy.' },
  { title: 'Read the fabric', body: 'Opens the most promising product pages to read the stated fabric composition.' },
  { title: 'Score and rank', body: 'Rates price, quality and seller trust out of 5. A low price never outweighs a weak seller.' },
]

const PRINCIPLES: { icon: IconName; title: string; body: string }[] = [
  { icon: 'leaf', title: 'Natural fibers first', body: 'Quality means cotton, linen, silk and wool, read from the product page.' },
  { icon: 'shield', title: 'Trust before price', body: 'Sellers that fail the legitimacy check are never recommended.' },
  { icon: 'help', title: 'Honest about gaps', body: 'When a fabric or seller cannot be confirmed, it is marked unknown.' },
]

export function HowItWorks() {
  return (
    <Box as="section" px={{ base: 5, md: 10 }} py={{ base: 16, md: 24 }}>
      <Box maxW="1120px" mx="auto">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <Text fontSize="11px" fontWeight="700" letterSpacing="0.26em" textTransform="uppercase" color={palette.brassText}>
            How it works
          </Text>
          <Text
            as="h2"
            mt={4}
            maxW="640px"
            fontFamily={fonts.display}
            fontSize={{ base: '34px', md: '48px' }}
            fontWeight="500"
            lineHeight="1.08"
            letterSpacing="-0.015em"
            color={palette.ink}
          >
            Four checks before anything is <Box as="span" fontStyle="italic">recommended.</Box>
          </Text>
        </motion.div>

        <SimpleGrid columns={{ base: 1, sm: 2, lg: 4 }} gap={0} mt={{ base: 10, md: 14 }} borderTopWidth="1px" borderColor={palette.ink}>
          {STEPS.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.7, delay: index * 0.09, ease: EASE }}
            >
              <Box
                h="100%"
                pt={7}
                pb={9}
                pr={{ base: 0, lg: 8 }}
                pl={{ base: 0, lg: index === 0 ? 0 : 8 }}
                borderLeftWidth={{ base: 0, lg: index === 0 ? 0 : '1px' }}
                borderBottomWidth={{ base: '1px', lg: 0 }}
                borderColor={palette.hairline}
              >
                <Text fontFamily={fonts.display} fontStyle="italic" fontSize="46px" fontWeight="500" lineHeight="1" color={palette.brass}>
                  {String(index + 1).padStart(2, '0')}
                </Text>
                <Text mt={5} fontSize="17px" fontWeight="700" color={palette.ink} letterSpacing="-0.005em">
                  {step.title}
                </Text>
                <Text mt={2.5} fontSize="14.5px" lineHeight="1.7" color={palette.textSecondary}>
                  {step.body}
                </Text>
              </Box>
            </motion.div>
          ))}
        </SimpleGrid>

        <SimpleGrid columns={{ base: 1, md: 3 }} gap={{ base: 6, md: 10 }} mt={{ base: 10, md: 16 }} pt={{ base: 8, md: 12 }} borderTopWidth="1px" borderColor={palette.hairline}>
          {PRINCIPLES.map((item, index) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ duration: 0.6, delay: index * 0.08, ease: EASE }}
            >
              <Flex gap={4} alignItems="flex-start">
                <Flex
                  w="40px"
                  h="40px"
                  flexShrink={0}
                  borderRadius="full"
                  borderWidth="1px"
                  borderColor={palette.hairlineStrong}
                  alignItems="center"
                  justifyContent="center"
                  color={palette.ink}
                >
                  <Icon name={item.icon} size={18} />
                </Flex>
                <Box>
                  <Text fontSize="15px" fontWeight="700" color={palette.ink}>{item.title}</Text>
                  <Text mt={1.5} fontSize="14px" lineHeight="1.65" color={palette.textSecondary}>{item.body}</Text>
                </Box>
              </Flex>
            </motion.div>
          ))}
        </SimpleGrid>
      </Box>
    </Box>
  )
}
