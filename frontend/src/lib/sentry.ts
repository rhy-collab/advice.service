import * as Sentry from "@sentry/react";

export function initFrontendSentry() {
  const dsn = import.meta.env.VITE_SENTRY_DSN as string | undefined;
  if (!dsn) {
    return false;
  }

  Sentry.init({
    dsn,
    tracesSampleRate: 0,
  });
  return true;
}
