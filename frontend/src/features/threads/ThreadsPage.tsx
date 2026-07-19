import { useCallback, useEffect, useRef, useState } from "react";
import {
  AdviserQuotesResponse,
  GetAuthToken,
  ThreadDetail,
  ThreadSummary,
  createThread,
  getAdviserQuotes,
  getThread,
  listThreads,
  postMessage,
} from "../../lib/threadsApi";

const DOMAIN_LABELS: Record<string, string> = {
  pricing: "Pricing strategy",
  fundraising: "Fundraising",
  gtm: "Go-to-market",
  pitch: "Pitch & messaging",
  legal: "Legal & compliance",
  ecosystem: "Resources & location",
  engineering: "Developer / engineering",
};

function speaker(role: string): { name: string; kind: string } {
  if (role.startsWith("advisor:")) return { name: role.slice(8), kind: "advisor" };
  switch (role) {
    case "founder":
      return { name: "You", kind: "founder" };
    case "agent":
      return { name: "Perfect Agent", kind: "agent" };
    case "board":
      return { name: "The Board", kind: "board" };
    case "chair":
      return { name: "The Chair", kind: "chair" };
    default:
      return { name: "System", kind: "system" };
  }
}

export function ThreadsPage({ getAuthToken }: { getAuthToken?: GetAuthToken }) {
  const [threads, setThreads] = useState<ThreadSummary[]>([]);
  const [active, setActive] = useState<ThreadDetail | null>(null);
  const [problemDraft, setProblemDraft] = useState(initialProblem());
  const [composerText, setComposerText] = useState("");
  const [composerMode, setComposerMode] = useState<"agent" | "adviser">("agent");
  const [quotes, setQuotes] = useState<AdviserQuotesResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const refreshThreads = useCallback(async () => {
    try {
      const response = await listThreads(getAuthToken);
      setThreads(response.threads);
      setError(null);
    } catch {
      setError("Cannot reach the API. Start the backend (uvicorn app.main:app) with CLERK_DEMO_AUTH=true, or check VITE_API_BASE_URL.");
    }
  }, [getAuthToken]);

  useEffect(() => {
    void refreshThreads();
  }, [refreshThreads]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [active]);

  async function guarded<T>(work: () => Promise<T>): Promise<T | null> {
    setBusy(true);
    try {
      const result = await work();
      setError(null);
      return result;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      return null;
    } finally {
      setBusy(false);
    }
  }

  async function handleCreate() {
    const text = problemDraft.trim();
    if (!text) return;
    const detail = await guarded(() => createThread(text, getAuthToken));
    if (detail) {
      setActive(detail);
      setProblemDraft("");
      setQuotes(null);
      void refreshThreads();
    }
  }

  async function handleOpen(threadId: string) {
    const detail = await guarded(() => getThread(threadId, getAuthToken));
    if (detail) {
      setActive(detail);
      setQuotes(null);
      setComposerMode("agent");
    }
  }

  async function handleSend() {
    if (!active || !composerText.trim()) return;
    if (composerMode === "adviser") {
      const response = await guarded(() => getAdviserQuotes(active.id, getAuthToken));
      if (response) setQuotes(response);
      setComposerText("");
      return;
    }
    const content = composerText.trim();
    setComposerText("");
    setActive((prev) =>
      prev
        ? { ...prev, messages: [...prev.messages, { role: "founder", content, created_at: "" }] }
        : prev,
    );
    const response = await guarded(() => postMessage(active.id, content, getAuthToken));
    if (response) {
      // Rounds may have posted many messages (deliberation) — fetch the full thread.
      const detail = await guarded(() => getThread(active.id, getAuthToken));
      if (detail) {
        setActive(detail);
        void refreshThreads();
      }
    }
  }

  return (
    <div className="th-shell">
      <aside className="th-sidebar">
        <a className="th-logo" href="/">Charter Consultancy</a>
        <button className="th-new" onClick={() => { setActive(null); setQuotes(null); }}>
          + New thread
        </button>
        <div className="th-section-label">Recent threads</div>
        <div className="th-thread-list">
          {threads.map((t) => (
            <button
              key={t.id}
              className={"th-thread-item" + (active?.id === t.id ? " active" : "")}
              onClick={() => void handleOpen(t.id)}
            >
              <span className="th-thread-title">{t.title}</span>
              <span className="th-thread-meta">
                {t.domain ? DOMAIN_LABELS[t.domain] ?? t.domain : statusLabel(t.status)}
              </span>
            </button>
          ))}
          {threads.length === 0 && <p className="th-empty">No threads yet — describe a problem to convene your first board.</p>}
        </div>
      </aside>

      <main className="th-main">
        <div className="th-banner">
          Boards convene instantly. Everything through the perfect agent is free — you only pay if you choose to book a real adviser.
        </div>
        {error && <div className="th-error">{error}</div>}

        {!active ? (
          <div className="th-intake">
            <h1>What's the problem?</h1>
            <p>Describe it once. Your board gathers context, defines the problem, and debates it with genuinely opposed views.</p>
            <textarea
              value={problemDraft}
              onChange={(e) => setProblemDraft(e.target.value)}
              placeholder="e.g. My cofounder wants 60% equity — is that reasonable at our stage?"
              rows={4}
            />
            <button className="th-primary" disabled={busy || !problemDraft.trim()} onClick={() => void handleCreate()}>
              {busy ? "Convening your board…" : "Convene the board"}
            </button>
          </div>
        ) : (
          <>
            <div className="th-thread-scroll" ref={scrollRef}>
              <div className="th-problem">
                <span className="th-problem-label">Problem</span>
                <p>{active.problem_text}</p>
              </div>

              {active.domain && (
                <div className="th-round">
                  <span className="th-domain-chip">{DOMAIN_LABELS[active.domain] ?? active.domain}</span>
                </div>
              )}

              {active.messages.map((message, index) => {
                const who = speaker(message.role);
                return (
                  <div key={index} className={`th-msg th-msg-${who.kind}`}>
                    <span className="th-msg-name">{who.name}</span>
                    <p>{message.content}</p>
                  </div>
                );
              })}

              {busy && <div className="th-msg th-msg-board"><span className="th-msg-name">The Board</span><p className="th-typing">deliberating…</p></div>}

              {quotes && (
                <div className="th-quotes">
                  <h2>Matched advisers — {DOMAIN_LABELS[quotes.domain] ?? quotes.domain}</h2>
                  <p className="th-quotes-note">
                    Real individuals, ranked for this exact problem. Each sets their own rate; the estimate shown is a not-to-exceed cap
                    (includes the {quotes.quotes[0]?.platform_fee_pct ?? 10}% platform fee).
                  </p>
                  {quotes.quotes.map((quote) => (
                    <article key={quote.adviser_id} className="th-quote">
                      <div>
                        <h3>{quote.name}</h3>
                        <p className="th-quote-meta">{quote.metro} · ${quote.hourly_rate}/hr · est. {quote.estimated_hours} hrs</p>
                        <p>{quote.skills_profile}</p>
                      </div>
                      <div className="th-quote-price">
                        <span>${quote.estimated_total}</span>
                        <button className="th-primary" disabled title="Booking wires up with Stripe in Phase 8">Book</button>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>

            <div className="th-composer">
              <textarea
                value={composerText}
                onChange={(e) => setComposerText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void handleSend();
                  }
                }}
                placeholder={
                  composerMode === "agent"
                    ? active.status === "agent_ready"
                      ? "Ask your perfect agent about this problem…"
                      : "Answer the board — users, MRR or stage, customer, team, goals…"
                    : "Describe what you need — send to see your matched advisers…"
                }
                rows={2}
              />
              <div className="th-composer-row">
                <div className="th-tabs">
                  <button
                    className={composerMode === "agent" ? "active" : ""}
                    onClick={() => setComposerMode("agent")}
                  >
                    🤖 Perfect Agent
                  </button>
                  <button
                    className={composerMode === "adviser" ? "active" : ""}
                    onClick={() => {
                      setComposerMode("adviser");
                      if (active.status === "agent_ready") {
                        void guarded(() => getAdviserQuotes(active.id, getAuthToken)).then((r) => r && setQuotes(r));
                      }
                    }}
                  >
                    🧑‍💼 Adviser <span className="th-paid-dot" />
                  </button>
                </div>
                <button className="th-send" disabled={busy} onClick={() => void handleSend()} aria-label="Send">→</button>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function statusLabel(status: string): string {
  switch (status) {
    case "context_pending":
      return "Awaiting context";
    case "triage":
      return "Triage";
    case "panel":
      return "Panel running";
    case "agent_ready":
      return "Agent ready";
    default:
      return status;
  }
}

function initialProblem(): string {
  const params = new URLSearchParams(window.location.search);
  return params.get("problem") ?? "";
}
