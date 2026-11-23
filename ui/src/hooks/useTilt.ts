'use client'

import { useCallback, useMemo, type PointerEvent } from 'react'
import { useMotionTemplate, useMotionValue, useReducedMotion, useSpring, useTransform } from 'framer-motion'

const SPRING = { stiffness: 220, damping: 22, mass: 0.6 }

// Pointer-driven 3D tilt. px/py are the pointer position over the card, 0..1 (0.5 = centre).
// Returns motion values to spread into a motion element's style, plus the pointer handlers.
// Touch input and "reduce motion" users get a flat card: the handlers do nothing.
export function useTilt(maxDeg = 7) {
  const reduce = useReducedMotion()
  const px = useMotionValue(0.5)
  const py = useMotionValue(0.5)

  const rotateY = useSpring(useTransform(px, [0, 1], [-maxDeg, maxDeg]), SPRING)
  const rotateX = useSpring(useTransform(py, [0, 1], [maxDeg, -maxDeg]), SPRING)

  // photo drifts slightly against the tilt, which reads as depth
  const shiftX = useSpring(useTransform(px, [0, 1], [10, -10]), SPRING)
  const shiftY = useSpring(useTransform(py, [0, 1], [8, -8]), SPRING)

  // shadow falls away from the light, so it moves opposite to the tilt
  const shadowX = useTransform(rotateY, (v) => -v * 2.4)
  const shadowY = useTransform(rotateX, (v) => 20 + v * 2.4)
  const boxShadow = useMotionTemplate`${shadowX}px ${shadowY}px 46px rgba(15, 27, 45, 0.15)`

  const glareX = useTransform(px, (v) => v * 100)
  const glareY = useTransform(py, (v) => v * 100)
  const glare = useMotionTemplate`radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255, 255, 255, 0.38), rgba(255, 255, 255, 0) 55%)`
  const glareOpacity = useSpring(0, { stiffness: 160, damping: 24 })

  const onPointerMove = useCallback(
    (event: PointerEvent<HTMLElement>) => {
      if (reduce || event.pointerType !== 'mouse') return
      const box = event.currentTarget.getBoundingClientRect()
      px.set((event.clientX - box.left) / box.width)
      py.set((event.clientY - box.top) / box.height)
      glareOpacity.set(1)
    },
    [reduce, px, py, glareOpacity],
  )

  const onPointerLeave = useCallback(() => {
    px.set(0.5)
    py.set(0.5)
    glareOpacity.set(0)
  }, [px, py, glareOpacity])

  return useMemo(
    () => ({ enabled: !reduce, rotateX, rotateY, shiftX, shiftY, boxShadow, glare, glareOpacity, onPointerMove, onPointerLeave }),
    [reduce, rotateX, rotateY, shiftX, shiftY, boxShadow, glare, glareOpacity, onPointerMove, onPointerLeave],
  )
}
