import { Matter, matters as demoMatters } from "./demoData";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/v1";

type ApiMatter = {
  id: string;
  fileName: string;
  serviceTier: "simple_review" | "standard_redline" | "full_negotiation";
  status: "intake" | "ai_review" | "attorney_queue" | "attorney_review" | "delivered" | "completed";
  uploadStatus: "awaiting_upload" | "uploaded";
  paymentStatus: "unpaid" | "checkout_pending" | "paid" | "failed" | "refunded";
  submittedAt: string;
  nextUpdateEtaMinutes: number | null;
  deliverableAvailable: boolean;
  riskScore: number;
  riskRoute: "fast_track" | "standard_review" | "escalate";
  attorneyReviewMinutes: number | null;
};

type MatterListResponse = {
  matters: ApiMatter[];
};

type CreateMatterResponse = {
  matterId: string;
  status: ApiMatter["status"];
  upload: {
    method: "PUT";
    url: string;
    expiresAt: string;
    mode: "gcs" | "demo";
  };
};

export type PortalApiState = "api" | "demo";
export type GetAuthToken = () => Promise<string | null>;
export type CheckoutMode = "stripe" | "demo";
export type UploadMode = "gcs" | "demo";

type CheckoutResponse = {
  checkoutUrl: string;
  mode: CheckoutMode;
  sessionId: string;
};

type UploadCompleteResponse = {
  matter: ApiMatter;
};

type DownloadResponse = {
  url: string;
};

type AttorneyApprovalResponse = {
  matter: ApiMatter;
};

export type AIPrepIssue = {
  title: string;
  severity: "low" | "medium" | "high" | "critical";
  detail: string;
  confidence: "weak" | "medium" | "strong";
  playbookCheckId: string | null;
  playbookCheckKey: string | null;
};

export type AIPrepResult = {
  matterId: string;
  mode: "stub" | "anthropic";
  summary: string;
  issues: AIPrepIssue[];
  createdAt: string;
};

type AttorneyAIPrepResponse = {
  prep: AIPrepResult;
};

type AIPrepFeedbackAction = "apply" | "dismiss" | "edit";

type AIPrepFeedbackResponse = {
  matterId: string;
  issueTitle: string;
  action: AIPrepFeedbackAction;
  reasonTag: string;
  playbookCheckId: string | null;
  accuracyCorrect: number | null;
  accuracyTotal: number | null;
};

type AttorneyReviewMinutesResponse = {
  matter: ApiMatter;
};

export async function fetchPortalMatters(
  getAuthToken?: GetAuthToken,
): Promise<{ matters: Matter[]; source: PortalApiState }> {
  try {
    const response = await fetch(`${API_BASE_URL}/matters`, {
      headers: await authHeaders(getAuthToken),
    });

    if (!response.ok) {
      throw new Error(`Matter list failed: ${response.status}`);
    }

    const payload = (await response.json()) as MatterListResponse;
    return {
      matters: payload.matters.map((matter) => mapApiMatter(matter)),
      source: "api",
    };
  } catch {
    return {
      matters: demoMatters,
      source: "demo",
    };
  }
}

export async function fetchAttorneyQueue(
  getAuthToken?: GetAuthToken,
): Promise<{ matters: Matter[]; source: PortalApiState }> {
  try {
    const response = await fetch(`${API_BASE_URL}/attorney/queue`, {
      headers: await authHeaders(getAuthToken),
    });

    if (!response.ok) {
      throw new Error(`Attorney queue failed: ${response.status}`);
    }

    const payload = (await response.json()) as MatterListResponse;
    return {
      matters: payload.matters.map((matter) => mapApiMatter(matter)),
      source: "api",
    };
  } catch {
    return {
      matters: demoMatters.filter((matter) => matter.status === "Attorney Review"),
      source: "demo",
    };
  }
}

export async function createPortalMatter(
  file: File,
  getAuthToken?: GetAuthToken,
): Promise<{ matter: Matter; source: PortalApiState; checkout: CheckoutResponse; uploadMode: UploadMode }> {
  const fileName = file.name;

  try {
    const response = await fetch(`${API_BASE_URL}/matters`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(await authHeaders(getAuthToken)),
      },
      body: JSON.stringify({
        fileName,
        serviceTier: "standard_redline",
        contractType: "commercial_contract",
        notes: "Created from the local Charter Law portal shell.",
      }),
    });

    if (!response.ok) {
      throw new Error(`Matter create failed: ${response.status}`);
    }

    const payload = (await response.json()) as CreateMatterResponse;

    await uploadContractFile(file, payload.upload);
    const uploadedMatter = await completeUpload(payload.matterId, getAuthToken);

    const matter = mapApiMatter(uploadedMatter.matter, "Just now");

    return {
      matter,
      source: "api",
      checkout: await createCheckout(payload.matterId, getAuthToken),
      uploadMode: payload.upload.mode,
    };
  } catch {
    const matterId = `matter_local_${Date.now()}`;
    return {
      matter: {
        id: matterId,
        file: fileName,
        type: "Standard redline",
        status: "Received",
        uploadStatus: "Uploaded",
        paymentStatus: "Demo checkout",
        submitted: "Just now",
        eta: "15 minutes",
        activeStage: 0,
        deliverableAvailable: false,
        riskScore: 0,
        riskRoute: "standard_review",
        attorneyReviewMinutes: null,
      },
      source: "demo",
      checkout: {
        checkoutUrl: `https://checkout.stripe.com/c/pay/demo-${matterId}`,
        mode: "demo",
        sessionId: `demo-${matterId}`,
      },
      uploadMode: "demo",
    };
  }
}

async function uploadContractFile(file: File, upload: CreateMatterResponse["upload"]): Promise<void> {
  if (upload.mode === "demo") {
    return;
  }

  const response = await fetch(upload.url, {
    method: upload.method,
    headers: {
      "Content-Type": file.type || "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
    body: file,
  });

  if (!response.ok) {
    throw new Error(`Contract upload failed: ${response.status}`);
  }
}

async function completeUpload(matterId: string, getAuthToken?: GetAuthToken): Promise<UploadCompleteResponse> {
  const response = await fetch(`${API_BASE_URL}/matters/${matterId}/upload-complete`, {
    method: "POST",
    headers: await authHeaders(getAuthToken),
  });

  if (!response.ok) {
    throw new Error(`Upload completion failed: ${response.status}`);
  }

  return (await response.json()) as UploadCompleteResponse;
}

async function createCheckout(matterId: string, getAuthToken?: GetAuthToken): Promise<CheckoutResponse> {
  const response = await fetch(`${API_BASE_URL}/matters/${matterId}/checkout`, {
    method: "POST",
    headers: await authHeaders(getAuthToken),
  });

  if (!response.ok) {
    throw new Error(`Checkout create failed: ${response.status}`);
  }

  return (await response.json()) as CheckoutResponse;
}

function mapApiMatter(matter: ApiMatter, submittedOverride?: string): Matter {
  return {
    id: matter.id,
    file: matter.fileName,
    type: mapServiceTier(matter.serviceTier),
    status: mapStatus(matter.status),
    uploadStatus: mapUploadStatus(matter.uploadStatus),
    paymentStatus: mapPaymentStatus(matter.paymentStatus),
    submitted: submittedOverride ?? formatSubmitted(matter.submittedAt),
    eta: matter.nextUpdateEtaMinutes === null ? "Complete" : `${matter.nextUpdateEtaMinutes} minutes`,
    activeStage: mapActiveStage(matter.status),
    deliverableAvailable: matter.deliverableAvailable,
    riskScore: matter.riskScore ?? 0,
    riskRoute: matter.riskRoute ?? "standard_review",
    attorneyReviewMinutes: matter.attorneyReviewMinutes ?? null,
  };
}

export async function fetchAttorneyAIPrep(
  matter: Matter,
  getAuthToken?: GetAuthToken,
): Promise<{ prep: AIPrepResult; source: PortalApiState }> {
  if (matter.id.startsWith("matter_demo_") || matter.id.startsWith("matter_local_")) {
    return { prep: demoAIPrep(matter), source: "demo" };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/attorney/matters/${matter.id}/ai-prep`, {
      headers: await authHeaders(getAuthToken),
    });
    if (!response.ok) {
      throw new Error(`AI prep failed: ${response.status}`);
    }
    const payload = (await response.json()) as AttorneyAIPrepResponse;
    return { prep: payload.prep, source: "api" };
  } catch {
    return { prep: demoAIPrep(matter), source: "demo" };
  }
}

export async function submitAttorneyAIPrepFeedback(
  matter: Matter,
  issueIndex: number,
  action: AIPrepFeedbackAction,
  getAuthToken?: GetAuthToken,
): Promise<{ feedback: AIPrepFeedbackResponse; source: PortalApiState }> {
  if (matter.id.startsWith("matter_demo_") || matter.id.startsWith("matter_local_")) {
    return {
      feedback: {
        matterId: matter.id,
        issueTitle: "Demo issue",
        action,
        reasonTag: `${action}_from_workbench`,
        playbookCheckId: null,
        accuracyCorrect: action === "apply" ? 1 : 0,
        accuracyTotal: 1,
      },
      source: "demo",
    };
  }

  const response = await fetch(`${API_BASE_URL}/attorney/matters/${matter.id}/ai-prep/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(await authHeaders(getAuthToken)),
    },
    body: JSON.stringify({
      issueIndex,
      action,
      reasonTag: `${action}_from_workbench`,
      correctedDetail: action === "edit" ? "Attorney edited this issue in the workbench." : null,
    }),
  });
  if (!response.ok) {
    throw new Error(`AI prep feedback failed: ${response.status}`);
  }
  return { feedback: (await response.json()) as AIPrepFeedbackResponse, source: "api" };
}

export async function recordAttorneyReviewMinutes(
  matter: Matter,
  minutes: number,
  getAuthToken?: GetAuthToken,
): Promise<{ matter: Matter; source: PortalApiState }> {
  if (matter.id.startsWith("matter_demo_") || matter.id.startsWith("matter_local_")) {
    return { matter: { ...matter, attorneyReviewMinutes: minutes }, source: "demo" };
  }

  const response = await fetch(`${API_BASE_URL}/attorney/matters/${matter.id}/review-minutes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(await authHeaders(getAuthToken)),
    },
    body: JSON.stringify({ minutes }),
  });
  if (!response.ok) {
    throw new Error(`Review minutes failed: ${response.status}`);
  }
  const payload = (await response.json()) as AttorneyReviewMinutesResponse;
  return { matter: mapApiMatter(payload.matter), source: "api" };
}

export async function fetchDeliverableUrl(matterId: string, getAuthToken?: GetAuthToken): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/matters/${matterId}/download`, {
    headers: await authHeaders(getAuthToken),
  });

  if (!response.ok) {
    throw new Error(`Download URL failed: ${response.status}`);
  }

  const payload = (await response.json()) as DownloadResponse;
  return payload.url;
}

export async function approveMatterDeliverable(
  matter: Matter,
  getAuthToken?: GetAuthToken,
): Promise<{ matter: Matter; source: PortalApiState }> {
  if (matter.id.startsWith("matter_demo_") || matter.id.startsWith("matter_local_")) {
    return {
      matter: {
        ...matter,
        status: "Delivered",
        eta: "Complete",
        activeStage: 3,
        deliverableAvailable: true,
      },
      source: "demo",
    };
  }

  const deliverableFileName = redlineFileName(matter.file);
  const response = await fetch(`${API_BASE_URL}/attorney/matters/${matter.id}/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(await authHeaders(getAuthToken)),
    },
    body: JSON.stringify({
      deliverableFileName,
      note: "Attorney approved the redline for client delivery from the internal review queue.",
    }),
  });

  if (!response.ok) {
    throw new Error(`Attorney approval failed: ${response.status}`);
  }

  const payload = (await response.json()) as AttorneyApprovalResponse;
  return {
    matter: mapApiMatter(payload.matter),
    source: "api",
  };
}

function demoAIPrep(matter: Matter): AIPrepResult {
  return {
    matterId: matter.id,
    mode: "stub",
    summary: `Internal preparation summary for ${matter.file}. Focus attorney review on the highest-risk clauses before approval.`,
    createdAt: new Date().toISOString(),
    issues: [
      {
        title: "Check limitation of liability",
        severity: matter.riskRoute === "escalate" ? "high" : "medium",
        detail: "Confirm the liability cap, carve-outs, and commercial value line up.",
        confidence: matter.riskRoute === "escalate" ? "weak" : "medium",
        playbookCheckId: "demo_check_liability",
        playbookCheckKey: "liability_cap",
      },
      {
        title: "Check termination mechanics",
        severity: "medium",
        detail: "Confirm notice, cure rights, and post-termination obligations are workable.",
        confidence: "medium",
        playbookCheckId: "demo_check_termination",
        playbookCheckKey: "termination",
      },
    ],
  };
}

function redlineFileName(fileName: string): string {
  return fileName.toLowerCase().endsWith(".docx")
    ? fileName.replace(/\\.docx$/i, "-redline.docx")
    : `${fileName}-redline.docx`;
}

function mapServiceTier(serviceTier: ApiMatter["serviceTier"]): string {
  const labels = {
    simple_review: "Simple review",
    standard_redline: "Standard redline",
    full_negotiation: "Full negotiation",
  };
  return labels[serviceTier];
}

function mapStatus(status: ApiMatter["status"]): string {
  const labels = {
    intake: "Received",
    ai_review: "AI Review",
    attorney_queue: "Queued for Attorney",
    attorney_review: "Attorney Review",
    delivered: "Delivered",
    completed: "Completed",
  };
  return labels[status];
}

function mapUploadStatus(status: ApiMatter["uploadStatus"]): string {
  const labels = {
    awaiting_upload: "Awaiting upload",
    uploaded: "Uploaded",
  };
  return labels[status];
}

function mapPaymentStatus(status: ApiMatter["paymentStatus"]): string {
  const labels = {
    unpaid: "Unpaid",
    checkout_pending: "Checkout pending",
    paid: "Paid",
    failed: "Payment failed",
    refunded: "Refunded",
  };
  return labels[status];
}

function mapActiveStage(status: ApiMatter["status"]): number {
  const stages = {
    intake: 0,
    ai_review: 1,
    attorney_queue: 1,
    attorney_review: 3,
    delivered: 4,
    completed: 4,
  };
  return stages[status];
}

function formatSubmitted(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
  }).format(date);
}

async function authHeaders(getAuthToken?: GetAuthToken): Promise<Record<string, string>> {
  const token = await getAuthToken?.();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}
