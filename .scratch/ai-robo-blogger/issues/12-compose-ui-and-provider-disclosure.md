# 12: Compose UI and provider disclosure

Type: task
Blocked by: 11

## Source requirements

- [PRD](../spec.md)
- [Composition module](../SPEC-composition.md)

## Description

Connect the fragment library to the composition operation. Let users choose and
order fragments, then disclose which composition provider receives the selected
transcripts and why before sending them.

## Acceptance criteria

- Users can select, deselect, and order their own transcribed fragments.
- The UI clearly identifies selected text, provider, and composition purpose
  before third-party composition.
- The generated draft view uses the returned draft and displays actionable
  errors without losing the selection.

## Verification

- Manually verify selection order, disclosure, successful generation, provider
  failure, and responsive layout.
- Run `npm run typecheck` and `npm run build` from `frontend/`.

## Dependencies

Blocked by: 11

## Files likely touched

- `frontend/components/FragmentLibrary.tsx`
- `frontend/components/DraftWorkspace.tsx`
- `frontend/lib/apiSlice.ts`

## Estimated scope

Small (3 files).

## Comments
