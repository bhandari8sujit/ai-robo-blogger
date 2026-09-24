"use client";

import { useMemo, useState } from "react";

import { useGetSentenceWhyQuery, useGetSourcesQuery, useReviseDraftMutation } from "@/lib/apiSlice";
import { Draft } from "@/lib/types";

interface DraftWorkspaceProps {
  draft: Draft | null;
  onRegenerateDraft: () => void;
}

export function DraftWorkspace({ draft, onRegenerateDraft }: DraftWorkspaceProps) {
  const [revisionPrompt, setRevisionPrompt] = useState("");
  const [sentenceId, setSentenceId] = useState("");

  const sourcesQuery = useGetSourcesQuery(draft?.id ?? "", { skip: !draft?.id });

  const [reviseDraft, reviseMutation] = useReviseDraftMutation();

  const whyQuery = useGetSentenceWhyQuery(
    { draftId: draft?.id ?? "", sentenceId },
    { skip: !(draft?.id && sentenceId) },
  );

  const preview = useMemo(() => {
    if (!draft?.content) {
      return "No draft generated yet. Add a fragment and generate a draft.";
    }
    return draft.content;
  }, [draft]);

  return (
    <section className="panel" aria-label="Draft workspace panel">
      <header className="panel-head split">
        <div>
          <p className="eyebrow">Draft workspace</p>
          <h2>Shape your article</h2>
        </div>
        <div className="actions">
          <button className="button button-secondary" type="button" onClick={onRegenerateDraft}>
            Regenerate
          </button>
          <button className="button button-primary" type="button">
            Publish
          </button>
        </div>
      </header>

      <article className="draft-sheet reveal">
        <p className="muted">{draft ? `Draft v${draft.version} • ${draft.wordCount} words` : "No version yet"}</p>
        <p>{preview}</p>
      </article>

      <div className="workspace-grid">
        <div className="card reveal">
          <h3>Request a revision</h3>
          <label htmlFor="revisionPrompt" className="field-label">
            What should change?
          </label>
          <textarea
            id="revisionPrompt"
            className="field"
            value={revisionPrompt}
            onChange={(event) => setRevisionPrompt(event.target.value)}
            placeholder="Example: Keep my skeptical tone in paragraph 2 and shorten the conclusion."
          />
          <button
            className="button button-secondary"
            type="button"
            disabled={!draft || !revisionPrompt.trim() || reviseMutation.isLoading}
            onClick={() => {
              void reviseDraft({ draftId: draft!.id, revisionPrompt })
                .unwrap()
                .then(() => setRevisionPrompt(""));
            }}
          >
            {reviseMutation.isLoading ? "Revising" : "Apply revision"}
          </button>
        </div>

        <div className="card reveal">
          <h3>Why is this here?</h3>
          <label htmlFor="sentenceId" className="field-label">
            Sentence id
          </label>
          <input
            id="sentenceId"
            className="field"
            value={sentenceId}
            onChange={(event) => setSentenceId(event.target.value)}
            placeholder="s_17"
          />
          {whyQuery.data ? (
            <div className="explain-box">
              <p>{whyQuery.data.aiInterpretation}</p>
              <p className="muted">Confidence {Math.round(whyQuery.data.confidence * 100)}%</p>
            </div>
          ) : (
            <p className="muted">Enter a sentence id to inspect provenance.</p>
          )}
        </div>
      </div>

      <div className="card reveal">
        <h3>Sources</h3>
        <ul>
          {!sourcesQuery.data?.length ? <li>No linked sources yet.</li> : null}
          {sourcesQuery.data?.map((source) => (
            <li key={source.id}>
              <a href={source.url} target="_blank" rel="noreferrer">
                {source.title}
              </a>{" "}
              <span className="muted">({Math.round(source.credibility * 100)} credibility)</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
