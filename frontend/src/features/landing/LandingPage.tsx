import { ChangeEvent, FormEvent, useState } from "react";
import { ArrowRight, Building2, FileSearch, FileText, LockKeyhole, UploadCloud } from "lucide-react";
import { AssistantCard } from "../../components/AssistantCard";
import { MatterCard } from "../../components/MatterCard";
import { SiteHeader } from "../../components/SiteHeader";
import { matters, pricing, proofPoints } from "../../lib/demoData";
import {
  checkContractMistakes,
  ContractCheckReport,
  PublicApiState,
  PublicIntakeRequest,
  PublicIntakeResponse,
  submitPublicIntake,
} from "../../lib/publicApi";

export function LandingPage() {
  return (
    <main>
      <SiteHeader />

      <section className="hero" id="top">
        <div className="hero-copy">
          <h1>Outside counsel that scales like software.</h1>
          <p>
            Charter Law provides attorney-reviewed contract redlines for startup
            teams. Send a contract through the portal, email, or Slack-style
            intake, get a flat fee, and receive practical markup approved by a
            reviewing attorney.
          </p>
          <div className="hero-actions">
            <a className="primary-action" href="#intake">
              Send a contract <ArrowRight aria-hidden="true" size={18} />
            </a>
            <a className="secondary-action" href="/login">
              Open client portal
            </a>
          </div>
          <dl className="hero-meta" aria-label="Service summary">
            <div>
              <dt>First scope</dt>
              <dd>Commercial contracts</dd>
            </div>
            <div>
              <dt>Launch model</dt>
              <dd>California-first</dd>
            </div>
            <div>
              <dt>Output</dt>
              <dd>Word redline</dd>
            </div>
          </dl>
        </div>

        <MatterPreview />
      </section>

      <section className="proof-band" id="services">
        {proofPoints.map(({ title, text, icon: Icon }) => (
          <article key={title}>
            <Icon aria-hidden="true" size={22} />
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>

      <section className="split-section" id="workflow">
        <div>
          <h2>AI prepares. An attorney approves and owns.</h2>
          <p>
            The product is designed around one rule: no AI output reaches a
            customer as legal advice. The system prepares summaries, issue
            lists, and fallback positions internally; the reviewing attorney
            decides what ships.
          </p>
        </div>
        <ol className="workflow-list">
          <li>
            <UploadCloud aria-hidden="true" />
            <span>Upload a .docx contract and answer a short intake.</span>
          </li>
          <li>
            <Building2 aria-hidden="true" />
            <span>Charter Law confirms scope and flat-fee pricing.</span>
          </li>
          <li>
            <LockKeyhole aria-hidden="true" />
            <span>AI prep stays internal until attorney approval is recorded.</span>
          </li>
          <li>
            <FileText aria-hidden="true" />
            <span>Download the final Word redline and practical cover note.</span>
          </li>
        </ol>
      </section>

      <section className="pricing-section" id="pricing">
        <div className="section-heading">
          <h2>Flat-fee contract review, clear before work begins.</h2>
          <p>
            Early pricing anchors for the manual MVP. Final public pricing and
            claims should be reviewed with counsel before launch.
          </p>
        </div>
        <div className="pricing-grid">
          {pricing.map(([name, price, detail]) => (
            <article key={name}>
              <h3>{name}</h3>
              <strong>{price}</strong>
              <p>{detail}</p>
            </article>
          ))}
        </div>
      </section>

      <ContractCheckerSection />

      <section className="portal-section" id="portal">
        <div>
          <h2>The client portal starts with predictability.</h2>
          <p>
            The first portal slice mirrors the visible General Legal pattern:
            sign in, view matters, upload documents, track status, and keep
            every client behind authenticated access.
          </p>
        </div>
        <a className="secondary-action dark" href="/login">
          Sign in to the portal
        </a>
      </section>

      <IntakeSection />
    </main>
  );
}

type IntakeState = "idle" | "submitting" | "submitted" | "error";

const initialIntake: PublicIntakeRequest = {
  name: "",
  email: "",
  company: "",
  contractType: "vendor_saas",
  urgency: "standard",
  serviceTier: "standard_redline",
  notes: "",
};

function IntakeSection() {
  const [intake, setIntake] = useState<PublicIntakeRequest>(initialIntake);
  const [state, setState] = useState<IntakeState>("idle");
  const [result, setResult] = useState<{ response: PublicIntakeResponse; source: PublicApiState } | null>(null);

  function updateField<Key extends keyof PublicIntakeRequest>(key: Key, value: PublicIntakeRequest[Key]) {
    setIntake((current) => ({ ...current, [key]: value }));
    if (state !== "submitting") {
      setState("idle");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("submitting");

    try {
      const response = await submitPublicIntake(intake);
      setResult(response);
      setState("submitted");
    } catch {
      setState("error");
    }
  }

  return (
    <section className="intake-section" id="intake">
      <div className="intake-copy">
        <h2>Send us the contract context first.</h2>
        <p>
          This starts a follow-up conversation, not legal advice. Charter Law
          confirms scope, payment, and the reviewing attorney path before legal
          work begins.
        </p>
      </div>
      <form className="intake-form" onSubmit={handleSubmit}>
        <div className="field-grid">
          <label>
            <span>Name</span>
            <input
              minLength={2}
              onChange={(event) => updateField("name", event.target.value)}
              required
              type="text"
              value={intake.name}
            />
          </label>
          <label>
            <span>Work email</span>
            <input
              onChange={(event) => updateField("email", event.target.value)}
              required
              type="email"
              value={intake.email}
            />
          </label>
          <label>
            <span>Company</span>
            <input
              minLength={2}
              onChange={(event) => updateField("company", event.target.value)}
              required
              type="text"
              value={intake.company}
            />
          </label>
          <label>
            <span>Contract type</span>
            <select
              onChange={(event) => updateField("contractType", event.target.value)}
              value={intake.contractType}
            >
              <option value="vendor_saas">Vendor SaaS agreement</option>
              <option value="mutual_nda">Mutual NDA</option>
              <option value="customer_msa">Customer MSA</option>
              <option value="other_commercial">Other commercial contract</option>
            </select>
          </label>
          <label>
            <span>Review tier</span>
            <select
              onChange={(event) => updateField("serviceTier", event.target.value as PublicIntakeRequest["serviceTier"])}
              value={intake.serviceTier}
            >
              <option value="simple_review">Simple review</option>
              <option value="standard_redline">Standard redline</option>
              <option value="full_negotiation">Full negotiation</option>
            </select>
          </label>
          <label>
            <span>Urgency</span>
            <select
              onChange={(event) => updateField("urgency", event.target.value as PublicIntakeRequest["urgency"])}
              value={intake.urgency}
            >
              <option value="standard">Standard</option>
              <option value="rush">Rush</option>
              <option value="not_sure">Not sure yet</option>
            </select>
          </label>
        </div>
        <label>
          <span>What should the reviewing attorney know?</span>
          <textarea
            maxLength={4000}
            onChange={(event) => updateField("notes", event.target.value)}
            rows={4}
            value={intake.notes}
          />
        </label>
        <button className="primary-action intake-submit" disabled={state === "submitting"} type="submit">
          {state === "submitting" ? "Sending..." : "Request review follow-up"}
          <ArrowRight aria-hidden="true" size={18} />
        </button>
        {state === "submitted" && result && (
          <p className="intake-result">
            {result.response.message} Reference: {result.response.intakeId}
            {result.source === "demo" ? " (demo mode)" : ""}.
          </p>
        )}
        {state === "error" && (
          <p className="intake-result intake-result-error">
            The intake could not be sent. Email hello@charterlaw.services as a fallback.
          </p>
        )}
      </form>
    </section>
  );
}

type CheckerState = "empty" | "selected" | "checking" | "complete" | "error";

function ContractCheckerSection() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<CheckerState>("empty");
  const [report, setReport] = useState<ContractCheckReport | null>(null);
  const [source, setSource] = useState<PublicApiState | null>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0] ?? null;
    setReport(null);
    setSource(null);

    if (selectedFile === null) {
      setFile(null);
      setState("empty");
      return;
    }

    setFile(selectedFile);
    setState(selectedFile.name.toLowerCase().endsWith(".docx") ? "selected" : "error");
  }

  async function runCheck() {
    if (file === null || state !== "selected") {
      return;
    }

    setState("checking");
    const result = await checkContractMistakes(file);
    setReport(result.report);
    setSource(result.source);
    setState("complete");
  }

  return (
    <section className="checker-section" id="checker">
      <div className="checker-copy">
        <span className="checker-label">
          <FileSearch aria-hidden="true" size={18} /> Free contract mistake checker
        </span>
        <h2>Catch obvious contract mistakes before you pay for review.</h2>
        <p>
          Drop in a Word document and get a quick preparation-only scan for typos,
          broken references, unused defined terms, and missing common sections.
        </p>
        <p className="privacy-promise">
          <LockKeyhole aria-hidden="true" size={16} />
          We never save or store your contract. The checker processes the upload in memory only.
        </p>
      </div>

      <div className="checker-tool" aria-label="Free contract mistake checker">
        <label className="file-picker checker-file-picker">
          <input type="file" accept=".docx" onChange={handleFileChange} />
          <span>{file?.name ?? "Choose a .docx contract"}</span>
        </label>
        <button
          className="upload-submit"
          disabled={state !== "selected"}
          onClick={runCheck}
          type="button"
        >
          {state === "checking" ? "Checking..." : "Run free check"}
        </button>

        {state === "empty" && <p className="checker-status">No document selected yet.</p>}
        {state === "selected" && <p className="checker-status">Ready to check {file?.name}.</p>}
        {state === "checking" && <p className="checker-status">Checking the document without saving it.</p>}
        {state === "error" && (
          <p className="checker-status checker-status-error">Please choose a `.docx` Word document.</p>
        )}
        {state === "complete" && report && (
          <CheckerReport report={report} source={source ?? "demo"} />
        )}
      </div>
    </section>
  );
}

function CheckerReport({ report, source }: { report: ContractCheckReport; source: PublicApiState }) {
  return (
    <div className="checker-report">
      <div className="checker-report-header">
        <div>
          <strong>{report.fileName}</strong>
          <span>{report.wordCount.toLocaleString()} words scanned · {source === "api" ? "FastAPI" : "demo"} result</span>
        </div>
        <span className={report.stored ? "storage-pill storage-pill-warning" : "storage-pill"}>
          {report.stored ? "Stored" : "Not stored"}
        </span>
      </div>
      <div className="checker-findings">
        {report.findings.length === 0 ? (
          <p>No obvious mechanical issues found. A lawyer should still review legal risk.</p>
        ) : (
          report.findings.map((finding, index) => (
            <article key={`${finding.type}-${index}`} className={`checker-finding checker-finding-${finding.severity}`}>
              <span>{finding.type.replaceAll("_", " ")}</span>
              <h3>{finding.title}</h3>
              <p>{finding.detail}</p>
              {finding.evidence && <small>Evidence: {finding.evidence}</small>}
            </article>
          ))
        )}
      </div>
      <p className="checker-disclaimer">{report.disclaimer}</p>
      <a className="primary-action checker-cta" href="#intake">
        Submit for attorney-reviewed redline <ArrowRight aria-hidden="true" size={18} />
      </a>
    </div>
  );
}

function MatterPreview() {
  return (
    <div className="product-preview" aria-label="Client portal preview">
      <div className="preview-topbar">
        <span>Client matter</span>
        <strong>Attorney in review</strong>
      </div>
      <MatterCard matter={matters[0]} />
      <AssistantCard />
    </div>
  );
}
