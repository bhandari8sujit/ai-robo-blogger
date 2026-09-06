import { BlogState } from "@/lib/types";

interface BlogBrainPanelProps {
  state: BlogState;
  stale: boolean;
}

function ProvenanceTag({ origin }: { origin: string }) {
  return <span className="tag">{origin.toLowerCase().replace("_", " ")}</span>;
}

export function BlogBrainPanel({ state, stale }: BlogBrainPanelProps) {
  return (
    <section className="panel" aria-label="Blog brain panel">
      <header className="panel-head split">
        <div>
          <p className="eyebrow">Blog brain</p>
          <h2>Current understanding</h2>
        </div>
        {stale ? <span className="badge-warn">Refreshing data</span> : <span className="badge-ok">Live</span>}
      </header>

      <article className="card reveal">
        <div className="card-head">
          <h3>Thesis</h3>
          <ProvenanceTag origin={state.thesis.originType} />
        </div>
        <p>{state.thesis.value}</p>
      </article>

      <article className="card reveal">
        <div className="card-head">
          <h3>Arguments</h3>
          <ProvenanceTag origin={state.arguments.originType} />
        </div>
        <ul>
          {state.arguments.value.map((argument) => (
            <li key={argument}>{argument}</li>
          ))}
        </ul>
      </article>

      <article className="card reveal">
        <div className="card-head">
          <h3>Sentiment and intent</h3>
          <ProvenanceTag origin={state.sentiment.originType} />
        </div>
        <p>
          {state.sentiment.value.primary}
          {state.sentiment.value.secondary ? `, ${state.sentiment.value.secondary}` : ""}
          {` (${Math.round(state.sentiment.value.intensity * 100)}%)`}
        </p>
        <p className="muted">Intent: {state.intent.value}</p>
      </article>

      <article className="card reveal">
        <div className="card-head">
          <h3>Open questions</h3>
          <ProvenanceTag origin={state.openQuestions.originType} />
        </div>
        <ul>
          {state.openQuestions.value.map((question) => (
            <li key={question}>{question}</li>
          ))}
        </ul>
      </article>

      {state.contradictionCount > 0 ? (
        <p className="warn-text">
          {state.contradictionCount} contradiction{state.contradictionCount > 1 ? "s" : ""} found. Review before publish.
        </p>
      ) : null}
    </section>
  );
}
