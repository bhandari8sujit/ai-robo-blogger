import {
  BlogState,
  Draft,
  Fragment,
  ResearchQuestion,
  SentenceWhy,
  Source,
} from "@/lib/types";
import { getApiBaseUrl } from "@/lib/runtime";

const API_BASE_URL = getApiBaseUrl();

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function getBlogState(blogId: string): Promise<BlogState> {
  return request<BlogState>(`/blogs/${blogId}/state`);
}

export async function getFragments(blogId: string): Promise<Fragment[]> {
  return request<Fragment[]>(`/blogs/${blogId}/fragments`);
}

export async function getResearch(blogId: string): Promise<ResearchQuestion[]> {
  return request<ResearchQuestion[]>(`/blogs/${blogId}/research`);
}

export async function generateDraft(blogId: string): Promise<Draft> {
  return request<Draft>(`/blogs/${blogId}/draft/generate`, {
    method: "POST",
  });
}

export async function reviseDraft(draftId: string, revisionPrompt: string): Promise<Draft> {
  return request<Draft>(`/drafts/${draftId}/revise`, {
    method: "POST",
    body: JSON.stringify({ revisionPrompt }),
  });
}

export async function getSources(draftId: string): Promise<Source[]> {
  return request<Source[]>(`/drafts/${draftId}/sources`);
}

export async function getSentenceWhy(draftId: string, sentenceId: string): Promise<SentenceWhy> {
  return request<SentenceWhy>(`/drafts/${draftId}/sentences/${sentenceId}/why`);
}

export async function uploadFragment(blogId: string, file: Blob): Promise<Fragment> {
  const form = new FormData();
  form.append("audio", file, `fragment-${Date.now()}.webm`);

  const response = await fetch(`${API_BASE_URL}/blogs/${blogId}/fragments`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Upload failed with ${response.status}`);
  }

  return (await response.json()) as Fragment;
}
