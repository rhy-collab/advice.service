import { SignUpButton } from "@clerk/clerk-react";

const clerkEnabled = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY);

export function SiteHeader() {
  return (
    <header className="site-header">
      <a className="brand" href="/" aria-label="Charter Law home">
        <span className="brand-mark">CL</span>
        <span>
          <strong>Charter Law</strong>
          <small>charterlaw.services</small>
        </span>
      </a>
      <nav aria-label="Primary navigation">
        <a href="/#services">Services</a>
        <a href="/#pricing">Pricing</a>
        <a href="/#workflow">How it works</a>
        <a href="/portal">Portal</a>
        <a href="/attorney">Attorney</a>
      </nav>
      <div className="header-actions">
        <a className="header-signin" href="/login">
          Sign in
        </a>
        <SignUpAction />
        <a className="header-action" href="/#intake">
          Send a contract
        </a>
      </div>
    </header>
  );
}

function SignUpAction() {
  if (!clerkEnabled) {
    return (
      <a className="header-signup" href="/portal">
        Sign up
      </a>
    );
  }

  return (
    <SignUpButton forceRedirectUrl="/portal" mode="modal">
      <button className="header-signup" type="button">
        Sign up
      </button>
    </SignUpButton>
  );
}
