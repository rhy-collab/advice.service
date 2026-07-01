import { CircleDollarSign, Scale, ShieldCheck } from "lucide-react";

export const stages = ["Received", "AI Review", "Attorney Review", "Delivered"] as const;

export type Matter = {
  id: string;
  file: string;
  type: string;
  status: string;
  uploadStatus: string;
  paymentStatus: string;
  submitted: string;
  eta: string;
  activeStage: number;
  deliverableAvailable: boolean;
};

export const matters: Matter[] = [
  {
    id: "matter_demo_1",
    file: "vendor-saas-agreement.docx",
    type: "Standard redline",
    status: "Attorney Review",
    uploadStatus: "Uploaded",
    paymentStatus: "Checkout pending",
    submitted: "Today",
    eta: "42 minutes",
    activeStage: 2,
    deliverableAvailable: false,
  },
  {
    id: "matter_demo_2",
    file: "mutual-nda-series-a.docx",
    type: "Simple review",
    status: "AI Review",
    uploadStatus: "Uploaded",
    paymentStatus: "Checkout pending",
    submitted: "Yesterday",
    eta: "2 hours",
    activeStage: 1,
    deliverableAvailable: false,
  },
  {
    id: "matter_demo_3",
    file: "customer-msa-clean.docx",
    type: "Delivered",
    status: "Delivered",
    uploadStatus: "Uploaded",
    paymentStatus: "Paid",
    submitted: "Jun 28",
    eta: "Complete",
    activeStage: 3,
    deliverableAvailable: true,
  },
];

export const proofPoints = [
  {
    title: "Flat fees",
    text: "Know the price before review begins, with clear tiers for routine startup contracts.",
    icon: CircleDollarSign,
  },
  {
    title: "Attorney approval",
    text: "AI prepares the first pass; a reviewing attorney approves the redline before delivery.",
    icon: Scale,
  },
  {
    title: "Predictable status",
    text: "Track each matter from upload through attorney review and final Word delivery.",
    icon: ShieldCheck,
  },
];

export const pricing = [
  ["Simple review", "$250", "A focused issue spot for short, low-complexity agreements."],
  ["Standard redline", "$500", "A Word redline, risk notes, and practical fallback positions."],
  ["Full negotiation", "$1,000+", "Attorney-led negotiation support for higher-stakes matters."],
] as const;
