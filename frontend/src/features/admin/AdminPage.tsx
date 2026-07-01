import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, FileCheck2, Scale, ShieldCheck } from "lucide-react";
import { SiteHeader } from "../../components/SiteHeader";
import { Matter, matters as fallbackMatters } from "../../lib/demoData";
import {
  approveMatterDeliverable,
  fetchAttorneyQueue,
  GetAuthToken,
  PortalApiState,
} from "../../lib/portalApi";

type ApprovalState = {
  matterId: string;
  message: string;
  status: "idle" | "pending" | "success" | "error";
};

export function AdminPage({
  demoMode = false,
  getAuthToken,
}: {
  demoMode?: boolean;
  getAuthToken?: GetAuthToken;
}) {
  const [matters, setMatters] = useState<Matter[]>(fallbackMatters);
  const [apiSource, setApiSource] = useState<PortalApiState>("demo");
  const [isLoading, setIsLoading] = useState(true);
  const [approvalState, setApprovalState] = useState<ApprovalState>({
    matterId: "",
    message: "",
    status: "idle",
  });

  useEffect(() => {
    let isActive = true;

    fetchAttorneyQueue(getAuthToken).then((result) => {
      if (!isActive) {
        return;
      }
      setMatters(result.matters);
      setApiSource(result.source);
      setIsLoading(false);
    });

    return () => {
      isActive = false;
    };
  }, [getAuthToken]);

  const queueStats = useMemo(() => {
    const readyToApprove = matters.filter(canApproveMatter).length;
    const delivered = matters.filter((matter) => matter.deliverableAvailable).length;

    return { delivered, readyToApprove, total: matters.length };
  }, [matters]);

  async function approveMatter(matter: Matter) {
    if (!canApproveMatter(matter)) {
      setApprovalState({
        matterId: matter.id,
        message: "Upload and payment must both be complete before attorney approval.",
        status: "error",
      });
      return;
    }

    setApprovalState({
      matterId: matter.id,
      message: `Approving ${matter.file} for delivery...`,
      status: "pending",
    });

    try {
      const result = await approveMatterDeliverable(matter, getAuthToken);
      setMatters((current) => current.map((item) => (item.id === matter.id ? result.matter : item)));
      setApiSource(result.source);
      setApprovalState({
        matterId: matter.id,
        message: `${matter.file} is approved and ready for client download.`,
        status: "success",
      });
    } catch {
      setApprovalState({
        matterId: matter.id,
        message: "Approval failed. Check that payment is paid and the upload is complete.",
        status: "error",
      });
    }
  }

  return (
    <main className="admin-page">
      <SiteHeader />
      <section className="admin-shell">
        <div className="admin-hero">
          <span className="portal-label">Internal review</span>
          <h1>Attorney delivery queue</h1>
          <p>
            Review matter readiness, approve the final Word redline, and keep
            client delivery behind attorney judgment.
          </p>
          {demoMode && (
            <p className="demo-note">
              Demo mode is visible until Clerk is configured. This screen is an
              internal workflow shell, not a public client control.
            </p>
          )}
        </div>

        <div className="admin-summary" aria-label="Review queue summary">
          <div>
            <Scale size={18} />
            <strong>{queueStats.readyToApprove}</strong>
            <span>Ready for approval</span>
          </div>
          <div>
            <FileCheck2 size={18} />
            <strong>{queueStats.delivered}</strong>
            <span>Delivered</span>
          </div>
          <div>
            <ShieldCheck size={18} />
            <strong>{queueStats.total}</strong>
            <span>Total matters</span>
          </div>
        </div>

        <p className={`api-source api-source-${apiSource}`}>
          {isLoading
            ? "Checking local FastAPI backend..."
            : apiSource === "api"
              ? "Connected to local FastAPI backend."
              : "Using local demo data until the FastAPI backend is running."}
        </p>

        <div className="review-list" aria-label="Attorney review queue">
          {matters.map((matter) => (
            <article className="review-row" key={matter.id}>
              <div className="review-main">
                <span className="review-icon">
                  <FileCheck2 size={20} />
                </span>
                <div>
                  <h2>{matter.file}</h2>
                  <p>
                    {matter.type} · {matter.status} · {matter.eta}
                  </p>
                </div>
              </div>

              <div className="review-checks">
                <ReadinessPill label="Upload" ready={matter.uploadStatus === "Uploaded"} value={matter.uploadStatus} />
                <ReadinessPill label="Payment" ready={matter.paymentStatus === "Paid"} value={matter.paymentStatus} />
                <ReadinessPill
                  label="Delivery"
                  ready={matter.deliverableAvailable}
                  value={matter.deliverableAvailable ? "Ready" : "Locked"}
                />
              </div>

              <button
                className="approve-button"
                disabled={!canApproveMatter(matter) || approvalState.status === "pending"}
                onClick={() => approveMatter(matter)}
                type="button"
              >
                <CheckCircle2 size={16} />
                {matter.deliverableAvailable ? "Approved" : "Approve redline"}
              </button>

              {approvalState.matterId === matter.id && approvalState.message && (
                <p className={`approval-message approval-message-${approvalState.status}`}>
                  {approvalState.message}
                </p>
              )}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function ReadinessPill({ label, ready, value }: { label: string; ready: boolean; value: string }) {
  return (
    <span className={`readiness-pill ${ready ? "readiness-pill-ready" : ""}`}>
      <strong>{label}</strong>
      {value}
    </span>
  );
}

function canApproveMatter(matter: Matter): boolean {
  return matter.uploadStatus === "Uploaded" && matter.paymentStatus === "Paid" && !matter.deliverableAvailable;
}
