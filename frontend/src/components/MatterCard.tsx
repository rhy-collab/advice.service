import { Check, FileText } from "lucide-react";
import { Matter, stages } from "../lib/demoData";

export function MatterCard({ matter }: { matter: Matter }) {
  return (
    <div className="matter-card">
      <div className="file-row">
        <span className="file-icon">
          <FileText aria-hidden="true" size={24} />
        </span>
        <div>
          <strong>{matter.file}</strong>
          <span>{matter.type}</span>
        </div>
      </div>
      <div className="stage-track">
        {stages.map((stage, index) => (
          <div className={`stage ${index <= matter.activeStage ? "complete" : ""}`} key={stage}>
            <span>{index <= matter.activeStage ? <Check size={14} /> : index + 1}</span>
            <p>{stage}</p>
          </div>
        ))}
      </div>
      <p className="eta">
        {matter.status === "Delivered"
          ? "Final Word redline is ready to download."
          : `Current step: ${matter.status}. Estimated next update: ${matter.eta}.`}
      </p>
    </div>
  );
}
