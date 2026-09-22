import {
  AuthToken,
  AuthUser,
  BlogState,
  Draft,
  Fragment,
  ResearchQuestion,
  SentenceWhy,
  Source,
} from "@/lib/types";
import { getApiBaseUrl } from "@/lib/runtime";

const API_BASE_URL = getApiBaseUrl();
const AUTH_TOKEN_KEY = "robo-blog-access-token";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export function getAuthToken(): string | null {
  return typeof window === "undefined" ? null : window.sessionStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  window.sessionStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  window.sessionStorage.removeItem(AUTH_TOKEN_KEY);
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const isFormData = options?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(!isFormData ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, text || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function register(email: string, password: string): Promise<AuthUser> {
  return request<AuthUser>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email: string, password: string): Promise<AuthToken> {
  const form = new URLSearchParams({ username: email, password });
  return request<AuthToken>("/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });
}

export async function getCurrentUser(): Promise<AuthUser> {
  return request<AuthUser>("/auth/me");
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

  return request<Fragment>(`/blogs/${blogId}/fragments`, {
    method: "POST",
    body: form,
  });
}

export async function runResearch(blogId: string): Promise<{ completed: number }> {
  return request<{ completed: number }>(`/blogs/${blogId}/research/run`, { method: "POST" });
}
