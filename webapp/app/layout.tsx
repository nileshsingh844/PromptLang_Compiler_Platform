import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'PromptLang Compiler Platform',
  description: 'Transform Human Input → PromptLang IR → Optimized IR → Model Dialect → Contract Enforced Output',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
