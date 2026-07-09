import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MarkdownReport({ content }: { content: string }) {
  if (!content) return null;

  return (
    <div className="glass p-8 rounded-2xl w-full max-w-4xl mx-auto mt-8 animate-in slide-in-from-bottom-8 duration-500">
      <div className="prose prose-invert prose-primary max-w-none">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}
