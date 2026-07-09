import React, { useState, useEffect, useRef } from 'react';
import MarkdownReport from './MarkdownReport';

interface Props {
  apiKey: string | null;
  provider: string | null;
  onCreditUpdate: (credits: number | string) => void;
}

/**
 * Main Interactive Research Component
 * Handles user input and actively connects to the backend FastAPI via
 * Server-Sent Events (SSE). It builds a live terminal HUD showing LangGraph
 * node transitions in real-time, scrolling automatically as states update.
 */
export default function ResearchUI({ apiKey, provider, onCreditUpdate }: Props) {
  const [topic, setTopic] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [logs, setLogs] = useState<{ node: string; state: any }[]>([]);
  const [report, setReport] = useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const startResearch = async () => {
    if (!topic.trim()) return;
    
    setLogs([]);
    setReport(null);
    setIsResearching(true);

    try {
      // 1. Init Session
      const sessionId = 'session-' + Math.random().toString(36).substr(2, 9);
      const res = await fetch('http://localhost:8001/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, session_id: sessionId, api_key: apiKey, provider })
      });
      
      if (!res.ok) {
        if (res.status === 403) onCreditUpdate(0);
        setIsResearching(false);
        return;
      }
      
      const data = await res.json();
      onCreditUpdate(data.remaining_credits);

      // 2. Consume SSE
      const eventSource = new EventSource(`http://localhost:8001/api/stream/${encodeURIComponent(topic)}`);
      
      eventSource.addEventListener('update', (e) => {
        const parsed = JSON.parse(e.data);
        setLogs(prev => [...prev, parsed]);
        if (parsed.node === 'synthesizer' && parsed.state.report) {
            setReport(parsed.state.report);
        }
      });

      eventSource.addEventListener('done', () => {
        setIsResearching(false);
        eventSource.close();
      });

      eventSource.addEventListener('error', (e) => {
        console.error('SSE Error:', e);
        setIsResearching(false);
        eventSource.close();
      });
      
    } catch (err) {
      console.error(err);
      setIsResearching(false);
    }
  };

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const hasStarted = isResearching || logs.length > 0 || report !== null;

  // Render the pill-shaped input form (matches DocumentDoc style)
  const renderInputForm = () => (
    <form 
      onSubmit={(e) => { e.preventDefault(); startResearch(); }} 
      className="relative flex items-center bg-surface border border-border rounded-[28px] px-4 py-2.5 shadow-sm hover:shadow-md focus-within:shadow-md focus-within:border-primary transition-all w-full max-w-3xl mx-auto"
    >
      <input 
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Research a topic (e.g., 'Impact of autonomous AI agents on SaaS startups in 2024')..."
        className="flex-1 min-h-[24px] bg-transparent border-none focus:outline-none focus:ring-0 py-1.5 px-3 text-sm text-textMain placeholder-textMuted"
        disabled={isResearching}
      />
      <button 
        type="submit"
        disabled={isResearching || !topic.trim()}
        className="p-2 bg-primary hover:bg-accent text-white rounded-full transition-colors disabled:opacity-50 flex items-center justify-center ml-2 shadow-lg hover:scale-105"
        title="Start Research"
      >
        <svg className="h-4 w-4 rotate-90" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
      </button>
    </form>
  );

  return (
    <div className="flex-1 flex flex-col h-full w-full relative">
      {!hasStarted ? (
        // Initial state: Welcome text at top, Input centered
        <div className="flex-1 flex flex-col w-full mx-auto px-4 h-full">
          
          {/* Top text area */}
          <div className="pt-4 space-y-4 text-center md:text-left max-w-3xl mx-auto w-full shrink-0">
            <h1 className="text-4xl md:text-5xl font-medium tracking-tight bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              StateScout
            </h1>
            <p className="text-lg md:text-xl text-textMuted/90 font-normal leading-relaxed max-w-2xl mx-auto md:mx-0 mt-4">
              An autonomous, LangGraph-powered AI agent. Capable of real-time web scraping, semantic chunking, and streaming fully synthesized Markdown reports.
            </p>
          </div>

          {/* Centered Input */}
          <div className="flex-1 flex flex-col justify-center w-full pb-24">
            <div className="w-full">
              {renderInputForm()}
            </div>
          </div>
          
        </div>
      ) : (
        // Active state: Logs/Report scrollable above, Input fixed at bottom
        <div className="flex flex-col w-full h-full min-h-0">
          <div className="flex-1 overflow-y-auto p-4 space-y-6 no-scrollbar pb-6 w-full flex flex-col">
            <div className="max-w-3xl mx-auto w-full flex-1 flex flex-col space-y-6">
              
              {/* Live HUD Logs */}
              {logs.length > 0 && (
                <div className="w-full glass p-6 rounded-2xl h-64 overflow-y-auto font-mono text-sm space-y-3 shrink-0">
                  {logs.map((log, i) => (
                    <div key={i} className="animate-in fade-in slide-in-from-left-4 flex flex-col border-l-2 border-primary pl-4">
                      <span className="text-accent font-bold uppercase tracking-wider mb-1">[{log.node}]</span>
                      <pre className="text-textMuted whitespace-pre-wrap">
                        {JSON.stringify(log.state, null, 2)}
                      </pre>
                    </div>
                  ))}
                  <div ref={logsEndRef} />
                </div>
              )}

              {/* Final Report */}
              {report && <MarkdownReport content={report} />}
              
            </div>
          </div>

          {/* Bottom Fixed Input */}
          <div className="pt-4 mt-auto shrink-0 w-full">
            <div className="max-w-3xl mx-auto w-full">
              {renderInputForm()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
