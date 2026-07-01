import { MessageSquareText } from "lucide-react";

export function AssistantCard() {
  return (
    <div className="assistant-card">
      <div className="assistant-header">
        <MessageSquareText aria-hidden="true" size={18} />
        <strong>Contract assistant</strong>
        <div className="toggle" aria-label="Assistant mode">
          <span>AI</span>
          <b>Attorney</b>
        </div>
      </div>
      <p>
        Ask for preparation help instantly, or route advice-level questions to
        the reviewing attorney.
      </p>
      <div className="prompt-list">
        <button>Summarize this contract</button>
        <button>What are the key risks?</button>
        <button>Anything unusual?</button>
      </div>
    </div>
  );
}
