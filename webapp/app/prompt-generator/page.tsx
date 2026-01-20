'use client';

import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CopyButton } from '@/components/ui/copy-button';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Loader2, Download, Save, FolderOpen, Trash2 } from 'lucide-react';

type PromptTemplatesResponse = {
  templates: string[];
};

type PromptJobResponse = {
  job_id: string;
  template_name: string;
  prompt: string;
  ir: any;
  knowledge_card: any;
  enriched_context: any;
  sources: any;
  provenance: any;
};

type SSEMessage = {
  event: string;
  data: any;
};

const API_BASE_URL = 'http://localhost:8000';

const DRAFT_STORAGE_KEY = 'promptlang.prompt_generator.draft.v1';

function parseUrls(text: string): string[] {
  return text
    .split('\n')
    .map((x) => x.trim())
    .filter(Boolean);
}

async function* readSSE(response: Response): AsyncGenerator<SSEMessage, void, unknown> {
  if (!response.body) {
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = '';
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    while (true) {
      const idx = buffer.indexOf('\n\n');
      if (idx === -1) break;
      const rawEvent = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      const lines = rawEvent.split('\n');
      let event = 'message';
      let dataStr = '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          event = line.slice('event:'.length).trim();
        }
        if (line.startsWith('data:')) {
          dataStr += line.slice('data:'.length).trim();
        }
      }

      let data: any = dataStr;
      try {
        data = JSON.parse(dataStr);
      } catch {
        // keep as string
      }

      yield { event, data };
    }
  }
}

export default function PromptGeneratorPage() {
  const abortRef = useRef<AbortController | null>(null);

  const [step, setStep] = useState<1 | 2 | 3>(1);

  const [templates, setTemplates] = useState<string[]>(['universal_cursor_prompt']);
  const [templateName, setTemplateName] = useState('universal_cursor_prompt');

  const [input, setInput] = useState('Create a FastAPI REST API with user authentication');
  const [repoUrl, setRepoUrl] = useState('');
  const [urlsText, setUrlsText] = useState('');

  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<Array<{ stage: string; data: any }>>([]);
  const [error, setError] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  const [result, setResult] = useState<PromptJobResponse | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(DRAFT_STORAGE_KEY);
      if (!raw) return;
      const d = JSON.parse(raw);

      if (typeof d?.input === 'string') setInput(d.input);
      if (typeof d?.repoUrl === 'string') setRepoUrl(d.repoUrl);
      if (typeof d?.urlsText === 'string') setUrlsText(d.urlsText);
      if (typeof d?.templateName === 'string') setTemplateName(d.templateName);
      if (typeof d?.step === 'number') {
        const s = d.step as 1 | 2 | 3;
        if (s === 1 || s === 2 || s === 3) setStep(s);
      }
    } catch {
      return;
    }
  }, []);

  const urls = useMemo(() => parseUrls(urlsText), [urlsText]);

  const saveDraft = () => {
    try {
      localStorage.setItem(
        DRAFT_STORAGE_KEY,
        JSON.stringify({
          step,
          templateName,
          input,
          repoUrl,
          urlsText,
        })
      );
    } catch {
      return;
    }
  };

  const loadDraft = () => {
    try {
      const raw = localStorage.getItem(DRAFT_STORAGE_KEY);
      if (!raw) return;
      const d = JSON.parse(raw);

      if (typeof d?.input === 'string') setInput(d.input);
      if (typeof d?.repoUrl === 'string') setRepoUrl(d.repoUrl);
      if (typeof d?.urlsText === 'string') setUrlsText(d.urlsText);
      if (typeof d?.templateName === 'string') setTemplateName(d.templateName);
      if (typeof d?.step === 'number') {
        const s = d.step as 1 | 2 | 3;
        if (s === 1 || s === 2 || s === 3) setStep(s);
      }
    } catch {
      return;
    }
  };

  const clearDraft = () => {
    try {
      localStorage.removeItem(DRAFT_STORAGE_KEY);
    } catch {
      return;
    }
  };

  const validateForGeneration = () => {
    if (!input.trim()) {
      return 'Project Input is required.';
    }

    if (repoUrl.trim()) {
      const u = repoUrl.trim();
      if (!u.startsWith('http://') && !u.startsWith('https://')) {
        return 'GitHub Repo must start with http(s)://';
      }
      if (!u.includes('github.com/')) {
        return 'GitHub Repo must be a github.com URL.';
      }
    }

    for (const u of urls) {
      if (!u.startsWith('http://') && !u.startsWith('https://')) {
        return `URL must start with http(s)://: ${u}`;
      }
    }

    return null;
  };

  const fetchTemplates = async () => {
    setError(null);
    try {
      const r = await fetch(`${API_BASE_URL}/api/v1/templates`);
      if (!r.ok) throw new Error(await r.text());
      const data = (await r.json()) as PromptTemplatesResponse;
      setTemplates(data.templates || []);
    } catch (e: any) {
      setError(e?.message || 'Failed to load templates');
    }
  };

  useEffect(() => {
    void fetchTemplates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (validationError) setValidationError(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [input, repoUrl, urlsText, templateName]);

  const handleGenerate = async () => {
    const v = validateForGeneration();
    setValidationError(v);
    if (v) {
      return;
    }

    setStep(2);
    setLoading(true);
    setError(null);
    setProgress([]);
    setResult(null);

    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({
          input,
          template_name: templateName,
          repo_url: repoUrl || null,
          urls,
          token_budget: 4000,
        }),
        signal: ac.signal,
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      for await (const msg of readSSE(response)) {
        if (msg.event === 'error') {
          setError(msg.data?.message || 'Generation failed');
          continue;
        }

        if (msg.event === 'result') {
          setResult(msg.data as PromptJobResponse);
          setStep(3);
          continue;
        }

        setProgress((prev) => [...prev, { stage: msg.event, data: msg.data }]);
      }
    } catch (e: any) {
      if (e?.name === 'AbortError') {
        return;
      }
      setError(e?.message || 'Failed to generate');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    abortRef.current?.abort();
    setLoading(false);
  };

  const handleDownload = async () => {
    if (!result?.job_id) return;
    window.open(`${API_BASE_URL}/api/v1/download/${result.job_id}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Prompt Generator</h1>
            <p className="text-muted-foreground">Generate Cursor-ready prompts with progress streaming.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant={step === 1 ? 'default' : 'outline'} size="sm" onClick={() => setStep(1)} disabled={loading}>
              Input
            </Button>
            <Button variant={step === 2 ? 'default' : 'outline'} size="sm" onClick={() => setStep(2)} disabled={loading}>
              Sources
            </Button>
            <Button variant={step === 3 ? 'default' : 'outline'} size="sm" onClick={() => setStep(3)} disabled={loading}>
              Result
            </Button>
            <Button variant="outline" onClick={fetchTemplates} disabled={loading}>
              Refresh Templates
            </Button>
            <Button variant="outline" onClick={saveDraft} disabled={loading} className="gap-2">
              <Save className="h-4 w-4" />
              Save
            </Button>
            <Button variant="outline" onClick={loadDraft} disabled={loading} className="gap-2">
              <FolderOpen className="h-4 w-4" />
              Load
            </Button>
            <Button variant="outline" onClick={clearDraft} disabled={loading} className="gap-2">
              <Trash2 className="h-4 w-4" />
              Clear
            </Button>
            <ThemeToggle />
          </div>
        </div>

        {(validationError || error) && (
          <Card>
            <CardHeader>
              <CardTitle className="text-red-600">Error</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap text-sm">{validationError || error}</pre>
            </CardContent>
          </Card>
        )}

        {step === 1 ? (
          <Card>
            <CardHeader>
              <CardTitle>Step 1: Input</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="text-sm font-medium">Template</div>
                <select
                  className="h-10 w-full rounded-md border bg-background px-3 text-sm"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  disabled={loading}
                >
                  {(templates.length ? templates : ['universal_cursor_prompt']).map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Project Input</div>
                <Textarea value={input} onChange={(e) => setInput(e.target.value)} rows={10} />
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setStep(2)} disabled={loading || !input.trim()}>
                  Next
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : null}

        {step === 2 ? (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Step 2: Sources</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="text-sm font-medium">GitHub Repo (optional)</div>
                  <Textarea
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    rows={2}
                    placeholder="https://github.com/org/repo"
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <div className="text-sm font-medium">URLs (optional, one per line)</div>
                  <Textarea
                    value={urlsText}
                    onChange={(e) => setUrlsText(e.target.value)}
                    rows={5}
                    placeholder="https://docs.example.com\nhttps://example.com/blog/post"
                    disabled={loading}
                  />
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" onClick={() => setStep(1)} disabled={loading}>
                    Back
                  </Button>
                  <Button onClick={handleGenerate} disabled={loading || !input.trim()} className="gap-2">
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                    Generate (SSE)
                  </Button>
                  <Button variant="outline" onClick={handleCancel} disabled={!loading}>
                    Cancel
                  </Button>
                  <Button variant="outline" onClick={() => setStep(3)} disabled={!result?.prompt || loading}>
                    Go to result
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Progress</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex flex-wrap gap-2">
                  {loading ? <Badge>running</Badge> : <Badge variant="outline">idle</Badge>}
                  {result?.job_id ? <Badge variant="outline">job: {result.job_id.slice(0, 8)}</Badge> : null}
                </div>
                <div className="max-h-[420px] overflow-auto rounded border p-3 text-sm">
                  {progress.length === 0 ? (
                    <div className="text-muted-foreground">No events yet.</div>
                  ) : (
                    <div className="space-y-2">
                      {progress.map((p, i) => (
                        <div key={i} className="rounded border p-2">
                          <div className="font-medium">{p.stage}</div>
                          <pre className="mt-1 whitespace-pre-wrap text-xs text-muted-foreground">
                            {JSON.stringify(p.data, null, 2)}
                          </pre>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : null}

        <Card className={step === 3 ? '' : 'hidden'}>
          <CardHeader>
            <CardTitle>Result</CardTitle>
          </CardHeader>
          <CardContent>
            {!result ? (
              <div className="text-muted-foreground">No prompt generated yet.</div>
            ) : (
              <Tabs defaultValue="prompt">
                <TabsList>
                  <TabsTrigger value="prompt">Prompt</TabsTrigger>
                  <TabsTrigger value="meta">Meta</TabsTrigger>
                </TabsList>

                <TabsContent value="prompt" className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    <CopyButton text={result.prompt} />
                    <Button variant="outline" size="sm" onClick={handleDownload} className="gap-2">
                      <Download className="h-4 w-4" />
                      Download
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                    <div className="rounded border overflow-hidden">
                      <Editor
                        height="420px"
                        language="markdown"
                        value={result.prompt}
                        onChange={(v) => setResult({ ...result, prompt: v || '' })}
                        options={{
                          minimap: { enabled: false },
                          wordWrap: 'on',
                          fontSize: 13,
                        }}
                      />
                    </div>
                    <div className="rounded border p-3 max-h-[420px] overflow-auto">
                      <div className="text-sm font-medium mb-2">Preview</div>
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown>{result.prompt}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="meta" className="space-y-3">
                  <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                    <div className="rounded border p-3">
                      <div className="mb-2 text-sm font-medium">IR</div>
                      <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(result.ir, null, 2)}</pre>
                    </div>
                    <div className="rounded border p-3">
                      <div className="mb-2 text-sm font-medium">Knowledge Card</div>
                      <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(result.knowledge_card, null, 2)}</pre>
                    </div>
                    <div className="rounded border p-3">
                      <div className="mb-2 text-sm font-medium">Enriched Context</div>
                      <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(result.enriched_context, null, 2)}</pre>
                    </div>
                    <div className="rounded border p-3">
                      <div className="mb-2 text-sm font-medium">Sources</div>
                      <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(result.sources, null, 2)}</pre>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
