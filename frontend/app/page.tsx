"use client";

import { useState, useRef, useEffect } from "react";
import { useChat } from "@/hooks/useChat";
import { ChatMessageBubble } from "@/components/ChatMessage";

const suggestions = [
  "What is our total revenue by order status?",
  "Why is our margin so low overall?",
  "What is our margin percentage by product category?",
];

export default function Home() {
  const { messages, sendMessage, loading } = useChat();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    sendMessage(input);
    setInput("");
  }

  return (
    <main className="flex flex-col h-screen bg-gray-950 text-gray-100">
      <div className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
          MetricMind
        </h1>
        <p className="text-sm text-gray-500">Agentic Semantic BI Engine</p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 max-w-4xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="mt-10">
            <p className="text-gray-400 mb-4">Try asking:</p>
            <div className="grid gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-left px-4 py-3 rounded-xl bg-gray-900 border border-gray-800 hover:border-blue-500 hover:bg-gray-800 transition-colors text-sm"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => (
          <ChatMessageBubble key={m.id} message={m} />
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-4">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse [animation-delay:0.2s]" />
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse [animation-delay:0.4s]" />
            <span>Analyzing...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-800 px-6 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask MetricMind a question..."
            className="flex-1 bg-gray-900 border border-gray-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl text-sm font-medium disabled:opacity-40 transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </main>
  );
}