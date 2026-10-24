# Module Spec: Audio Fragments

- **Module id:** `audio-fragments`
- **Depends on:** `identity-privacy`
- **Parent PRD:** [spec.md](spec.md)

## Objective

Let users capture spontaneous thoughts as separate, saved audio fragments on
responsive desktop web.

## Requirements

- Record and upload supported audio in a secure browser context with microphone
  permission.
- Save each recording as an independent fragment associated with its owner.
- List a user's fragments with useful creation and processing status.
- Validate empty payloads, media type, size, and duration against agreed limits.
- Allow owners to delete fragments and their app-controlled audio objects.
- Native apps, offline/background recording, and direct publication are outside
  this module's v1 scope.

## Acceptance criteria

- A user can record, stop, save, and find a fragment in their own list.
- Invalid or over-limit uploads fail with an actionable error and are not
  treated as saved fragments.
- Other accounts cannot list, retrieve, process, or delete the fragment.
- Deletion removes the audio object and its fragment record or clearly reports
  cleanup failure.

## Verification

Backend upload/list/delete and ownership tests; frontend browser checks for
permission, recording, upload, processing, and error states.

## Open questions

- Which media formats, maximum duration/size, and browser matrix are required?
- Is local buffering/retry required for v1?
