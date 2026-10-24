# Module Spec: Composition

- **Module id:** `composition`
- **Depends on:** `transcripts`
- **Parent PRD:** [spec.md](spec.md)

## Objective

Compose user-selected transcript fragments into an elegant draft that remains
faithful to the author's voice, viewpoint, and meaning.

## Requirements

- Let a user select multiple owned, transcribed fragments in a visible order.
- Compose from only the selected, user-edited transcript text and necessary
  instructions/context.
- A third-party composition model is permitted only with clear disclosure of
  provider, content sent, and purpose before processing.
- Produce coherent, polished prose without inventing personal experience,
  viewpoint, or unsupported claims.
- Persist the generated result as a user-owned draft, preserving prior versions
  where applicable.
- Do not publish directly to an external blogging service in v1.

## Acceptance criteria

- Selection order and exact fragment set are reflected in the composition
  request.
- Unselected fragments and unrelated user content are not sent to the
  composition provider.
- Provider failures are visible and do not create success-shaped drafts.
- The draft is editable and persists for its owner.

## Verification

Provider-fake tests assert exact composition inputs and failure handling.
Product review evaluates representative drafts for elegance, factual grounding,
and preservation of voice/viewpoint.

## Open questions

- Is disclosure notice sufficient, or must users explicitly opt in?
- What evaluation rubric and quality threshold should be used?
