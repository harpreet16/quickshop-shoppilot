import type { Metadata } from 'next'
import { Cormorant_Garamond, Hanken_Grotesk } from 'next/font/google'
import { ChakraProvider } from '@/components/ChakraProvider'
import './globals.css'

const display = Cormorant_Garamond({
  variable: '--font-display',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  style: ['normal', 'italic'],
})

const body = Hanken_Grotesk({
  variable: '--font-body',
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'QuickShop — Clothing Shopping Assistant',
  description: 'Find clothing from trustworthy sellers, made from natural fibers, at a fair price',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body>
        <ChakraProvider>{children}</ChakraProvider>
      </body>
    </html>
  )
}
