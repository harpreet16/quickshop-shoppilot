'use client'

import { useEffect, useRef, useState } from 'react'
import { Box, Flex, Image, Text } from '@chakra-ui/react'
import { motion, type MotionValue } from 'framer-motion'
import { palette } from '@/theme/palette'
import { Icon } from './Icon'

interface ProductImageProps {
  src: string
  alt: string
  // hero: full-height column on the featured card. thumb: portrait thumbnail beside a regular card's details.
  variant: 'hero' | 'thumb'
  // optional parallax: the photo drifts by these offsets (px) inside its frame
  shiftX?: MotionValue<number>
  shiftY?: MotionValue<number>
}

const unavailable = (
  <Flex
    direction="column"
    alignItems="center"
    justifyContent="center"
    gap={2}
    w="100%"
    h="100%"
    color={palette.textMuted}
    role="img"
    aria-label="Product photo unavailable"
  >
    <Icon name="layers" size={24} strokeWidth={1.4} />
    <Text fontSize="11px" letterSpacing="0.1em" textTransform="uppercase" textAlign="center" px={2}>
      Photo unavailable
    </Text>
  </Flex>
)

// Product photos come from third-party shop CDNs. If one fails to load (hotlink block, expired link),
// show a quiet placeholder instead of a broken-image icon.
export function ProductImage({ src, alt, variant, shiftX, shiftY }: ProductImageProps) {
  const [failed, setFailed] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)
  // 'cover' fills the frame (best for portrait photos). Wide or very small photos would be cropped badly
  // or blown up blurry, so those are shown whole ('contain') on a soft background instead.
  const [fit, setFit] = useState<'cover' | 'contain'>('cover')

  const judge = (img: HTMLImageElement) => {
    if (!img.naturalWidth || !img.naturalHeight) return
    const ratio = img.naturalWidth / img.naturalHeight
    setFit(ratio < 0.55 || ratio > 1.0 || img.naturalWidth < 300 ? 'contain' : 'cover')
  }

  // A broken image can finish failing before React attaches onError (server-rendered or cached pages),
  // so also check once after mount.
  useEffect(() => {
    const img = imgRef.current
    if (img && img.complete && img.naturalWidth === 0) setFailed(true)
    else if (img && img.complete) judge(img)
  }, [src])
  const hero = variant === 'hero'

  const photo = failed ? (
    unavailable
  ) : (
    <motion.div
      // when cropping ('cover') the photo is scaled up a little so the parallax drift never exposes the frame's edge
      style={{ position: 'absolute', inset: 0, x: fit === 'cover' ? shiftX : 0, y: fit === 'cover' ? shiftY : 0, scale: fit === 'cover' && shiftX ? 1.08 : 1 }}
    >
      <Image
        ref={imgRef}
        // plain <img> (not next/image): arbitrary third-party shop hosts, so a host allow-list cannot apply
        src={src}
        alt={alt}
        loading="lazy"
        referrerPolicy="no-referrer"
        onError={() => setFailed(true)}
        onLoad={(event) => judge(event.currentTarget)}
        w="100%"
        h="100%"
        objectFit={fit}
        objectPosition={fit === 'cover' ? 'center top' : 'center'}
        p={fit === 'contain' ? 3 : 0}
      />
    </motion.div>
  )

  if (hero) {
    return (
      <Box
        position="relative"
        flex={{ base: 'none', md: '0 0 clamp(260px, 31%, 380px)' }}
        h={{ base: '360px', md: 'auto' }}
        minH={{ md: '440px' }}
        bg={palette.paperDeep}
        borderBottomWidth={{ base: '1px', md: 0 }}
        borderRightWidth={{ base: 0, md: '1px' }}
        borderColor={palette.hairline}
        overflow="hidden"
      >
        {photo}
      </Box>
    )
  }

  return (
    <Box
      position="relative"
      flex="none"
      w={{ base: '112px', sm: '140px', md: '160px' }}
      aspectRatio="3 / 4"
      bg={palette.paperDeep}
      borderWidth="1px"
      borderColor={palette.hairline}
      borderRadius="8px"
      overflow="hidden"
    >
      {photo}
    </Box>
  )
}
