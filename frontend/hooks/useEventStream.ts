"use client";

import { useEffect, useRef, useState } from "react";

import { getApiBaseUrl } from "@/lib/runtime";
import { EventMessage } from "@/lib/types";

interface UseEventStreamOptions {
  enabled?: boolean;
  onMessage?: (event: EventMessage) => void;
}

interface EventStreamState {
  connected: boolean;
  stale: boolean;
  lastEventAt?: string;
}

const STALE_MS = 30_000;

export function useEventStream(blogId: string, options?: UseEventStreamOptions): EventStreamState {
  const [connected, setConnected] = useState(false);
  const [lastEventAt, setLastEventAt] = useState<string | undefined>(undefined);
  const lastEventRef = useRef<number>(Date.now());

  useEffect(() => {
    if (!options?.enabled) {
      return;
    }

    const baseUrl = getApiBaseUrl();
    const source = new EventSource(`${baseUrl}/blogs/${blogId}/events`);

    source.onopen = () => {
      setConnected(true);
    };

    source.onmessage = (rawEvent) => {
      try {
        const parsed = JSON.parse(rawEvent.data) as EventMessage;
        lastEventRef.current = Date.now();
        setLastEventAt(parsed.createdAt);
        options.onMessage?.(parsed);
      } catch {
        // Ignore malformed event payloads and keep stream alive.
      }
    };

    source.onerror = () => {
      setConnected(false);
      source.close();
    };

    return () => {
      source.close();
      setConnected(false);
    };
  }, [blogId, options]);

  const stale = Date.now() - lastEventRef.current > STALE_MS;

  return {
    connected,
    stale,
    lastEventAt,
  };
}
