'use client'

import { useEffect, useRef, useState } from 'react'

// Type declaration for mermaid
declare global {
  interface Window {
    mermaid: any
  }
}

interface MermaidDiagramProps {
  content: string
  className?: string
  maxHeight?: number
  aspectRatio?: 'auto' | 'square' | 'wide'
}

export default function MermaidDiagram({ 
  content, 
  className = '', 
  maxHeight = 400,
  aspectRatio = 'auto'
}: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [renderId, setRenderId] = useState<string>('')
  const [hasRendered, setHasRendered] = useState(false)

  useEffect(() => {
    // Only render if we have valid content and container, and haven't rendered yet
    if (!content || !containerRef.current || content.trim() === '') {
      setIsLoading(false)
      return
    }

    // Prevent re-rendering if already rendered with same content
    if (hasRendered && renderId === content.substring(0, 50)) {
      return
    }

    const renderDiagram = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        // Clear previous content
        if (containerRef.current) {
          containerRef.current.innerHTML = ''
        }

        // Wait for mermaid to be available
        if (typeof window === 'undefined' || !window.mermaid) {
          throw new Error('Mermaid library not loaded')
        }

        // Initialize mermaid with proper configuration
        window.mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'loose',
          theme: 'default',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontSize: 14,
          flowchart: {
            useMaxWidth: false,
            htmlLabels: true,
            curve: 'basis',
            padding: 20
          },
          themeVariables: {
            primaryColor: '#3b82f6',
            primaryTextColor: '#1e293b',
            primaryBorderColor: '#3b82f6',
            lineColor: '#64748b',
            sectionBkgColor: '#f8fafc',
            altSectionBkgColor: '#f1f5f9',
            gridColor: '#e2e8f0',
            tertiaryColor: '#64748b',
            background: '#ffffff',
            mainBkg: '#ffffff',
            secondBkg: '#f8fafc',
            tertiaryBkg: '#f1f5f9',
            nodeBkg: '#ffffff',
            nodeBorder: '#e2e8f0',
            clusterBkg: '#f8fafc',
            clusterBorder: '#cbd5e1'
          }
        })

        // Create unique ID for this diagram
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        setRenderId(content.substring(0, 50))

        // Create temporary div for rendering
        const tempDiv = document.createElement('div')
        tempDiv.className = 'mermaid'
        tempDiv.textContent = content
        
        if (containerRef.current) {
          containerRef.current.appendChild(tempDiv)
        }

        // Use mermaid.run for proper rendering
        await window.mermaid.run({
          nodes: [tempDiv]
        })

        // Get the rendered SVG and optimize it
        const svgElement = tempDiv.querySelector('svg')
        if (svgElement) {
          // Create wrapper for proper sizing
          const wrapper = document.createElement('div')
          wrapper.className = 'diagram-wrapper'
          wrapper.style.cssText = `
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
            min-height: 200px;
            max-height: ${maxHeight}px;
            overflow: auto;
            position: relative;
          `
          
          // Optimize SVG for consistent sizing
          svgElement.style.cssText = `
            max-width: 100%;
            max-height: ${maxHeight}px;
            width: auto;
            height: auto;
            display: block;
            margin: 0 auto;
            padding: 16px;
            box-sizing: border-box;
          `
          
          // Ensure viewBox exists for proper scaling
          if (!svgElement.getAttribute('viewBox')) {
            const bbox = svgElement.getBBox()
            svgElement.setAttribute('viewBox', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`)
          }
          
          wrapper.appendChild(svgElement)
          
          // Replace tempDiv with optimized wrapper
          if (containerRef.current && tempDiv.parentNode) {
            tempDiv.parentNode.replaceChild(wrapper, tempDiv)
          }
        }

        setIsLoading(false)
        setHasRendered(true)
      } catch (err) {
        console.error('Mermaid rendering error:', err)
        setError(err instanceof Error ? err.message : 'Unknown error occurred')
        setIsLoading(false)
        setHasRendered(false)
        
        // Show error in container
        if (containerRef.current) {
          containerRef.current.innerHTML = `
            <div class="flex items-center justify-center h-32 text-red-500 text-sm">
              <div class="text-center">
                <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>Diagram rendering failed</p>
                <p class="text-xs mt-1">${err instanceof Error ? err.message : 'Unknown error'}</p>
              </div>
            </div>
          `
        }
      }
    }

    // Add small delay to ensure DOM is ready
    const timer = setTimeout(renderDiagram, 100)
    
    return () => {
      clearTimeout(timer)
    }
  }, [content, maxHeight])

  // Show empty state if no content
  if (!content || content.trim() === '') {
    return (
      <div className={`flex items-center justify-center h-32 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="text-center">
          <svg className="w-8 h-8 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <p className="text-sm text-gray-600 dark:text-gray-400">No diagram content available</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center h-48 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-sm text-gray-600 dark:text-gray-400">Rendering diagram...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-32 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800 ${className}`}>
        <div className="text-center">
          <svg className="w-8 h-8 mx-auto mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p className="text-sm text-red-600 dark:text-red-400">Failed to render diagram</p>
          <p className="text-xs text-red-500 mt-1">{error}</p>
        </div>
      </div>
    )
  }

  return <div ref={containerRef} className={`mermaid-diagram-container ${className}`} />
}
