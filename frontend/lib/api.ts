import { AskResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function askMetricMind(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}