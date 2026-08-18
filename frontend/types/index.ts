export interface CubeQuery {
  measures: string[];
  dimensions: string[];
}

export interface DataRow {
  [key: string]: string | number | null;
}

export interface AskResponse {
  question: string;
  mode: "simple" | "investigative";
  cube_query: CubeQuery;
  breakdown_query?: CubeQuery;
  data: DataRow[];
  breakdown_data?: DataRow[];
  explanation: string;
  error?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: AskResponse;
}