"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: string;
}

interface ChatPanelProps {
  sessionId: string;
}

export function ChatPanel({ sessionId }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch initial messages
    fetch(`/api/sessions/${sessionId}/messages`)
      .then((res) => {
        if (res.ok) return res.json();
        return [];
      })
      .then((data) => setMessages(data))
      .catch((err) => console.error("Failed to fetch messages", err));
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSubmitting) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsSubmitting(true);

    try {
      const res = await fetch(`/api/sessions/${sessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: userMsg.content }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.message) {
          setMessages((prev) => [...prev, data.message]);
        }
      }
    } catch (error) {
      console.error("Failed to send message", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderContent = (content: string) => {
    // Simple markdown code block parsing
    const parts = content.split(/(```[\s\S]*?```)/g);
    
    return parts.map((part, i) => {
      if (part.startsWith("```") && part.endsWith("```")) {
        const code = part.slice(3, -3).replace(/^[a-z]+\n/, ""); // Remove language tag if present
        return (
          <pre key={i} className="font-mono bg-zinc-950 p-3 rounded-md my-2 overflow-x-auto text-sm border border-zinc-800 text-zinc-300">
            <code>{code}</code>
          </pre>
        );
      }
      return <span key={i} className="font-sans whitespace-pre-wrap">{part}</span>;
    });
  };

  return (
    <div className="flex flex-col h-full bg-zinc-900 border-l border-zinc-800">
      <div className="px-4 py-3 border-b border-zinc-800 font-medium text-zinc-200">
        Chat
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.role === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-4 py-2 ${
                msg.role === "user"
                  ? "bg-zinc-100 text-zinc-900"
                  : "bg-zinc-800 text-zinc-200 border border-zinc-700"
              }`}
            >
              <div className="text-sm">{renderContent(msg.content)}</div>
            </div>
            <span className="text-[10px] text-zinc-500 mt-1 px-1">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}
        {messages.length === 0 && (
          <div className="text-zinc-500 text-center py-8 text-sm">
            No messages yet. Start the conversation!
          </div>
        )}
      </div>

      <div className="p-4 border-t border-zinc-800 bg-zinc-900">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            disabled={isSubmitting}
            className="flex-1 bg-zinc-950 border border-zinc-800 rounded-md px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:ring-1 focus:ring-zinc-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isSubmitting}
            className="bg-zinc-100 text-zinc-900 px-4 py-2 rounded-md text-sm font-medium hover:bg-zinc-200 transition-colors disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
