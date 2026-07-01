import { ArrowRight, Building2, FileText, LockKeyhole, UploadCloud } from "lucide-react";
import { AssistantCard } from "../../components/AssistantCard";
import { MatterCard } from "../../components/MatterCard";
import { SiteHeader } from "../../components/SiteHeader";
import { matters, pricing, proofPoints } from "../../lib/demoData";

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
            <a className="secondary-action" href="/portal">
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

      <section className="portal-section" id="portal">
        <div>
          <h2>The client portal starts with predictability.</h2>
          <p>
            The first portal slice mirrors the visible General Legal pattern:
            sign in, view matters, upload documents, track status, and keep
            every client behind authenticated access.
          </p>
        </div>
        <a className="secondary-action dark" href="/portal">
          View portal shell
        </a>
      </section>

      <section className="intake-section" id="intake">
        <h2>Ready for the first Charter Law intake flow.</h2>
        <p>
          The first live version should connect this call to action to Stripe
          hosted checkout and a lightweight intake form. For now, this is the
          local landing page for the future public site at charterlaw.services.
        </p>
        <a className="primary-action" href="mailto:hello@charterlaw.services">
          hello@charterlaw.services <ArrowRight aria-hidden="true" size={18} />
        </a>
      </section>
    </main>
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
