import React from "react";
import { createRoot } from "react-dom/client";
import { ClerkProvider, useAuth } from "@clerk/clerk-react";
import { AdminPage } from "./features/admin/AdminPage";
import { AttorneyWorkbenchPage } from "./features/admin/AttorneyWorkbenchPage";
import { LoginPage } from "./features/auth/LoginPage";
import { LandingPage } from "./features/landing/LandingPage";
import { PortalPage } from "./features/portal/PortalPage";
import { ThreadsPage } from "./features/threads/ThreadsPage";
import { initFrontendSentry } from "./lib/sentry";
import "./styles.css";

initFrontendSentry();

// Clerk temporarily bypassed — users go straight into the app (demo auth).
// To re-enable: restore the import.meta.env read below.
const clerkPublishableKey = undefined as string | undefined;
// const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY as string | undefined;
type AppRoute = "admin" | "app" | "attorney" | "home" | "login" | "portal";

function App() {
  const route = currentRoute();

  if (!clerkPublishableKey) {
    if (route === "admin" || route === "attorney") {
      return route === "attorney" ? <AttorneyWorkbenchPage demoMode /> : <AdminPage demoMode />;
    }
    if (route === "login") {
      return <LoginPage demoMode />;
    }
    if (route === "app") {
      return <ThreadsPage />;
    }
    return route === "portal" ? <PortalPage demoMode /> : <LandingPage />;
  }

  return (
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <AuthenticatedApp route={route} />
    </ClerkProvider>
  );
}

function AuthenticatedApp({ route }: { route: AppRoute }) {
  const { getToken } = useAuth();

  if (route === "admin" || route === "attorney") {
    return route === "attorney" ? <AttorneyWorkbenchPage getAuthToken={getToken} /> : <AdminPage getAuthToken={getToken} />;
  }

  if (route === "login") {
    return <LoginPage />;
  }

  if (route === "app") {
    return <ThreadsPage getAuthToken={getToken} />;
  }

  return route === "portal" ? <PortalPage getAuthToken={getToken} /> : <LandingPage />;
}

function currentRoute(): AppRoute {
  if (window.location.pathname === "/portal") {
    return "portal";
  }
  if (window.location.pathname === "/app") {
    return "app";
  }
  if (window.location.pathname === "/login") {
    return "login";
  }
  if (window.location.pathname === "/admin") {
    return "admin";
  }
  if (window.location.pathname === "/attorney") {
    return "attorney";
  }
  return "home";
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
