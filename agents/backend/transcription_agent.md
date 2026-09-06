# Backend Agent: Transcription Agent

## Purpose
Convert uploaded audio fragments into reliable low-cost text transcripts.

## Provider
- GPT-4o Mini Transcribe (default)

## Responsibilities
- Fetch audio from R2/S3 URL.
- Submit to STT provider.
- Store transcript and confidence metadata.
- Preserve raw audio pointer for future re-runs.

## Inputs
- `fragment_id`
- `audio_url`
- Optional language hint

## Outputs
- `transcript`
- `transcript_confidence`
- `transcription_model`
- `transcribed_at`

## Guardrails
- Reject too-short/no-audio fragments with explicit status.
- Mark low-confidence transcripts for optional user review.

## Failure Handling
- Provider timeout -> retry with backoff.
- Corrupt audio -> set `transcription_failed` and attach reason.

## Notes
- Do not mutate original audio file.
- Transcript corrections should create new version records.
