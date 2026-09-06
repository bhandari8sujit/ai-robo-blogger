"use client";

import { useMemo, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { uploadFragment } from "@/lib/api";

interface VoiceCapturePanelProps {
  blogId: string;
  onFragmentUploaded: () => void;
}

type RecorderState = "idle" | "recording" | "encoding" | "uploading" | "uploaded" | "error";

export function VoiceCapturePanel({ blogId, onFragmentUploaded }: VoiceCapturePanelProps) {
  const [recorderState, setRecorderState] = useState<RecorderState>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [seconds, setSeconds] = useState(0);
  const [level, setLevel] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const startTimeRef = useRef<number>(0);
  const intervalRef = useRef<number | null>(null);
  const animationRef = useRef<number | null>(null);
  const contextRef = useRef<AudioContext | null>(null);

  const uploadMutation = useMutation({
    mutationFn: async (blob: Blob) => uploadFragment(blogId, blob),
    onMutate: () => {
      setRecorderState("uploading");
    },
    onSuccess: () => {
      setRecorderState("uploaded");
      onFragmentUploaded();
    },
    onError: (error) => {
      setRecorderState("error");
      setErrorMessage(error instanceof Error ? error.message : "Upload failed. Try again.");
    },
  });

  const levelStyle = useMemo(
    () => ({
      width: `${Math.max(6, Math.round(level * 100))}%`,
    }),
    [level],
  );

  async function startRecording() {
    setErrorMessage("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];
      mediaRecorderRef.current = mediaRecorder;
      startTimeRef.current = Date.now();
      setRecorderState("recording");

      const audioContext = new AudioContext();
      contextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);

      const updateLevel = () => {
        analyser.getByteFrequencyData(data);
        const avg = data.reduce((sum, n) => sum + n, 0) / data.length;
        setLevel(avg / 255);
        animationRef.current = requestAnimationFrame(updateLevel);
      };
      animationRef.current = requestAnimationFrame(updateLevel);

      intervalRef.current = window.setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setSeconds(elapsed);
      }, 250);

      mediaRecorder.ondataavailable = (event) => {
        chunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        setRecorderState("encoding");
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current);
          animationRef.current = null;
        }
        if (contextRef.current) {
          void contextRef.current.close();
          contextRef.current = null;
        }

        const duration = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setSeconds(duration);

        const blob = new Blob(chunksRef.current, { type: mimeType });

        if (duration < 2 || blob.size < 1024) {
          setRecorderState("error");
          setErrorMessage("Recording is too short. Record at least 2 seconds.");
          return;
        }

        uploadMutation.mutate(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
    } catch {
      setRecorderState("error");
      setErrorMessage("Microphone access is blocked. Enable it and try again.");
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }

  function resetPanel() {
    setRecorderState("idle");
    setSeconds(0);
    setLevel(0);
    setErrorMessage("");
  }

  return (
    <section className="panel voice-panel" aria-label="Voice capture panel">
      <header className="panel-head">
        <p className="eyebrow">Voice capture</p>
        <h2>Talk in fragments</h2>
      </header>

      <p className="panel-copy">
        Speak one idea at a time. The system updates your thesis and draft after each fragment.
      </p>

      <div className="meter" aria-hidden>
        <span className="meter-level" style={levelStyle} />
      </div>

      <p className="muted" aria-live="polite">
        {recorderState === "recording" ? `Recording ${seconds}s` : `Last fragment length ${seconds}s`}
      </p>

      <div className="actions">
        {recorderState !== "recording" ? (
          <button className="button button-primary" type="button" onClick={startRecording}>
            Start recording
          </button>
        ) : (
          <button className="button button-danger" type="button" onClick={stopRecording}>
            Stop recording
          </button>
        )}

        <button className="button button-secondary" type="button" onClick={resetPanel}>
          Reset
        </button>
      </div>

      {errorMessage ? <p className="error-text">{errorMessage}</p> : null}
    </section>
  );
}
