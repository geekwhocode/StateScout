import React, { useState } from 'react';
import ResearchUI from './components/ResearchUI';
import BYOKModal from './components/BYOKModal';

/**
 * Root Application Component
 * Manages the global state for the Bring Your Own Key (BYOK) monetization model.
 * Initializes with 3 free session credits and tracks the active user's LLM provider
 * overrides to lift credit limits once their key is securely submitted.
 */
function App() {
  const [sessionCredits, setSessionCredits] = useState<number | string>(3);
  const [showBYOK, setShowBYOK] = useState<bool>(false);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [provider, setProvider] = useState<string | null>(null);

  const handleCreditUpdate = (credits: number | string) => {
    setSessionCredits(credits);
    if (credits === 0) {
      setShowBYOK(true);
    }
  };

  const handleKeySubmit = (key: string, prov: string) => {
    setApiKey(key);
    setProvider(prov);
    setShowBYOK(false);
    setSessionCredits('unlimited');
  };

  return (
    <div className="h-screen p-8 flex flex-col">
      <header className="shrink-0 mb-8 flex justify-end items-center max-w-5xl mx-auto w-full">
        <div className="glass px-4 py-2 rounded-full text-sm font-semibold shrink-0">
          Credits: {sessionCredits}
        </div>
      </header>
      
      <main className="flex-1 w-full max-w-5xl mx-auto flex flex-col min-h-0">
        <ResearchUI 
          apiKey={apiKey} 
          provider={provider} 
          onCreditUpdate={handleCreditUpdate} 
        />
      </main>

      {showBYOK && <BYOKModal onSubmit={handleKeySubmit} onClose={() => setShowBYOK(false)} />}
    </div>
  );
}

export default App;
