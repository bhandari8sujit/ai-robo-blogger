# Frontend Agent: Voice Capture UI Agent

## Purpose
Coordinate browser-side voice recording UX and fragment lifecycle from local capture to backend upload.

## Stack
- Next.js + TypeScript
- MediaRecorder API
- Web Audio API
- React Query mutation hooks

## Responsibilities
- Start/stop/preview short recordings.
- Validate fragment length and mime type.
- Upload fragment and metadata to backend.
- Emit UI state transitions and retry actions.

## Inputs
- `blog_id`
- User recording events (`start`, `stop`, `cancel`)
- Optional local transcript notes

## Outputs
- `fragment_created` event in UI store
- Upload status (`pending`, `uploaded`, `failed`)
- Fragment duration and local waveform metadata

## API Contract
- `POST /blogs/{blog_id}/fragments` (multipart)

## State Machine
1. `idle`
2. `recording`
3. `encoding`
4. `uploading`
5. `uploaded` or `error`

## Failure Handling
- Permission denied -> show microphone permission guide.
- Upload timeout -> exponential retry and manual retry CTA.
- Unsupported codec -> fallback mime type negotiation.

## Telemetry (Internal App Events)
- `capture_started`
- `capture_completed`
- `upload_succeeded`
- `upload_failed`

## Notes
- Keep fragments independent; never merge in client before upload.
- Preserve original recording quality for downstream re-transcription.
