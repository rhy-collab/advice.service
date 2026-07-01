import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";
import { ArrowRight, BadgeCheck, CircleDollarSign, Clock3, FileCheck2, LockKeyhole, UploadCloud } from "lucide-react";
import { AssistantCard } from "../../components/AssistantCard";
import { MatterCard } from "../../components/MatterCard";
import { SiteHeader } from "../../components/SiteHeader";
import { Matter, matters as fallbackMatters } from "../../lib/demoData";
import {
  CheckoutMode,
  createPortalMatter,
  fetchDeliverableUrl,
  fetchPortalMatters,
  GetAuthToken,
  PortalApiState,
  UploadMode,
} from "../../lib/portalApi";

export function PortalPage({
  demoMode = false,
  getAuthToken,
}: {
  demoMode?: boolean;
  getAuthToken?: GetAuthToken;
}) {
  return (
    <main className="portal-page">
      <SiteHeader />
      <section className="portal-hero">
        <div className="portal-login">
          <span className="portal-label">Client portal</span>
          <h1>Sign in to view your matters.</h1>
          <p>
            Charter Law matters are protected behind authenticated access. Clerk
            will handle Google sign-in, work email, passwords, and organisation
            membership.
          </p>
          <div className="login-actions">
            {demoMode ? <DemoSignInButton /> : <ClerkSignInControls />}
            <button className="secondary-action" type="button">
              Sign in with Google
            </button>
          </div>
          <p className="security-note">
            <LockKeyhole aria-hidden="true" size={16} />
            Secured with encrypted connections and authenticated access.
          </p>
          {demoMode && (
            <p className="demo-note">
              Add `VITE_CLERK_PUBLISHABLE_KEY` to enable live Clerk widgets.
              This local view keeps a demo dashboard visible for build review.
            </p>
          )}
        </div>

        <PortalDashboard getAuthToken={getAuthToken} />
      </section>
    </main>
  );
}

function DemoSignInButton() {
  return (
    <button className="primary-action" type="button">
      Clerk demo sign-in <ArrowRight aria-hidden="true" size={18} />
    </button>
  );
}

function ClerkSignInControls() {
  return (
    <>
      <SignedOut>
        <SignInButton mode="modal">
          <button className="primary-action" type="button">
            Sign in with Clerk <ArrowRight aria-hidden="true" size={18} />
          </button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </>
  );
}

function PortalDashboard({ getAuthToken }: { getAuthToken?: GetAuthToken }) {
  const [matters, setMatters] = useState<Matter[]>(fallbackMatters);
  const [apiSource, setApiSource] = useState<PortalApiState>("demo");
  const [isLoadingMatters, setIsLoadingMatters] = useState(true);
  const [downloadMessage, setDownloadMessage] = useState("");

  useEffect(() => {
    let isActive = true;

    fetchPortalMatters(getAuthToken).then((result) => {
      if (!isActive) {
        return;
      }
      setMatters(result.matters);
      setApiSource(result.source);
      setIsLoadingMatters(false);
    });

    return () => {
      isActive = false;
    };
  }, [getAuthToken]);

  const dashboardStats = useMemo(() => {
    const activeCount = matters.filter((matter) => matter.status !== "Delivered" && matter.status !== "Completed").length;
    const readyCount = matters.filter((matter) => matter.status === "Delivered" || matter.status === "Completed").length;

    return {
      activeCount,
      readyCount,
    };
  }, [matters]);

  function handleMatterCreated(matter: Matter, source: PortalApiState) {
    setMatters((currentMatters) => [matter, ...currentMatters]);
    setApiSource(source);
  }

  async function handleDownload(matter: Matter) {
    if (!matter.deliverableAvailable) {
      setDownloadMessage("The redline is still waiting for attorney approval.");
      return;
    }

    try {
      const url = apiSource === "api"
        ? await fetchDeliverableUrl(matter.id, getAuthToken)
        : "https://storage.googleapis.com/demo/redline.docx";
      setDownloadMessage(`Approved redline ready: ${matter.file}`);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch {
      setDownloadMessage("The redline is marked ready, but the download link could not be created.");
    }
  }

  const featuredMatter = matters[0] ?? fallbackMatters[0];

  return (
    <div className="portal-dashboard">
      <div className="dashboard-header">
        <div>
          <span>Acme Labs</span>
          <h2>Matters dashboard</h2>
        </div>
        <a className="upload-button" href="#upload-contract">
          <UploadCloud size={17} /> Upload .docx
        </a>
      </div>

      <p className={`api-source api-source-${apiSource}`}>
        {isLoadingMatters
          ? "Checking local FastAPI backend..."
          : apiSource === "api"
            ? "Connected to local FastAPI backend."
            : "Using local demo data until the FastAPI backend is running."}
      </p>

      <UploadPanel getAuthToken={getAuthToken} onMatterCreated={handleMatterCreated} />

      <div className="dashboard-stats">
        <div>
          <Clock3 size={18} />
          <strong>{dashboardStats.activeCount} active</strong>
          <span>Live matters</span>
        </div>
        <div>
          <BadgeCheck size={18} />
          <strong>{dashboardStats.readyCount} ready</strong>
          <span>Delivered redline</span>
        </div>
        <div>
          <CircleDollarSign size={18} />
          <strong>$500</strong>
          <span>Standard tier</span>
        </div>
      </div>

      <div className="matter-table" aria-label="Client matters">
        <div className="matter-table-head">
          <span>File name</span>
          <span>Status</span>
          <span>Upload</span>
          <span>Payment</span>
          <span>Deliverable</span>
          <span>Submitted</span>
          <span>Next update</span>
        </div>
        {matters.map((matter) => (
          <div className="matter-table-row" key={matter.file}>
            <span>{matter.file}</span>
            <strong>{matter.status}</strong>
            <span>{matter.uploadStatus}</span>
            <span>{matter.paymentStatus}</span>
            <button
              className="download-link"
              disabled={!matter.deliverableAvailable}
              onClick={() => handleDownload(matter)}
              type="button"
            >
              {matter.deliverableAvailable ? "Download redline" : "Pending approval"}
            </button>
            <span>{matter.submitted}</span>
            <span>{matter.eta}</span>
          </div>
        ))}
      </div>

      {downloadMessage && <p className="download-message">{downloadMessage}</p>}

      <MatterCard matter={featuredMatter} />
      <AssistantCard />
    </div>
  );
}

type UploadState = "empty" | "selected" | "pending" | "complete" | "error";

function UploadPanel({
  getAuthToken,
  onMatterCreated,
}: {
  getAuthToken?: GetAuthToken;
  onMatterCreated: (matter: Matter, source: PortalApiState) => void;
}) {
  const [fileName, setFileName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("empty");
  const [createdSource, setCreatedSource] = useState<PortalApiState | null>(null);
  const [checkoutUrl, setCheckoutUrl] = useState("");
  const [checkoutMode, setCheckoutMode] = useState<CheckoutMode | null>(null);
  const [uploadMode, setUploadMode] = useState<UploadMode | null>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) {
      setFileName("");
      setSelectedFile(null);
      setUploadState("empty");
      return;
    }

    setFileName(file.name);
    setSelectedFile(file.name.toLowerCase().endsWith(".docx") ? file : null);
    setUploadState(file.name.toLowerCase().endsWith(".docx") ? "selected" : "error");
    setCheckoutUrl("");
    setCheckoutMode(null);
    setUploadMode(null);
  }

  async function createMatter() {
    if (uploadState !== "selected" || selectedFile === null) {
      return;
    }

    setUploadState("pending");
    const result = await createPortalMatter(selectedFile, getAuthToken);
    setCreatedSource(result.source);
    setCheckoutUrl(result.checkout.checkoutUrl);
    setCheckoutMode(result.checkout.mode);
    setUploadMode(result.uploadMode);
    onMatterCreated(result.matter, result.source);
    setUploadState("complete");
  }

  return (
    <section className={`upload-panel upload-panel-${uploadState}`} id="upload-contract" aria-label="Upload contract">
      <div className="upload-panel-copy">
        <span className="upload-icon">
          {uploadState === "complete" ? <FileCheck2 size={20} /> : <UploadCloud size={20} />}
        </span>
        <div>
          <h3>Upload a contract for review</h3>
          <p>
            Choose a `.docx` contract. The real backend will create a matter,
            issue a short-lived Google Cloud Storage upload URL, then send the
            customer to Stripe hosted checkout.
          </p>
        </div>
      </div>

      <div className="upload-controls">
        <label className="file-picker">
          <input type="file" accept=".docx" onChange={handleFileChange} />
          <span>{fileName || "Choose .docx file"}</span>
        </label>
        <button
          className="upload-submit"
          disabled={uploadState !== "selected"}
          onClick={createMatter}
          type="button"
        >
          {uploadState === "pending" ? "Creating matter..." : "Create matter"}
        </button>
      </div>

      <UploadStatus
        checkoutMode={checkoutMode}
        checkoutUrl={checkoutUrl}
        fileName={fileName}
        source={createdSource}
        state={uploadState}
        uploadMode={uploadMode}
      />
    </section>
  );
}

function UploadStatus({
  checkoutMode,
  checkoutUrl,
  state,
  fileName,
  source,
  uploadMode,
}: {
  checkoutMode: CheckoutMode | null;
  checkoutUrl: string;
  state: UploadState;
  fileName: string;
  source: PortalApiState | null;
  uploadMode: UploadMode | null;
}) {
  if (state === "empty") {
    return <p className="upload-status">No document selected yet.</p>;
  }

  if (state === "error") {
    return (
      <p className="upload-status upload-status-error">
        Please choose a Word `.docx` file. PDF and legacy `.doc` upload can come later.
      </p>
    );
  }

  if (state === "pending") {
    return <p className="upload-status">Preparing secure upload and draft matter for {fileName}.</p>;
  }

  if (state === "complete") {
    return (
      <div className="upload-status upload-status-success">
        <p>
          Matter created for {fileName}
          {source === "api" ? " through FastAPI" : " in local demo mode"}. Upload is
          {uploadMode === "gcs" ? " confirmed in Google Cloud Storage" : " confirmed on the local demo path"}. Checkout is ready
          {checkoutMode === "stripe" ? " through Stripe" : " in demo mode"}.
        </p>
        {checkoutUrl && (
          <a href={checkoutUrl} rel="noreferrer" target="_blank">
            Open hosted checkout
          </a>
        )}
      </div>
    );
  }

  return <p className="upload-status">Ready to create a matter for {fileName}.</p>;
}
