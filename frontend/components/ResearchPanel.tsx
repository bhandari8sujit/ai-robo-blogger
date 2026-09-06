import { Claim, ResearchQuestion } from "@/lib/types";

interface ResearchPanelProps {
  claims: Claim[];
  questions: ResearchQuestion[];
  onRunResearch: () => void;
  running: boolean;
}

export function ResearchPanel({ claims, questions, onRunResearch, running }: ResearchPanelProps) {
  const pending = claims.filter((claim) => claim.requiresResearch && claim.researchStatus !== "completed");

  return (
    <section className="panel" aria-label="Research panel">
      <header className="panel-head split">
        <div>
          <p className="eyebrow">Research</p>
          <h2>Evidence queue</h2>
        </div>
        <button className="button button-secondary" type="button" onClick={onRunResearch} disabled={running}>
          {running ? "Researching" : "Run research"}
        </button>
      </header>

      <div className="stats-grid">
        <article className="stat-block">
          <p className="stat-label">Pending claims</p>
          <p className="stat-value">{pending.length}</p>
        </article>
        <article className="stat-block">
          <p className="stat-label">Questions</p>
          <p className="stat-value">{questions.length}</p>
        </article>
      </div>

      <div className="card reveal">
        <h3>Claims requiring evidence</h3>
        <ul>
          {pending.length === 0 ? <li>No pending claims</li> : null}
          {pending.map((claim) => (
            <li key={claim.id}>
              {claim.text} <span className="muted">({Math.round(claim.confidence * 100)}% confidence)</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="card reveal">
        <h3>Research questions</h3>
        <ul>
          {questions.length === 0 ? <li>No active questions</li> : null}
          {questions.map((question) => (
            <li key={question.id}>
              {question.question} <span className="tag">{question.status}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
