import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from "@clerk/clerk-react";
import { ArrowRight, LockKeyhole, ShieldCheck } from "lucide-react";
import { SiteHeader } from "../../components/SiteHeader";

export function LoginPage({ demoMode = false }: { demoMode?: boolean }) {
  return (
    <main className="login-page">
      <SiteHeader />
      <section className="login-shell">
        <div className="login-card">
          <span className="portal-label">Client portal</span>
          <h1>Sign in to Charter Law.</h1>
          <p>
            Matters, documents, and attorney redlines sit behind authenticated
            access. Sign in to pick up where you left off.
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
              Add `VITE_CLERK_PUBLISHABLE_KEY` to enable live Clerk widgets. This
              local view is a static preview for build review.
            </p>
          )}

          <p className="login-footnote">
            New client? <a href="/#intake">Send a contract</a> and we will set up
            your account with the first matter.
          </p>
        </div>

        <aside className="login-aside">
          <h2>What is behind sign-in</h2>
          <ul className="login-benefits">
            <li>
              <ShieldCheck aria-hidden="true" size={18} />
              <span>
                <strong>Every matter in one place.</strong> Status, owner, and
                turnaround for each contract you have sent us.
              </span>
            </li>
            <li>
              <ShieldCheck aria-hidden="true" size={18} />
              <span>
                <strong>Attorney-reviewed deliverables.</strong> Download
                redlines and summaries as soon as review completes.
              </span>
            </li>
            <li>
              <ShieldCheck aria-hidden="true" size={18} />
              <span>
                <strong>Flat-fee billing history.</strong> No surprise invoices —
                the price is agreed before work starts.
              </span>
            </li>
          </ul>
          <p className="login-aside-note">
            Trouble signing in? Email{" "}
            <a href="mailto:hello@charterlaw.services">hello@charterlaw.services</a>.
          </p>
        </aside>
      </section>
    </main>
  );
}

function DemoSignInButton() {
  return (
    <a className="primary-action" href="/app">
      Continue to the app <ArrowRight aria-hidden="true" size={18} />
    </a>
  );
}

function ClerkSignInControls() {
  return (
    <>
      <SignedOut>
        <SignInButton forceRedirectUrl="/portal" mode="modal">
          <button className="primary-action" type="button">
            Sign in with Clerk <ArrowRight aria-hidden="true" size={18} />
          </button>
        </SignInButton>
        <SignUpButton forceRedirectUrl="/portal" mode="modal">
          <button className="secondary-action" type="button">
            Create an account
          </button>
        </SignUpButton>
      </SignedOut>
      <SignedIn>
        <div className="login-signed-in">
          <UserButton />
          <a className="primary-action" href="/portal">
            Go to your portal <ArrowRight aria-hidden="true" size={18} />
          </a>
        </div>
      </SignedIn>
    </>
  );
}
