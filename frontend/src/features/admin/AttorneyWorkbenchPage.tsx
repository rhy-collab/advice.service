import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  FileCheck2,
  FileSearch,
  Pencil,
  XCircle,
} from "lucide-react";
import { SiteHeader } from "../../components/SiteHeader";
import { Matter, matters as fallbackMatters } from "../../lib/demoData";
import {
  AIPrepResult,
  approveMatterDeliverable,
  fetchAttorneyAIPrep,
  fetchAttorneyQueue,
  GetAuthToken,
  PortalApiState,
  recordAttorneyReviewMinutes,
  submitAttorneyAIPrepFeedback,
} from "../../lib/portalApi";

type ActionState = {
  message: string;
  status: "idle" | "pending" | "success" | "error";
};

export function AttorneyWorkbenchPage({
  demoMode = false,
  getAuthToken,
}: {
  demoMode?: boolean;
  getAuthToken?: GetAuthToken;
}) {
  const [matters, setMatters] = useState<Matter[]>(fallbackMatters);
  const [selectedId, setSelectedId] = useState(fallbackMatters[0]?.id ?? "");
  const [prep, setPrep] = useState<AIPrepResult | null>(null);
  const [minutes, setMinutes] = useState(0);
  const [apiSource, setApiSource] = useState<PortalApiState>("demo");
  const [isLoading, setIsLoading] = useState(true);
  const [actionState, setActionState] = useState<ActionState>({ message: "", status: "idle" });

  useEffect(() => {
    let isActive = true;
    fetchAttorneyQueue(getAuthToken).then((result) => {
      if (!isActive) {
        return;
      }
      setMatters(result.matters);
      setSelectedId((current) => current || result.matters[0]?.id || "");
      setApiSource(result.source);
      setIsLoading(false);
    });
    return () => {
      isActive = false;
    };
  }, [getAuthToken]);

  const selectedMatter = useMemo(
    () => matters.find((matter) => matter.id === selectedId) ?? matters[0],
    [matters, selectedId],
  );

  useEffect(() => {
    if (!selectedMatter) {
      return;
    }
    let isActive = true;
    setPrep(null);
    setMinutes(selectedMatter.attorneyReviewMinutes ?? 0);
    fetchAttorneyAIPrep(selectedMatter, getAuthToken).then((result) => {
      if (!isActive) {
        return;
      }
      setPrep(result.prep);
      setApiSource(result.source);
    });
    return () => {
      isActive = false;
    };
  }, [getAuthToken, selectedMatter]);

  const stats = useMemo(() => {
    const escalated = matters.filter((matter) => matter.riskRoute === "escalate").length;
    const weak = prep?.issues.filter((issue) => issue.confidence === "weak").length ?? 0;
    return { escalated, total: matters.length, weak };
  }, [matters, prep]);

  async function handleIssueAction(issueIndex: number, action: "apply" | "dismiss" | "edit") {
    if (!selectedMatter) {
      return;
    }
    setActionState({ message: `${actionLabel(action)} issue...`, status: "pending" });
    try {
      const result = await submitAttorneyAIPrepFeedback(selectedMatter, issueIndex, action, getAuthToken);
      setApiSource(result.source);
      setActionState({
        message: `${result.feedback.issueTitle} marked as ${action}.`,
        status: "success",
      });
    } catch {
      setActionState({ message: "Feedback failed. Check the backend and attorney auth.", status: "error" });
    }
  }

  async function saveMinutes() {
    if (!selectedMatter) {
      return;
    }
    setActionState({ message: "Saving review minutes...", status: "pending" });
    try {
      const result = await recordAttorneyReviewMinutes(selectedMatter, minutes, getAuthToken);
      setMatters((current) => current.map((matter) => (matter.id === result.matter.id ? result.matter : matter)));
      setApiSource(result.source);
      setActionState({ message: "Review minutes saved.", status: "success" });
    } catch {
      setActionState({ message: "Minutes were not saved.", status: "error" });
    }
  }

  async function approveSelectedMatter() {
    if (!selectedMatter) {
      return;
    }
    setActionState({ message: "Approving redline...", status: "pending" });
    try {
      const result = await approveMatterDeliverable(selectedMatter, getAuthToken);
      setMatters((current) => current.map((matter) => (matter.id === result.matter.id ? result.matter : matter)));
      setApiSource(result.source);
      setActionState({ message: "Matter approved for client delivery.", status: "success" });
    } catch {
      setActionState({ message: "Approval failed. Upload and payment must be complete.", status: "error" });
    }
  }

  return (
    <main className="admin-page">
      <SiteHeader />
      <section className="admin-shell attorney-workbench">
        <div className="admin-hero">
          <span className="portal-label">Attorney workbench</span>
          <h1>Review AI prep and approve delivery</h1>
          <p>Work the matter queue, action AI issues, record review minutes, and approve only after attorney judgment.</p>
          {demoMode && <p className="demo-note">Demo mode is visible until Clerk and FastAPI auth are configured.</p>}
        </div>

        <div className="admin-summary" aria-label="Workbench summary">
          <div>
            <FileCheck2 size={18} />
            <strong>{stats.total}</strong>
            <span>Queued matters</span>
          </div>
          <div>
            <AlertTriangle size={18} />
            <strong>{stats.escalated}</strong>
            <span>Escalated</span>
          </div>
          <div>
            <FileSearch size={18} />
            <strong>{stats.weak}</strong>
            <span>Weak-confidence issues</span>
          </div>
        </div>

        <p className={`api-source api-source-${apiSource}`}>
          {isLoading
            ? "Checking local FastAPI backend..."
            : apiSource === "api"
              ? "Connected to local FastAPI backend."
              : "Using local demo data until the FastAPI backend is running."}
        </p>

        <div className="workbench-grid">
          <aside className="workbench-queue" aria-label="Matter queue">
            {matters.map((matter) => (
              <button
                className={`queue-select ${matter.id === selectedMatter?.id ? "queue-select-active" : ""}`}
                key={matter.id}
                onClick={() => setSelectedId(matter.id)}
                type="button"
              >
                <strong>{matter.file}</strong>
                <span>{matter.type} · {riskLabel(matter.riskRoute)} · {matter.riskScore}</span>
              </button>
            ))}
          </aside>

          {selectedMatter && (
            <section className="workbench-detail" aria-label="Selected matter review">
              <div className="workbench-matter-head">
                <div>
                  <span className={`risk-badge risk-badge-${selectedMatter.riskRoute}`}>
                    {riskLabel(selectedMatter.riskRoute)}
                  </span>
                  <h2>{selectedMatter.file}</h2>
                  <p>
                    {selectedMatter.status} · {selectedMatter.uploadStatus} · {selectedMatter.paymentStatus}
                  </p>
                </div>
                <button className="approve-button" onClick={approveSelectedMatter} type="button">
                  <CheckCircle2 size={16} />
                  {selectedMatter.deliverableAvailable ? "Approved" : "Approve"}
                </button>
              </div>

              <div className="minutes-row">
                <label>
                  <Clock3 size={16} />
                  <span>Review minutes</span>
                  <input
                    min={0}
                    max={600}
                    onChange={(event) => setMinutes(Number(event.target.value))}
                    type="number"
                    value={minutes}
                  />
                </label>
                <button className="secondary-action" onClick={saveMinutes} type="button">
                  Save
                </button>
              </div>

              <div className="ai-prep-panel">
                <div className="ai-prep-summary">
                  <span>{prep?.mode ?? "loading"}</span>
                  <p>{prep?.summary ?? "Loading internal AI preparation..."}</p>
                </div>

                <div className="issue-list">
                  {(prep?.issues ?? []).map((issue, index) => (
                    <article className={`issue-row issue-row-${issue.confidence}`} key={`${issue.title}-${index}`}>
                      <div>
                        <span className="issue-meta">
                          {issue.severity} · {issue.confidence} confidence
                        </span>
                        <h3>{issue.title}</h3>
                        <p>{issue.detail}</p>
                        {issue.playbookCheckKey && <small>Playbook: {issue.playbookCheckKey}</small>}
                      </div>
                      <div className="issue-actions">
                        <button onClick={() => handleIssueAction(index, "apply")} title="Apply issue" type="button">
                          <CheckCircle2 size={16} />
                        </button>
                        <button onClick={() => handleIssueAction(index, "dismiss")} title="Dismiss issue" type="button">
                          <XCircle size={16} />
                        </button>
                        <button onClick={() => handleIssueAction(index, "edit")} title="Edit issue" type="button">
                          <Pencil size={16} />
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </div>

              {actionState.message && (
                <p className={`approval-message approval-message-${actionState.status}`}>{actionState.message}</p>
              )}
            </section>
          )}
        </div>
      </section>
    </main>
  );
}

function actionLabel(action: "apply" | "dismiss" | "edit") {
  return action === "apply" ? "Applying" : action === "dismiss" ? "Dismissing" : "Editing";
}

function riskLabel(route: Matter["riskRoute"]) {
  const labels = {
    fast_track: "Fast-track",
    standard_review: "Standard review",
    escalate: "Escalate",
  };
  return labels[route];
}
