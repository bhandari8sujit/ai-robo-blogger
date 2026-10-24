# Module Spec: Transcripts

- **Module id:** `transcripts`
- **Depends on:** `audio-fragments`
- **Parent PRD:** [spec.md](spec.md)

## Objective

Convert saved speech into editable text that users can correct before
composition.

## Requirements

- Transcribe each fragment using a speech-to-text model.
- Disclose the transcription provider, data sent (audio), and purpose before
  third-party processing.
- Persist explicit processing states and surface provider/configuration errors.
- Allow the owner to review and edit the transcript.
- Use the saved edited transcript for composition; preserve the source audio
  independently.
- Deleting the fragment removes the transcript and related app-controlled
  derivatives.

## Acceptance criteria

- A successful transcription is linked to its source fragment and owner.
- Failed or unavailable transcription is visibly distinct from an empty
  successful transcript.
- An edit persists across reload and is used in subsequent composition.
- Non-owners cannot read or edit a transcript.

## Verification

Service tests use a transcription provider fake; API and UI tests cover
successful, failed, and edited transcript paths and provider payload boundaries.

## Open questions

- Which transcription languages and supported audio limits are required?
- What provider retention terms are acceptable?
