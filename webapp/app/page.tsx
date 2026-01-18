'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CopyButton } from '@/components/ui/copy-button';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { api, GenerateResponse } from '@/lib/api';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const [input, setInput] = useState('Create a FastAPI REST API with user authentication');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

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
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate');
    } finally {
      setLoading(false);
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
                disabled={loading || !input.trim()}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium px-6 py-2 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    Generate Project
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
                <TabsList className="grid w-full grid-cols-4 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
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
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
