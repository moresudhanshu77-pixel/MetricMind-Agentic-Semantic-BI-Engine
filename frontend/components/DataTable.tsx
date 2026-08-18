import { DataRow } from "@/types";

export function DataTable({ rows, title }: { rows: DataRow[]; title?: string }) {
  if (!rows || rows.length === 0) return null;

  return (
    <div className="mt-3 overflow-x-auto">
      {title && <p className="text-xs font-medium text-gray-500 mb-1">{title}</p>}
      <table className="text-sm w-full border-collapse">
        <thead>
          <tr>
            {Object.keys(rows[0]).map((key) => (
              <th key={key} className="text-left border-b border-gray-800 py-1 pr-4 font-medium text-gray-400">
                {key.split(".").pop()}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {Object.values(row).map((val, j) => (
                <td key={j} className="py-1 pr-4 border-b border-gray-800">
                  {val === null ? "—" : String(val)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}