'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-slate-900">PromptLang Compiler Platform</h1>
          <p className="text-slate-600">Transform Human Input → PromptLang IR → Optimized IR → Model Dialect → Contract Enforced Output</p>
        </div>

        {/* Input Card */}
        <Card>
          <CardHeader>
            <CardTitle>Input</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter your request here..."
              className="w-full min-h-[120px] p-4 border rounded-md resize-y font-mono text-sm"
            />
            <div className="flex gap-2">
              <Button onClick={handleGenerate} disabled={loading || !input.trim()}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate'
                )}
              </Button>
            </div>
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-800">
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Tabs */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle>Results</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="output" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="output">Output</TabsTrigger>
                  <TabsTrigger value="ir">IR</TabsTrigger>
                  <TabsTrigger value="report">Validation Report</TabsTrigger>
                  <TabsTrigger value="metrics">Metrics</TabsTrigger>
                </TabsList>

                <TabsContent value="output" className="mt-4">
                  <div className="p-4 bg-slate-50 rounded-md border">
                    <pre className="whitespace-pre-wrap text-sm font-mono">{result.output}</pre>
                  </div>
                </TabsContent>

                <TabsContent value="ir" className="mt-4">
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-2">Original IR</h3>
                      <pre className="p-4 bg-slate-50 rounded-md border text-xs font-mono overflow-auto max-h-96">
                        {JSON.stringify(result.ir_json, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Optimized IR</h3>
                      <pre className="p-4 bg-slate-50 rounded-md border text-xs font-mono overflow-auto max-h-96">
                        {JSON.stringify(result.optimized_ir, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Compiled Prompt</h3>
                      <pre className="p-4 bg-slate-50 rounded-md border text-xs font-mono overflow-auto max-h-96 whitespace-pre-wrap">
                        {result.compiled_prompt}
                      </pre>
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
