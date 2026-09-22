"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { BlogBrainPanel } from "@/components/BlogBrainPanel";
import { DraftWorkspace } from "@/components/DraftWorkspace";
import { ResearchPanel } from "@/components/ResearchPanel";
import { VoiceCapturePanel } from "@/components/VoiceCapturePanel";
import { generateDraft, getBlogState, getResearch, runResearch } from "@/lib/api";

const BLOG_ID = "demo-blog";

interface AppShellProps {
  email: string;
  onLogout: () => void;
}

export function AppShell({ email, onLogout }: AppShellProps) {
  const queryClient = useQueryClient();
  const [draftVersion, setDraftVersion] = useState(0);

  const stateQuery = useQuery({
    queryKey: ["blog-state", BLOG_ID],
    queryFn: () => getBlogState(BLOG_ID),
    retry: 1,
    refetchInterval: 30_000,
  });

  const researchQuery = useQuery({
    queryKey: ["research", BLOG_ID],
    queryFn: () => getResearch(BLOG_ID),
    retry: 1,
    refetchInterval: 30_000,
  });

  const draftMutation = useMutation({
    mutationFn: () => generateDraft(BLOG_ID),
    onSuccess: () => {
      setDraftVersion((version) => version + 1);
    },
  });

  const researchMutation = useMutation({
    mutationFn: () => runResearch(BLOG_ID),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["research", BLOG_ID] });
      void queryClient.invalidateQueries({ queryKey: ["blog-state", BLOG_ID] });
    },
  });

  // const stream = useEventStream(BLOG_ID, {
  //   enabled: true,
  //   onMessage: () => {
  //     void queryClient.invalidateQueries({ queryKey: ["blog-state", BLOG_ID] });
  //     void queryClient.invalidateQueries({ queryKey: ["research", BLOG_ID] });
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
        <VoiceCapturePanel
          blogId={BLOG_ID}
          onFragmentUploaded={() => {
            void queryClient.invalidateQueries({ queryKey: ["blog-state", BLOG_ID] });
          }}
        />

        <ResearchPanel
          claims={state?.claims ?? []}
          questions={researchQuery.data ?? []}
          running={researchMutation.isPending}
          onRunResearch={() => researchMutation.mutate()}
        />

        <DraftWorkspace draft={draftMutation.data ?? null} onRegenerateDraft={() => draftMutation.mutate()} />
      </section>
    </main>
  );
}
