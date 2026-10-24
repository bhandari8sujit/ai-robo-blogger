# 09: Transcribe with provider disclosure

Type: task
Blocked by: 08

## Source requirements

- [PRD](../spec.md)
- [Transcripts module](../SPEC-transcripts.md)

## Description

Transcribe saved fragments as a distinct processing stage, expose its status and
errors, and disclose the transcription provider and audio transfer before
third-party processing. Resolve whether notice or explicit opt-in is required
before implementing the disclosure gate.

## Acceptance criteria

- A saved fragment can be transcribed without running analysis, research, or
  draft composition.
- Transcription success, failure, and missing configuration are distinct,
  visible states.
- The user sees the provider, audio data sent, and purpose before transcription
  begins; no audio is sent if the required disclosure gate is not satisfied.

## Verification

- Provider-fake tests assert transcription receives only the fragment audio and
  failure states are not represented as success.
- Manually verify disclosure, transcription, and failure states in the UI.
- Run `python -m pytest` from `backend/` and `npm run typecheck` from `frontend/`.

## Dependencies

Blocked by: 08

## Files likely touched

- `backend/app/api/fragments.py`
- `backend/app/services/orchestration_service.py`
- `backend/tests/test_transcription.py`
- `frontend/components/VoiceCapturePanel.tsx`
- `frontend/lib/apiSlice.ts`

## Estimated scope

Medium (5 files).

## Comments
