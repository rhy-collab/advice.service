const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/v1";

export type ContractCheckFinding = {
  type: "broken_cross_reference" | "missing_standard_section" | "possible_typo" | "unused_defined_term";
  severity: "info" | "warning";
  title: string;
  detail: string;
  evidence: string | null;
};

export type ContractCheckReport = {
  fileName: string;
  stored: boolean;
  wordCount: number;
  findings: ContractCheckFinding[];
  disclaimer: string;
  nextStep: string;
};

export type PublicApiState = "api" | "demo";

export type PublicIntakeRequest = {
  name: string;
  email: string;
  company: string;
  contractType: string;
  urgency: "standard" | "rush" | "not_sure";
  serviceTier: "simple_review" | "standard_redline" | "full_negotiation";
  notes: string;
};

export type PublicIntakeResponse = {
  intakeId: string;
  status: string;
  createdAt: string;
  message: string;
};

export async function checkContractMistakes(file: File): Promise<{ report: ContractCheckReport; source: PublicApiState }> {
  const body = new FormData();
  body.append("file", file);

  try {
    const response = await fetch(`${API_BASE_URL}/public/check-contract`, {
      method: "POST",
      body,
    });

    if (!response.ok) {
      throw new Error(`Contract check failed: ${response.status}`);
    }

    return {
      report: (await response.json()) as ContractCheckReport,
      source: "api",
    };
  } catch {
    return {
      report: demoContractReport(file.name),
      source: "demo",
    };
  }
}

function demoContractReport(fileName: string): ContractCheckReport {
  return {
    fileName,
    stored: false,
    wordCount: 1240,
    findings: [
      {
        type: "possible_typo",
        severity: "warning",
        title: "Possible typo: seperate",
        detail: "Check whether `seperate` should be `separate`.",
        evidence: "seperate",
      },
      {
        type: "broken_cross_reference",
        severity: "warning",
        title: "Referenced section 9.1 was not found",
        detail: "The document appears to refer to a section that may not exist.",
        evidence: "Section 9.1",
      },
      {
        type: "missing_standard_section",
        severity: "info",
        title: "Standard section not detected: Limitation of liability",
        detail: "This may be fine, but it is worth checking before signature.",
        evidence: null,
      },
    ],
    disclaimer: "Free preparation check only. This is not legal advice and no contract is saved or stored.",
    nextStep: "For a legal review, submit the contract for an attorney-approved Charter Law redline.",
  };
}

export async function submitPublicIntake(
  request: PublicIntakeRequest,
): Promise<{ response: PublicIntakeResponse; source: PublicApiState }> {
  try {
    const apiResponse = await fetch(`${API_BASE_URL}/public/intake`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!apiResponse.ok) {
      throw new Error(`Public intake failed: ${apiResponse.status}`);
    }

    return {
      response: (await apiResponse.json()) as PublicIntakeResponse,
      source: "api",
    };
  } catch {
    return {
      response: {
        intakeId: `intake_demo_${Date.now()}`,
        status: "demo",
        createdAt: new Date().toISOString(),
        message: "Demo intake captured locally. Connect FastAPI to persist real leads.",
      },
      source: "demo",
    };
  }
}
