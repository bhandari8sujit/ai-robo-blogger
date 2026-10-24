# AI Robo Blogger: Product Intent

## Outcome

Help people capture spontaneous thoughts as audio fragments and turn selected
fragments into elegant, fact-grounded blog drafts.

## User and workflow

The product is for anyone who wants to record thoughts while walking or doing
other activities. Users can:

1. Record and save audio fragments.
2. Have speech transcribed, then review and edit each transcript.
3. Select saved fragments to compose a blog post.
4. Review the generated draft and claim-level fact-check suggestions.
5. Accept or reject suggested corrections, optionally include citations, and
   save the result as a draft to copy or export.

Generated writing should be polished and elegant while preserving the author's
voice, viewpoint, and intended meaning.

## Fact-checking

The backend should identify factual claims and use web search to check them.
Searches may send extracted claims to a search provider, with clear disclosure;
recordings and full drafts must not be sent for those searches. Results should
include evidence and linked sources, with suggested corrections for the user to
accept or reject. Citations should be available as claim-level review and
optionally included in the draft.

## Product boundaries

- First release: responsive desktop web.
- Support separate user accounts; recordings, transcripts, and drafts are
  private to their owner by default.
- Users can delete their content at any time.
- Use a transcription model to convert speech to text. Do not otherwise share
  recordings or content with third parties, except for disclosed searches of
  extracted claims.
- Keep completed posts as in-app drafts and allow copy or export.
- Native mobile apps and direct publishing integrations are outside the first
  release.

## Implementation constraint

The existing `/backend` and `/frontend` were AI-generated and are verbose and
difficult to reason about. Simplify their code only when necessary to implement
a feature; do not create a standalone refactoring effort.

## Success

The generated draft's quality is the primary measure of value: writing should
be elegant and grounded in facts while retaining the author's voice and
viewpoint.

## Scope of this intent

This document records product intent. It does not specify implementation
details, define measurable acceptance thresholds, or authorize feature
implementation.
