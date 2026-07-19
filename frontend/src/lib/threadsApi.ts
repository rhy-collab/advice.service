const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/v1";

export type GetAuthToken = () => Promise<string | null>;

export type ContextProfile = {
  users_customers: string | null;
  revenue_or_funding_stage: string | null;
  customer_profile: string | null;
  team_size: string | null;
  goals: string | null;
};

export type AdvisorPosition = {
  advisor_name: string;
  persona: string;
  position: string;
  cross_examination: string | null;
};

export type Verdict = {
  ruling: string;
  assumptions: string[];
  dissent: string | null;
  validation_plan: string | null;
  follow_up_questions: string[];
};

export type BoardView = {
  id: string;
  round: number;
  domain: string | null;
  status: string;
  positions: AdvisorPosition[];
  verdict: Verdict | null;
};

export type ThreadMessage = {
  role: "founder" | "agent" | "system";
  content: string;
  created_at: string;
};

export type ThreadSummary = {
  id: string;
  title: string;
  status: string;
  domain: string | null;
  created_at: string;
};

export type ThreadDetail = {
  id: string;
  title: string;
  problem_text: string;
  status: "context_pending" | "triage" | "panel" | "agent_ready";
  domain: string | null;
  boards: BoardView[];
  messages: ThreadMessage[];
  context_profile: ContextProfile;
  context_sufficient: boolean;
};

export type AdviserQuote = {
  adviser_id: string;
  name: string;
  title: string;
  metro: string;
  hourly_rate: number;
  skills_profile: string;
  why_fit: string;
  estimated_hours: string;
  estimated_total: number;
  platform_fee_pct: number;
  not_to_exceed: number;
};

export type AdviserQuotesResponse = {
  domain: string;
  quotes: AdviserQuote[];
};

async function request<T>(
  path: string,
  getAuthToken: GetAuthToken | undefined,
  init?: RequestInit,
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getAuthToken ? await getAuthToken() : null;
  headers.Authorization = `Bearer ${token ?? "demo"}`;
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    throw new Error(`API ${response.status}: ${await response.text()}`);
  }
  return (await response.json()) as T;
}

export function listThreads(getAuthToken?: GetAuthToken): Promise<{ threads: ThreadSummary[] }> {
  return request("/threads", getAuthToken);
}

export function createThread(
  problemText: string,
  getAuthToken?: GetAuthToken,
): Promise<ThreadDetail> {
  return request("/threads", getAuthToken, {
    method: "POST",
    body: JSON.stringify({ problem_text: problemText }),
  });
}

export function getThread(threadId: string, getAuthToken?: GetAuthToken): Promise<ThreadDetail> {
  return request(`/threads/${threadId}`, getAuthToken);
}

export function updateContext(
  threadId: string,
  context: Partial<ContextProfile>,
  getAuthToken?: GetAuthToken,
): Promise<ThreadDetail> {
  return request(`/threads/${threadId}/context`, getAuthToken, {
    method: "POST",
    body: JSON.stringify(context),
  });
}

export function postMessage(
  threadId: string,
  content: string,
  getAuthToken?: GetAuthToken,
): Promise<{ reply: ThreadMessage }> {
  return request(`/threads/${threadId}/messages`, getAuthToken, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function getAdviserQuotes(
  threadId: string,
  getAuthToken?: GetAuthToken,
): Promise<AdviserQuotesResponse> {
  return request(`/threads/${threadId}/adviser-quotes`, getAuthToken);
}
