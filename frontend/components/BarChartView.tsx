"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { DataRow } from "@/types";

export function BarChartView({ rows, title }: { rows: DataRow[]; title?: string }) {
  if (!rows || rows.length === 0) return null;

  const keys = Object.keys(rows[0]);
  const dimensionKey = keys.find((k) => typeof rows[0][k] === "string") || keys[0];
  const measureKey = keys.find(
    (k) => k !== dimensionKey && !isNaN(parseFloat(String(rows[0][k])))
  );

  if (!measureKey) return null;

  const chartData = rows
    .filter((r) => r[dimensionKey] !== null && r[measureKey] !== null)
    .map((r) => ({
      name: String(r[dimensionKey]).replace(/_/g, " "),
      value: parseFloat(String(r[measureKey])),
    }));

  return (
    <div className="mt-4">
      {title && <p className="text-xs font-medium text-gray-500 mb-2">{title}</p>}
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-30} textAnchor="end" interval={0} fontSize={11} />
          <YAxis fontSize={11} />
          <Tooltip />
          <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}