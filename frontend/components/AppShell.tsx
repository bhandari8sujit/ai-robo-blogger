"use client";

import { BlogBrainPanel } from "@/components/BlogBrainPanel";
import { DraftWorkspace } from "@/components/DraftWorkspace";
import { ResearchPanel } from "@/components/ResearchPanel";
import { VoiceCapturePanel } from "@/components/VoiceCapturePanel";
import { useGenerateDraftMutation, useGetBlogStateQuery, useGetResearchQuery, useRunResearchMutation } from "@/lib/apiSlice";

const BLOG_ID = "demo-blog";

interface AppShellProps {
  email: string;
  onLogout: () => void;
}

export function AppShell({ email, onLogout }: AppShellProps) {
  const stateQuery = useGetBlogStateQuery(BLOG_ID, { pollingInterval: 30_000 });
  const researchQuery = useGetResearchQuery(BLOG_ID, { pollingInterval: 30_000 });

  const [generateDraft, draftMutation] = useGenerateDraftMutation();
  const [runResearch, researchMutation] = useRunResearchMutation();

  // const stream = useEventStream(BLOG_ID, {
  //   enabled: true,
  //   onMessage: () => {
  //     void stateQuery.refetch();
  //     void researchQuery.refetch();
  //   },
  // });

  const state = stateQuery.data;

  return (
    <main className="app-shell">
      <section className="hero reveal">
        <div className="session-bar">
          <span>{email}</span>
          <button className="button session-button" type="button" onClick={onLogout}>
            Sign out
          </button>
        </div>
        <p className="eyebrow">Voice-first writing studio</p>
        <h1>Talk to your blog while the system builds evidence and structure.</h1>
        <p>
          Designed for thinkers who speak in fragments. Record one idea, let the agent synthesize it, then steer the
          next revision.
        </p>
      </section>

      <section className="layout-grid">
        <VoiceCapturePanel blogId={BLOG_ID} />

        <ResearchPanel
          claims={state?.claims ?? []}
          questions={researchQuery.data ?? []}
          running={researchMutation.isLoading}
          onRunResearch={() => void runResearch(BLOG_ID)}
        />

        <DraftWorkspace draft={draftMutation.data ?? null} onRegenerateDraft={() => void generateDraft(BLOG_ID)} />
      </section>
    </main>
  );
}
