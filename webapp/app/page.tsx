'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CopyButton } from '@/components/ui/copy-button';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { api, GenerateResponse, DiagramRequest, DiagramResponse } from '@/lib/api';
import { Loader2, Download, Eye, BarChart3, FileText, Network, Code } from 'lucide-react';
import MermaidDiagram from '@/components/mermaid-diagram';

export default function Home() {
  const [input, setInput] = useState('Create a FastAPI REST API with user authentication');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [diagrams, setDiagrams] = useState<DiagramResponse | null>(null);
  const [diagramsLoading, setDiagramsLoading] = useState(false);
  const [diagramsError, setDiagramsError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setDiagrams(null);

    try {
      const response = await api.generate({
        input,
        intent: 'scaffold',
        target_model: 'oss',
        token_budget: 4000,
        scaffold_mode: 'full',
        security_level: 'high',
        validation_mode: 'strict',
      });
      setResult(response);
      
      // Automatically generate diagrams after successful generation
      await generateDiagrams(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate');
    } finally {
      setLoading(false);
    }
  };

  const generateDiagrams = async (generationResult: GenerateResponse) => {
    setDiagramsLoading(true);
    setDiagramsError(null);

    try {
      // Extract project context from the generation result
      const ir = generationResult.ir_json;
      const diagramRequest = {
        prd_content: generationResult.output, // Use the generated output as PRD content
        codebase_path: null, // No codebase path for now
        config: {
          max_diagrams: 10,
          min_score_threshold: 0.0,
          include_optional: true,
          preferred_tool: "mermaid",
          output_format: "svg",
          export_directory: "./diagrams",
          generate_complementary: true,
          parallel_generation: true,
          timeout_seconds: 300
        }
      };

      const diagramResponse = await api.generateDiagrams(diagramRequest);
      console.log('Diagram response:', diagramResponse);
      setDiagrams(diagramResponse);
    } catch (err: any) {
      setDiagramsError(err.response?.data?.detail || err.message || 'Failed to generate diagrams');
    } finally {
      setDiagramsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-between items-center max-w-4xl mx-auto">
            <div className="flex-1"></div>
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 text-center">
              PromptLang Compiler Platform
            </h1>
            <div className="flex-1 flex justify-end">
              <ThemeToggle />
            </div>
          </div>
          <p className="text-slate-600 dark:text-slate-400 text-sm md:text-base max-w-3xl mx-auto">
            Transform Human Input → PromptLang IR → Optimized IR → Model Dialect → Contract Enforced Output
          </p>
        </div>

        {/* Input Card */}
        <Card className="shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
            <CardTitle className="text-slate-800 dark:text-slate-100">
              Create Your Project
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Describe your project idea:
              </label>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="e.g., Create a modern web application with user authentication and dashboard..."
                className="w-full min-h-[120px] p-4 border rounded-lg resize-y font-mono text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border-slate-300 dark:border-slate-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
            </div>
            <div className="flex gap-3">
              <Button
                onClick={handleGenerate}
                disabled={loading || diagramsLoading}
                className="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-2xl disabled:opacity-50 text-lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    Generating...
                  </>
                ) : diagramsLoading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    Creating Diagrams...
                  </>
                ) : (
                  <>
                    <BarChart3 className="mr-3 h-5 w-5" />
                    Generate & Create Diagrams
                  </>
                )}
              </Button>
            </div>
            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-200">
                <div className="flex items-center gap-2">
                  <span className="font-medium">Error:</span>
                  <span>{error}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Tabs */}
        {result && (
          <Card className="shadow-lg">
            <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
              <CardTitle className="text-slate-800 dark:text-slate-100">
                Your Generated Project
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="output" className="w-full">
                <TabsList className="grid w-full grid-cols-5 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
                  <TabsTrigger value="output" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-white text-slate-700 dark:text-slate-300 rounded-md transition-all duration-200">
                    Output
                  </TabsTrigger>
                  <TabsTrigger value="ir" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-white text-slate-700 dark:text-slate-300 rounded-md transition-all duration-200">
                    IR
                  </TabsTrigger>
                  <TabsTrigger value="report" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-white text-slate-700 dark:text-slate-300 rounded-md transition-all duration-200">
                    Report
                  </TabsTrigger>
                  <TabsTrigger value="metrics" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-white text-slate-700 dark:text-slate-300 rounded-md transition-all duration-200">
                    Metrics
                  </TabsTrigger>
                  <TabsTrigger value="diagrams" className="data-[state=active]:bg-gradient-to-r from-blue-500 to-purple-500 data-[state=active]:text-white data-[state=active]:shadow-lg rounded-md transition-all duration-200 font-semibold">
                    📊 Diagrams
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="output" className="mt-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                      <h3 className="font-semibold text-slate-800 dark:text-slate-200">
                        Generated Project Code
                      </h3>
                      <CopyButton text={result.output} />
                    </div>
                    <div className="p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm">
                      <pre className="whitespace-pre-wrap text-sm font-mono text-slate-900 dark:text-slate-100 leading-relaxed">{result.output}</pre>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="ir" className="mt-4">
                  <div className="space-y-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                        <h3 className="font-semibold text-slate-800 dark:text-slate-200">
                          Original IR
                        </h3>
                        <CopyButton text={JSON.stringify(result.ir_json, null, 2)} />
                      </div>
                      <div className="p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm">
                        <pre className="text-xs font-mono overflow-auto max-h-96 text-slate-900 dark:text-slate-100 leading-relaxed">
                          {JSON.stringify(result.ir_json, null, 2)}
                        </pre>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                        <h3 className="font-semibold text-slate-800 dark:text-slate-200">
                          Optimized IR
                        </h3>
                        <CopyButton text={JSON.stringify(result.optimized_ir, null, 2)} />
                      </div>
                      <div className="p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm">
                        <pre className="text-xs font-mono overflow-auto max-h-96 text-slate-900 dark:text-slate-100 leading-relaxed">
                          {JSON.stringify(result.optimized_ir, null, 2)}
                        </pre>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                        <h3 className="font-semibold text-slate-800 dark:text-slate-200">
                          Compiled Prompt
                        </h3>
                        <CopyButton text={result.compiled_prompt} />
                      </div>
                      <div className="p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm">
                        <pre className="text-xs font-mono overflow-auto max-h-96 whitespace-pre-wrap text-slate-900 dark:text-slate-100 leading-relaxed">
                          {result.compiled_prompt}
                        </pre>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="report" className="mt-4">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">Status:</span>
                      <span className={`px-2 py-1 rounded text-sm ${
                        result.validation_report.status === 'success' ? 'bg-green-100 text-green-800' :
                        result.validation_report.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                        result.validation_report.status === 'error' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {result.validation_report.status}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Summary</h3>
                      <pre className="p-4 bg-slate-50 rounded-md border text-xs font-mono overflow-auto">
                        {JSON.stringify(result.validation_report.summary, null, 2)}
                      </pre>
                    </div>
                    {result.validation_report.findings.length > 0 && (
                      <div>
                        <h3 className="font-semibold mb-2">Findings ({result.validation_report.findings.length})</h3>
                        <pre className="p-4 bg-slate-50 rounded-md border text-xs font-mono overflow-auto max-h-96">
                          {JSON.stringify(result.validation_report.findings, null, 2)}
                        </pre>
                      </div>
                    )}
                    <div>
                      <h3 className="font-semibold mb-2">Contract Compliance</h3>
                      <pre className="p-4 bg-slate-50 rounded-md border text-xs font-mono overflow-auto">
                        {JSON.stringify(result.validation_report.contract_compliance, null, 2)}
                      </pre>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="metrics" className="mt-4">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-slate-50 rounded-md border">
                        <div className="text-sm text-slate-600">Request ID</div>
                        <div className="text-sm font-mono mt-1">{result.provenance.request_id}</div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-md border">
                        <div className="text-sm text-slate-600">Build Hash</div>
                        <div className="text-sm font-mono mt-1">{result.provenance.build_hash}</div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-md border">
                        <div className="text-sm text-slate-600">Cache Hit</div>
                        <div className="text-sm font-mono mt-1">{result.cache_hit ? 'Yes' : 'No'}</div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-md border">
                        <div className="text-sm text-slate-600">Token Usage</div>
                        <div className="text-sm font-mono mt-1">
                          {result.provenance.token_usage.estimated} / {result.provenance.token_usage.budget}
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Stage Timings (ms)</h3>
                      <pre className="p-4 bg-slate-50 rounded-md border text-xs font-mono overflow-auto">
                        {JSON.stringify(result.provenance.stage_timings_ms, null, 2)}
                      </pre>
                    </div>
                    {result.warnings.length > 0 && (
                      <div>
                        <h3 className="font-semibold mb-2">Warnings</h3>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                          {result.warnings.map((warning, idx) => (
                            <li key={idx} className="text-yellow-800">{warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="diagrams" className="mt-4">
                  <div className="space-y-4">
                    {diagramsLoading && (
                      <div className="flex flex-col items-center justify-center p-12 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl border border-blue-200 dark:border-blue-800">
                        <Loader2 className="h-12 w-12 animate-spin text-blue-600 dark:text-blue-400 mb-4" />
                        <div className="text-center">
                          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-2">
                            Generating Diagrams
                          </h3>
                          <p className="text-sm text-slate-600 dark:text-slate-400">
                            Creating beautiful visual diagrams from your project description...
                          </p>
                          <div className="mt-4 flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse delay-75"></div>
                            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse delay-150"></div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {diagramsError && (
                      <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-200">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Diagram Generation Error:</span>
                          <span>{diagramsError}</span>
                        </div>
                      </div>
                    )}

                    {diagrams && (
                      <div className="space-y-8">
                        {/* Enhanced Header Section */}
                        <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/30 dark:via-indigo-900/30 dark:to-purple-900/30 p-6 rounded-xl border border-blue-200 dark:border-blue-800 shadow-lg">
                          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                            <div>
                              <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-3">
                                <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                                  <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                </div>
                                Generated Diagrams
                              </h3>
                              <p className="text-base text-slate-600 dark:text-slate-400 mt-2">
                                {diagrams.generated_diagrams?.length || 0} diagrams created successfully
                              </p>
                            </div>
                            {diagrams.status === 'completed' && (
                              <div className="flex items-center gap-2 px-3 py-1 bg-green-100 dark:bg-green-900 rounded-full">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-sm font-medium text-green-700 dark:text-green-400">Completed</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Show generated diagrams with improved layout */}
                        {diagrams.generated_diagrams && diagrams.generated_diagrams.length > 0 && (
                          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                            {diagrams.generated_diagrams.map((diagram: any, idx: number) => (
                              <Card key={idx} className="group hover:shadow-2xl transition-all duration-300 border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 bg-white dark:bg-slate-800 overflow-hidden diagram-card">
                                {/* Card Header */}
                                <CardHeader className="pb-4 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-700 border-b border-slate-200 dark:border-slate-700">
                                  <div className="flex items-start justify-between gap-3">
                                    <div className="flex items-start gap-3 min-w-0 flex-1">
                                      <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center flex-shrink-0">
                                        <Network className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                      </div>
                                      <div className="min-w-0 flex-1">
                                        <CardTitle className="text-lg font-semibold text-slate-800 dark:text-slate-100 leading-tight break-words">
                                          {diagram.name}
                                        </CardTitle>
                                        <div className="flex items-center gap-3 mt-2 flex-wrap">
                                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-xs font-medium">
                                            {diagram.tool}
                                          </span>
                                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                                            {diagram.format.toUpperCase()}
                                          </span>
                                        </div>
                                      </div>
                                    </div>
                                    {diagram.success && (
                                      <div className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0"></div>
                                    )}
                                  </div>
                                </CardHeader>

                                {/* Card Content */}
                                <CardContent className="p-0">
                                  {/* Diagram Display Area */}
                                  <div className="relative bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
                                    <div className="absolute top-3 right-3 z-10">
                                      <span className="px-2 py-1 bg-white dark:bg-slate-800 text-blue-700 dark:text-blue-300 text-xs rounded-full font-medium shadow-sm border border-blue-200 dark:border-blue-700">
                                        Mermaid Diagram
                                      </span>
                                    </div>
                                    
                                    {/* Standardized diagram container */}
                                    <div className="p-4 h-96">
                                      <MermaidDiagram 
                                        content={diagram.content}
                                        className="w-full h-full"
                                        maxHeight={320}
                                      />
                                    </div>
                                  </div>
                                  
                                  {/* Action Buttons */}
                                  <div className="p-4 bg-white dark:bg-slate-800">
                                    <div className="flex gap-2">
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => {
                                          navigator.clipboard.writeText(diagram.content)
                                        }}
                                        className="flex-1 hover:bg-blue-50 dark:hover:bg-blue-900/20 border-blue-200 dark:border-blue-700"
                                      >
                                        <Code className="w-4 h-4 mr-2" />
                                        Copy Code
                                      </Button>
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => {
                                          const blob = new Blob([diagram.content], { type: 'text/plain' })
                                          const url = URL.createObjectURL(blob)
                                          const a = document.createElement('a')
                                          a.href = url
                                          a.download = `${diagram.name.replace(/\s+/g, '_')}.mmd`
                                          a.click()
                                          URL.revokeObjectURL(url)
                                        }}
                                        className="flex-1 hover:bg-green-50 dark:hover:bg-green-900/20 border-green-200 dark:border-green-700"
                                      >
                                        <Download className="w-4 h-4 mr-2" />
                                        Download
                                      </Button>
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        )}

                        {(!diagrams.recommendations || diagrams.recommendations?.length === 0) && 
                         (!diagrams.generated_diagrams || diagrams.generated_diagrams.length === 0) && (
                          <div className="text-center p-8 text-slate-600 dark:text-slate-400">
                            No diagrams were generated. Try adjusting project description or parameters.
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
