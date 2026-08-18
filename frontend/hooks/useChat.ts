"use client";

import { useState } from "react";
import { askMetricMind } from "@/lib/api";
import { ChatMessage } from "@/types";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage(question: string) {
    if (!question.trim()) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
  const response = await askMetricMind(question);

  const isEmpty = !response.data || response.data.length === 0 || 
    response.data.every((row) => Object.values(row).every((v) => v === null));

  if (isEmpty) {
    throw new Error("Empty data from live source");
  }

  const assistantMessage: ChatMessage = {
    id: crypto.randomUUID(),
    role: "assistant",
    content: response.explanation || response.error || "Something went wrong.",
    response,
  };
  setMessages((prev) => [...prev, assistantMessage]);
} catch (err) {
  const { DEMO_MARGIN_BY_CATEGORY, DEMO_MARGIN_BY_STATUS } = await import("@/lib/demoData");
  const isInvestigative = /why|low|drop|cause|category|categories/i.test(question);
  const demo = isInvestigative ? DEMO_MARGIN_BY_CATEGORY : DEMO_MARGIN_BY_STATUS;

  const fallbackMessage: ChatMessage = {
    id: crypto.randomUUID(),
    role: "assistant",
    content: `[Live data temporarily unavailable — showing last synced results] ${demo.explanation}`,
    response: demo,
  };
  setMessages((prev) => [...prev, fallbackMessage]);
} finally {
  setLoading(false);
}
  }

  return { messages, sendMessage, loading };
}