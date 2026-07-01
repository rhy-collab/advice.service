import React from "react";
import { createRoot } from "react-dom/client";
import { ClerkProvider, useAuth } from "@clerk/clerk-react";
import { AdminPage } from "./features/admin/AdminPage";
import { AttorneyWorkbenchPage } from "./features/admin/AttorneyWorkbenchPage";
import { LandingPage } from "./features/landing/LandingPage";
import { PortalPage } from "./features/portal/PortalPage";
import { initFrontendSentry } from "./lib/sentry";
import "./styles.css";

initFrontendSentry();

const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY as string | undefined;
type AppRoute = "admin" | "attorney" | "home" | "portal";

function App() {
  const route = currentRoute();

  if (!clerkPublishableKey) {
    if (route === "admin" || route === "attorney") {
      return route === "attorney" ? <AttorneyWorkbenchPage demoMode /> : <AdminPage demoMode />;
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

  return route === "portal" ? <PortalPage getAuthToken={getToken} /> : <LandingPage />;
}

function currentRoute(): AppRoute {
  if (window.location.pathname === "/portal") {
    return "portal";
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
