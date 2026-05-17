"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

interface Session {
  id: string;
  created_at: string;
}

export function Sidebar() {
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/sessions")
      .then((res) => {
        if (res.ok) return res.json();
        return [];
      })
      .then((data) => setSessions(data))
      .catch(() => setSessions([]));
  }, []);

  const createSession = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/sessions", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        router.push(`/session/${data.id}`);
      }
    } catch (error) {
      console.error("Failed to create session", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-[240px] h-full bg-zinc-900 border-r border-zinc-800 flex flex-col">
      <div className="p-4 border-b border-zinc-800">
        <button
          onClick={createSession}
          disabled={loading}
          className="w-full bg-zinc-100 text-zinc-900 hover:bg-zinc-200 font-medium py-2 px-4 rounded transition-colors disabled:opacity-50"
        >
          {loading ? "Creating..." : "New Session"}
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {sessions.map((session) => (
          <Link
            key={session.id}
            href={`/session/${session.id}`}
            className="block px-3 py-2 rounded hover:bg-zinc-800 text-sm text-zinc-300 transition-colors"
          >
            Session {session.id.slice(0, 8)}
          </Link>
        ))}
        {sessions.length === 0 && (
          <div className="text-zinc-500 text-sm p-2 text-center">
            No sessions yet
          </div>
        )}
      </div>
    </div>
  );
}
