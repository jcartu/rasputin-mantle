"use client";

import { useEffect, useState, useRef } from "react";

interface StreamEvent {
  id: string;
  type: string;
  data: any;
  timestamp: string;
}

interface SessionStreamProps {
  sessionId: string;
}

export function SessionStream({ sessionId }: SessionStreamProps) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const scrollRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    let eventSource: EventSource | null = null;
    let retryCount = 0;

    const connect = () => {
      setStatus("connecting");
      eventSource = new EventSource(`/api/sessions/${sessionId}/stream`);

      eventSource.onopen = () => {
        setStatus("connected");
        retryCount = 0;
      };

      eventSource.onmessage = (e) => {
        try {
          const parsed = JSON.parse(e.data);
          setEvents((prev) => [...prev, parsed]);
        } catch (err) {
          console.error("Failed to parse SSE message", err);
        }
      };

      eventSource.onerror = () => {
        setStatus("disconnected");
        eventSource?.close();
        
        // Exponential backoff for reconnect
        const timeout = Math.min(1000 * Math.pow(2, retryCount), 30000);
        retryCount++;
        
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, timeout);
      };
    };

    connect();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="flex flex-col h-full bg-zinc-950 border-t border-zinc-800">
      <div className="px-4 py-2 border-b border-zinc-800 flex items-center justify-between text-xs text-zinc-500">
        <span>Event Stream</span>
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              status === "connected"
                ? "bg-green-500"
                : status === "connecting"
                ? "bg-yellow-500"
                : "bg-red-500"
            }`}
          />
          <span className="capitalize">{status}</span>
        </div>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-sm">
        {events.map((event, i) => (
          <div key={i} className="p-2 rounded bg-zinc-900 border border-zinc-800 text-zinc-300">
            <div className="flex justify-between text-xs text-zinc-500 mb-1">
              <span>{event.type}</span>
              <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
            </div>
            <pre className="whitespace-pre-wrap break-words">
              {JSON.stringify(event.data, null, 2)}
            </pre>
          </div>
        ))}
        {events.length === 0 && status === "connected" && (
          <div className="text-zinc-600 text-center py-4">Waiting for events...</div>
        )}
      </div>
    </div>
  );
}
