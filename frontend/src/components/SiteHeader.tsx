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
        <a href="/admin">Review</a>
      </nav>
      <a className="header-action" href="/#intake">
        Send a contract
      </a>
    </header>
  );
}
