'use client'

import { Box, Link, Text } from '@chakra-ui/react'
import type { ReactNode } from 'react'
import { fonts, palette } from '@/theme/palette'

interface ListItem {
  text: string
  children: ListNode[]
}

interface ListNode {
  ordered: boolean
  items: ListItem[]
}

interface RawListLine {
  indent: number
  ordered: boolean
  text: string
}

type Block =
  | { type: 'heading'; level: number; text: string }
  | { type: 'rule' }
  | { type: 'paragraph'; text: string }
  | { type: 'list'; list: ListNode }

const INLINE_PATTERN = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|\[[^\]]+\]\([^)]+\))/g
const LINK_PATTERN = /^\[([^\]]+)\]\(([^)]+)\)$/
const SAFE_URL = /^https?:\/\//i
const BLOCK_START = /^\s*(#{1,6}\s|-{3,}\s*$|\d+[.)]\s|[-*+]\s)/

export function leadText(content: string): string {
  const kept: string[] = []
  for (const line of content.replace(/\r\n/g, '\n').split('\n')) {
    if (BLOCK_START.test(line)) break
    kept.push(line)
  }
  return kept.join('\n').trim()
}

function buildList(lines: RawListLine[]): ListNode {
  const root: ListNode = { ordered: lines[0].ordered, items: [] }
  const stack: { indent: number; list: ListNode }[] = [{ indent: lines[0].indent, list: root }]

  for (const line of lines) {
    while (stack.length > 1 && line.indent < stack[stack.length - 1].indent) stack.pop()
    let top = stack[stack.length - 1]

    if (line.indent > top.indent) {
      const parent = top.list.items[top.list.items.length - 1]
      if (parent) {
        const child: ListNode = { ordered: line.ordered, items: [] }
        parent.children.push(child)
        stack.push({ indent: line.indent, list: child })
        top = stack[stack.length - 1]
      }
    }
    top.list.items.push({ text: line.text, children: [] })
  }
  return root
}

function parseBlocks(content: string): Block[] {
  const blocks: Block[] = []
  let paragraph: string[] = []
  let listLines: RawListLine[] = []

  const flushParagraph = () => {
    if (paragraph.length > 0) blocks.push({ type: 'paragraph', text: paragraph.join(' ') })
    paragraph = []
  }
  const flushList = () => {
    if (listLines.length > 0) blocks.push({ type: 'list', list: buildList(listLines) })
    listLines = []
  }

  for (const rawLine of content.replace(/\r\n/g, '\n').split('\n')) {
    const line = rawLine.replace(/\s+$/, '')
    if (!line.trim()) {
      flushParagraph()
      continue
    }

    const heading = line.match(/^(#{1,6})\s+(.*)$/)
    if (heading) {
      flushParagraph()
      flushList()
      blocks.push({ type: 'heading', level: heading[1].length, text: heading[2] })
      continue
    }

    if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
      flushParagraph()
      flushList()
      blocks.push({ type: 'rule' })
      continue
    }

    const item = line.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/)
    if (item) {
      flushParagraph()
      listLines.push({ indent: item[1].length, ordered: /\d/.test(item[2]), text: item[3] })
      continue
    }

    flushList()
    paragraph.push(line.trim())
  }

  flushParagraph()
  flushList()
  return blocks
}

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  return text
    .split(INLINE_PATTERN)
    .filter(Boolean)
    .map((part, index) => {
      const key = `${keyPrefix}-${index}`

      if (part.length > 4 && part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={key} style={{ fontWeight: 700 }}>
            {renderInline(part.slice(2, -2), key)}
          </strong>
        )
      }
      if (part.length > 2 && part.startsWith('*') && part.endsWith('*')) {
        return <em key={key}>{renderInline(part.slice(1, -1), key)}</em>
      }

      const link = part.match(LINK_PATTERN)
      if (link) {
        const href = link[2].trim()
        if (!SAFE_URL.test(href)) return <span key={key}>{link[1]}</span>
        return (
          <Link
            key={key}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            color={palette.brassText}
            textDecoration="underline"
            textUnderlineOffset="3px"
            fontWeight="600"
            overflowWrap="anywhere"
          >
            {link[1]}
          </Link>
        )
      }

      return <span key={key}>{part}</span>
    })
}

function renderList(list: ListNode, key: string): ReactNode {
  return (
    <Box
      key={key}
      as={list.ordered ? 'ol' : 'ul'}
      listStyleType={list.ordered ? 'decimal' : 'disc'}
      pl={5}
      display="flex"
      flexDirection="column"
      gap={1.5}
    >
      {list.items.map((item, index) => (
        <Box as="li" key={`${key}-${index}`} pl={1}>
          {renderInline(item.text, `${key}-${index}`)}
          {item.children.map((child, childIndex) => (
            <Box key={`${key}-${index}-${childIndex}`} mt={1.5}>
              {renderList(child, `${key}-${index}-${childIndex}`)}
            </Box>
          ))}
        </Box>
      ))}
    </Box>
  )
}

interface MarkdownProps {
  text: string
}

export function Markdown({ text }: MarkdownProps) {
  const blocks = parseBlocks(text)

  return (
    <Box display="flex" flexDirection="column" gap={3.5} fontSize="15px" lineHeight="1.75" color={palette.text} minW={0} overflowWrap="anywhere">
      {blocks.map((block, index) => {
        const key = `block-${index}`
        if (block.type === 'heading') {
          return (
            <Text
              key={key}
              as="h4"
              fontFamily={fonts.display}
              fontSize={block.level <= 2 ? '28px' : '23px'}
              fontWeight="600"
              lineHeight="1.15"
              color={palette.ink}
              letterSpacing="-0.01em"
              mt={index === 0 ? 0 : 3}
            >
              {renderInline(block.text, key)}
            </Text>
          )
        }
        if (block.type === 'rule') return <Box key={key} h="1px" bg={palette.hairline} my={1.5} />
        if (block.type === 'list') return renderList(block.list, key)
        return <Text key={key}>{renderInline(block.text, key)}</Text>
      })}
    </Box>
  )
}
