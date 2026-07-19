import { useCallback, useEffect, useRef, useState } from "react";
import {
  AdviserQuotesResponse,
  GetAuthToken,
  ThreadDetail,
  ThreadSummary,
  addConsultant,
  createThread,
  engageCharter,
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
  if (role.startsWith("chair:")) return { name: role.slice(6), kind: "chair" };
  if (role.startsWith("consultant:")) return { name: role.slice(11), kind: "consultant" };
  if (role === "charter") return { name: "Charter Consultancy", kind: "charter" };
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
  const [composerText, setComposerText] = useState("");
  const [composerMode, setComposerMode] = useState<"agent" | "adviser">("agent");
  const [quotes, setQuotes] = useState<AdviserQuotesResponse | null>(null);
  const [matching, setMatching] = useState(false);
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

  const startThread = useCallback(
    async (text: string) => {
      const detail = await guarded(() => createThread(text, getAuthToken));
      if (detail) {
        setActive(detail);
        setQuotes(null);
        void refreshThreads();
      }
    },
    [getAuthToken, refreshThreads],
  );

  // Landing handoff: ?problem=... auto-starts the thread — no extra click.
  const autoStarted = useRef(false);
  useEffect(() => {
    const problem = new URLSearchParams(window.location.search).get("problem");
    if (problem && !autoStarted.current) {
      autoStarted.current = true;
      window.history.replaceState({}, "", "/app");
      void startThread(problem);
    }
  }, [startThread]);

  async function handleOpen(threadId: string) {
    const detail = await guarded(() => getThread(threadId, getAuthToken));
    if (detail) {
      setActive(detail);
      setQuotes(null);
      setComposerMode("agent");
    }
  }

  function openAdviserScreen() {
    setComposerMode("adviser");
    // Consultants unlock only at Stage 4 — matched to the ruled problem (invariant 7).
    if (active?.status === "agent_ready" && !quotes) {
      setMatching(true);
      getAdviserQuotes(active.id, getAuthToken)
        .then((r) => setQuotes(r))
        .catch(() => {})
        .finally(() => setMatching(false));
    }
  }

  async function handleCharter() {
    if (!active) return;
    setComposerMode("agent");
    const detail = await guarded(() => engageCharter(active.id, getAuthToken));
    if (detail) setActive(detail);
  }

  async function handleAddConsultant(name: string, title: string, hourlyRate: number) {
    if (!active) return;
    const detail = await guarded(() =>
      addConsultant(active.id, { name, title, hourly_rate: hourlyRate }, getAuthToken),
    );
    if (detail) {
      setActive(detail);
      setComposerMode("agent");
    }
  }

  async function handleSend() {
    if (!composerText.trim()) return;
    if (!active) {
      // First message IS the problem — it convenes the board.
      const text = composerText.trim();
      setComposerText("");
      await startThread(text);
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

        <>
            <div className="th-thread-scroll" ref={scrollRef}>
              {!active && (
                <div className="th-msg th-msg-chair">
                  <span className="th-msg-name">Eleanor Voss — Chair of the Board</span>
                  <p>
                    What's your biggest startup problem right now? Describe it once, right here.
                    I'll gather context, define the problem, and convene a board of advisors with
                    genuinely opposed views to debate it — free, all the way through.
                  </p>
                </div>
              )}

              {active && (
                <div className="th-problem">
                  <span className="th-problem-label">Problem</span>
                  <p>{active.problem_text}</p>
                </div>
              )}

              {active?.domain && (
                <div className="th-round">
                  <span className="th-domain-chip">{DOMAIN_LABELS[active.domain] ?? active.domain}</span>
                </div>
              )}

              {(active?.messages ?? []).map((message, index) => {
                const who = speaker(message.role);
                return (
                  <div key={index} className={`th-msg th-msg-${who.kind}`}>
                    <span className="th-msg-name">{who.name}</span>
                    <p>{message.content}</p>
                  </div>
                );
              })}

              {busy && <div className="th-msg th-msg-board"><span className="th-msg-name">The board</span><p className="th-typing">deliberating…</p></div>}
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
                  !active
                    ? "What's your biggest startup problem right now?"
                    : active.status === "agent_ready"
                      ? "Ask your agent about this problem…"
                      : "Answer the board — users, MRR or stage, customer, team, goals, hourly budget for an expert…"
                }
                rows={2}
              />
              <div className="th-composer-row">
                <div className="th-tabs">
                  <button className={composerMode === "agent" ? "active" : ""} onClick={() => setComposerMode("agent")}>🤖 Agent</button>
                  <button onClick={() => void handleCharter()}>
                    🏛 Charter Consultancy <span className="th-paid-dot" />
                  </button>
                  <button className={composerMode === "adviser" ? "active" : ""} onClick={openAdviserScreen}>
                    ➕ Add consultant <span className="th-paid-dot" />
                  </button>
                </div>
                <button className="th-send" disabled={busy} onClick={() => void handleSend()} aria-label="Send">→</button>
              </div>
            </div>
          </>

        {composerMode === "adviser" && (
          <div className="th-marketplace-overlay">
            <div className="th-marketplace">
              <header className="th-marketplace-head">
                <div>
                  <h1>Your matched advisers</h1>
                  <p>Real experts matched to this exact problem, self-set rates, one flat 10% platform fee. Book only when you're ready — everything else stays free.</p>
                </div>
                <button className="th-primary" onClick={() => setComposerMode("agent")}>← Back to your board</button>
              </header>

              {(!active || active.status !== "agent_ready") && (
                <section className="th-gate">
                  <h2>We need a little more information together first.</h2>
                  <p>
                    Advisers are matched to your specific problem once your board has ruled — that means finishing
                    the conversation: describe your problem, answer the context questions, and let the panel debate
                    it. When the Chair delivers the verdict, this tab unlocks with advisers hand-matched to exactly
                    what you're facing.
                  </p>
                  <button className="th-primary" onClick={() => setComposerMode("agent")}>Continue the conversation</button>
                </section>
              )}

              {active?.status === "agent_ready" && matching && (
                <p className="th-typing">Matching advisers to your problem from its full context — a few seconds…</p>
              )}

              {active?.status === "agent_ready" && quotes && quotes.quotes.length > 0 && (
                <section className="th-quotes">
                  <h2>Matched to your thread — {DOMAIN_LABELS[quotes.domain] ?? quotes.domain}</h2>
                  <p className="th-quotes-note">
                    Picked for this exact problem using your context, triage, and the board's verdict. Estimates are
                    not-to-exceed caps including the {quotes.quotes[0]?.platform_fee_pct ?? 10}% platform fee.
                  </p>
                  {quotes.quotes.map((quote) => (
                    <article key={quote.adviser_id} className="th-quote">
                      <div>
                        <h3>{quote.name}{quote.title ? <span className="th-quote-title"> — {quote.title}</span> : null}</h3>
                        <p className="th-quote-meta">{quote.metro} · ${quote.hourly_rate}/hr · est. {quote.estimated_hours} hrs</p>
                        <p>{quote.why_fit || quote.skills_profile}</p>
                      </div>
                      <div className="th-quote-price">
                        <span>${quote.estimated_total}</span>
                        <button
                          className="th-primary"
                          disabled={busy}
                          onClick={() => void handleAddConsultant(quote.name, quote.title || quote.skills_profile, quote.hourly_rate)}
                        >
                          + Add to chat
                        </button>
                      </div>
                    </article>
                  ))}
                </section>
              )}
            </div>
          </div>
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

