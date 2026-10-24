# Module Spec: Draft Review and Export

- **Module id:** `draft-review-export`
- **Depends on:** `composition`, `claim-verification`
- **Parent PRD:** [spec.md](spec.md)

## Objective

Give authors control over fact-check suggestions and the final saved/exported
draft.

## Requirements

- Display the composed draft alongside claim-level evidence and correction
  suggestions.
- Let the author accept or reject each suggestion; only acceptance changes the
  draft, and only the corresponding claim text is affected.
- Let the author include or omit citations in the draft.
- Save and reopen an editable, user-owned draft.
- Provide copy and export actions.
- Do not provide direct publish-to-platform behavior in v1.

## Acceptance criteria

- Rejecting a suggestion leaves draft content unchanged.
- Accepting a suggestion changes the relevant text and preserves review state.
- Citations appear only when selected and correspond to stored source evidence.
- Saved changes survive reload; other users cannot access the draft.
- Copy/export produces the current reviewed content, not a stale generation.

## Verification

Frontend interaction tests cover review outcomes, citation selection, save,
reopen, copy, export, and ownership failures.

## Open questions

- Which export format(s) are required?
- Should revisions preserve a full user-visible version history?
