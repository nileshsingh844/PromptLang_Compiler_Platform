/**
 * Test component to verify mermaid utils functionality
 */
'use client'

import { useState } from 'react'
import { convertMermaidToSvg, openDiagramInNewTab } from '@/lib/mermaid-utils'

export default function MermaidTest() {
  const [isLoading, setIsLoading] = useState(false)
  
  const testContent = `graph TB
    subgraph "Presentation Layer"
        UI[User Interface]
        API_GW[API Gateway]
    end
    
    subgraph "Business Logic Layer"
        AUTH[Authentication Service]
        BUSINESS[Business Service]
        WORKFLOW[Workflow Engine]
    end
    
    subgraph "Data Layer"
        DB[(Database)]
        CACHE[(Cache)]
        QUEUE[Message Queue]
    end
    
    UI --> API_GW
    API_GW --> AUTH
    API_GW --> BUSINESS
    AUTH --> DB
    BUSINESS --> DB
    BUSINESS --> CACHE
    WORKFLOW --> QUEUE`

  const handleTestConversion = async () => {
    setIsLoading(true)
    try {
      const svgUrl = await convertMermaidToSvg(testContent)
      console.log('SVG URL generated:', svgUrl)
      alert('SVG conversion successful! Check console for URL.')
    } catch (error) {
      console.error('Conversion failed:', error)
      alert('Conversion failed. Check console for details.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestOpen = () => {
    openDiagramInNewTab(testContent, 'Test Diagram')
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Mermaid Utils Test</h1>
      
      <div className="space-y-4">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg border">
          <h2 className="text-lg font-semibold mb-4">Test Functions</h2>
          
          <div className="flex gap-4">
            <button
              onClick={handleTestConversion}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Converting...' : 'Test SVG Conversion'}
            </button>
            
            <button
              onClick={handleTestOpen}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Test Open in New Tab
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg border">
          <h2 className="text-lg font-semibold mb-4">Test Mermaid Content</h2>
          <pre className="bg-slate-100 dark:bg-slate-900 p-4 rounded text-sm overflow-x-auto">
            {testContent}
          </pre>
        </div>
      </div>
    </div>
  )
}
