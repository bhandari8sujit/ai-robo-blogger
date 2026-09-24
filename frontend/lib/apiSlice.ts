import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import { getAuthToken } from "@/lib/api";
import { getApiBaseUrl } from "@/lib/runtime";
import { BlogState, Draft, Fragment, ResearchQuestion, SentenceWhy, Source } from "@/lib/types";

export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: getApiBaseUrl(),
    prepareHeaders: (headers) => {
      const token = getAuthToken();
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ["BlogState", "Research", "Sources"],
  endpoints: (builder) => ({
    getBlogState: builder.query<BlogState, string>({
      query: (blogId) => `/blogs/${blogId}/state`,
      providesTags: (_result, _error, blogId) => [{ type: "BlogState", id: blogId }],
    }),
    getResearch: builder.query<ResearchQuestion[], string>({
      query: (blogId) => `/blogs/${blogId}/research`,
      providesTags: (_result, _error, blogId) => [{ type: "Research", id: blogId }],
    }),
    getSources: builder.query<Source[], string>({
      query: (draftId) => `/drafts/${draftId}/sources`,
      providesTags: (_result, _error, draftId) => [{ type: "Sources", id: draftId }],
    }),
    getSentenceWhy: builder.query<SentenceWhy, { draftId: string; sentenceId: string }>({
      query: ({ draftId, sentenceId }) => `/drafts/${draftId}/sentences/${sentenceId}/why`,
    }),
    generateDraft: builder.mutation<Draft, string>({
      query: (blogId) => ({ url: `/blogs/${blogId}/draft/generate`, method: "POST" }),
    }),
    reviseDraft: builder.mutation<Draft, { draftId: string; revisionPrompt: string }>({
      query: ({ draftId, revisionPrompt }) => ({
        url: `/drafts/${draftId}/revise`,
        method: "POST",
        body: { revisionPrompt },
      }),
    }),
    runResearch: builder.mutation<{ completed: number }, string>({
      query: (blogId) => ({ url: `/blogs/${blogId}/research/run`, method: "POST" }),
      invalidatesTags: (_result, _error, blogId) => [
        { type: "Research", id: blogId },
        { type: "BlogState", id: blogId },
      ],
    }),
    uploadFragment: builder.mutation<Fragment, { blogId: string; file: Blob }>({
      query: ({ blogId, file }) => {
        const form = new FormData();
        form.append("audio", file, `fragment-${Date.now()}.webm`);
        return { url: `/blogs/${blogId}/fragments`, method: "POST", body: form };
      },
      invalidatesTags: (_result, _error, { blogId }) => [{ type: "BlogState", id: blogId }],
    }),
  }),
});

export const {
  useGetBlogStateQuery,
  useGetResearchQuery,
  useGetSourcesQuery,
  useGetSentenceWhyQuery,
  useGenerateDraftMutation,
  useReviseDraftMutation,
  useRunResearchMutation,
  useUploadFragmentMutation,
} = api;
