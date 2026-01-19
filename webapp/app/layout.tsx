'use client'

import type { Metadata } from 'next'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import Script from 'next/script'
import { useEffect } from 'react'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    // Load Mermaid.js manually to handle errors properly
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js'
    script.async = true
    
    script.onload = () => {
      console.log('Mermaid.js loaded successfully')
    }
    
    script.onerror = (e) => {
      console.error('Failed to load Mermaid.js:', e)
    }
    
    document.head.appendChild(script)
    
    return () => {
      // Cleanup script on unmount
      if (document.head.contains(script)) {
        document.head.removeChild(script)
      }
    }
  }, [])

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
      </head>
      <body>
        <ThemeProvider defaultTheme="light">
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
