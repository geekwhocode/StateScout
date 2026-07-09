import React, { useState } from 'react';

export default function BYOKModal({ onSubmit, onClose }: { onSubmit: (key: string, provider: string) => void, onClose: () => void }) {
  const [key, setKey] = useState('');
  const [provider, setProvider] = useState('groq');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="glass p-8 rounded-2xl w-full max-w-md animate-in fade-in zoom-in duration-300">
        <h2 className="text-2xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
          Unlock Unlimited Research
        </h2>
        <p className="text-textMuted mb-6 text-sm">
          Your free trial credits are exhausted. Bring your own API key to continue exploring.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-textMuted mb-1">Provider</label>
            <select 
              value={provider} 
              onChange={(e) => setProvider(e.target.value)}
              className="w-full bg-surface/50 border border-white/10 rounded-lg p-2.5 text-textMain focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="groq">Groq (Llama3)</option>
              <option value="google">Google Gemini</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-textMuted mb-1">API Key</label>
            <input 
              type="password"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="sk-..."
              className="w-full bg-surface/50 border border-white/10 rounded-lg p-2.5 text-textMain focus:outline-none focus:ring-2 focus:ring-primary placeholder-textMuted/50"
            />
          </div>
        </div>

        <div className="mt-8 flex justify-end gap-3">
          <button 
            onClick={onClose}
            className="px-4 py-2 rounded-lg font-medium text-textMuted hover:text-textMain transition-colors"
          >
            Cancel
          </button>
          <button 
            onClick={() => onSubmit(key, provider)}
            className="px-6 py-2 rounded-lg font-medium bg-gradient-to-r from-primary to-accent text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 transition-all hover:scale-105"
          >
            Unlock Now
          </button>
        </div>
      </div>
    </div>
  );
}
