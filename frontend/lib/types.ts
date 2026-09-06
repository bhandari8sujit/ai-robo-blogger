export type OriginType = "USER_SAID" | "AI_INFERENCE" | "RESEARCH_FACT" | "AI_GENERATED";

export type ProcessingStatus =
  | "uploaded"
  | "transcribed"
  | "analyzed"
  | "researched"
  | "drafted"
  | "validated"
  | "failed";

export interface Fragment {
  id: string;
  blogId: string;
  createdAt: string;
  durationSeconds: number;
  transcript?: string;
  status: ProcessingStatus;
}

export interface Claim {
  id: string;
  text: string;
  requiresResearch: boolean;
  confidence: number;
  originType: OriginType;
  researchStatus: "pending" | "completed" | "insufficient";
}

export interface BlogBrainCard<T> {
  value: T;
  confidence: number;
  originType: OriginType;
  updatedAt: string;
}

export interface BlogState {
  blogId: string;
  title: string;
  thesis: BlogBrainCard<string>;
  arguments: BlogBrainCard<string[]>;
  sentiment: BlogBrainCard<{
    primary: string;
    secondary?: string;
    intensity: number;
  }>;
  intent: BlogBrainCard<string>;
  openQuestions: BlogBrainCard<string[]>;
  claims: Claim[];
  contradictionCount: number;
  processingStatus: ProcessingStatus;
}

export interface ResearchQuestion {
  id: string;
  question: string;
  status: "pending" | "completed" | "insufficient";
  priority: "low" | "medium" | "high";
  sourceCount: number;
}

export interface Source {
  id: string;
  title: string;
  url: string;
  publisher?: string;
  publishedAt?: string;
  credibility: number;
}

export interface Draft {
  id: string;
  blogId: string;
  version: number;
  content: string;
  wordCount: number;
  updatedAt: string;
}

export interface SentenceWhy {
  sentenceId: string;
  sentenceText: string;
  userBasis: string[];
  aiInterpretation: string;
  sourceEvidence: Array<{
    sourceTitle: string;
    sourceUrl: string;
    supportText: string;
  }>;
  confidence: number;
}

export interface EventMessage {
  type: "fragment_processed" | "research_completed" | "draft_updated" | "state_refreshed" | "error";
  blogId: string;
  payload: Record<string, unknown>;
  createdAt: string;
}
