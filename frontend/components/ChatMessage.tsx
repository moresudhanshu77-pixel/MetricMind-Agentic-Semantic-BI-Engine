"use client";

import { BarChartView } from "@/components/BarChartView";
import { useState } from "react";
import { ChatMessage as ChatMessageType } from "@/types";
import { DataTable } from "@/components/DataTable";

export function ChatMessageBubble({ message }: { message: ChatMessageType }) {
  const [showQuery, setShowQuery] = useState(false);
  const isUser = message.role === "user";
  const response = message.response;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-2xl rounded-xl px-5 py-4 mb-2 ${
  isUser ? "bg-blue-600 text-white" : "bg-gray-900 border border-gray-800 text-gray-100"
}`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {response && (
          <>
            <DataTable rows={response.data} />
            <BarChartView rows={response.data} title="Revenue / Margin Overview" />
            {response.mode === "investigative" && response.breakdown_data && (
              <DataTable rows={response.breakdown_data} title="Root-cause breakdown by category" />
            )}
            {response.mode === "investigative" && response.breakdown_data && (
            <BarChartView rows={response.breakdown_data} title="Margin % by Category" />
            )}

            <div className="mt-2">
              <button
                onClick={() => setShowQuery(!showQuery)}
                className="text-xs text-gray-500 underline"
              >
                {showQuery ? "Hide" : "View"} API Call
              </button>
              {showQuery && (
                <pre className="mt-1 text-xs bg-gray-900 text-green-400 p-2 rounded overflow-x-auto">
{JSON.stringify(
  { cube_query: response.cube_query, ...(response.breakdown_query && { breakdown_query: response.breakdown_query }) },
  null,
  2
)}
                </pre>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}