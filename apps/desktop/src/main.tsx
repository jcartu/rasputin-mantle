import React, { useRef, useState } from "react";
import { createRoot } from "react-dom/client";

type Message = { id: string; role: "user" | "agent"; content: string };

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { id: "welcome", role: "agent", content: "Rasputin Mantle desktop shell is connected to the local gateway." },
  ]);
  const [input, setInput] = useState("");
  const [recording, setRecording] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function sendMessage(content: string) {
    if (!content.trim()) return;
    const userMessage = { id: crypto.randomUUID(), role: "user" as const, content };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    try {
      const response = await fetch("http://127.0.0.1:8000/api/sessions/desktop/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      if (response.ok) {
        const data = await response.json();
        const contentFromGateway = data.message?.content ?? data.content ?? "Message accepted by gateway.";
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "agent", content: contentFromGateway }]);
      } else {
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "agent", content: `Gateway returned ${response.status}.` }]);
      }
    } catch (error) {
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "agent", content: `Gateway unavailable: ${String(error)}` }]);
    }
  }

  async function toggleMic() {
    if (recording) {
      recorderRef.current?.stop();
      setRecording(false);
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "agent", content: "MediaRecorder is unavailable in this runtime." }]);
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };
    recorder.onstop = async () => {
      stream.getTracks().forEach((track) => track.stop());
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", blob, "speech.webm");
      try {
        const response = await fetch("http://127.0.0.1:8000/api/voice/transcribe", { method: "POST", body: formData });
        const data = await response.json();
        const transcript = data.text ?? data.transcript ?? "";
        if (transcript) await sendMessage(transcript);
      } catch (error) {
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "agent", content: `Voice input unavailable: ${String(error)}` }]);
      }
    };
    recorderRef.current = recorder;
    recorder.start();
    setRecording(true);
  }

  return (
    <main className="shell">
      <aside>
        <div className="brand">Rasputin Mantle</div>
        <div className="muted">Local desktop wrapper for gateway, voice, browser, MCP, scheduler, and memory workflows.</div>
      </aside>
      <section className="chat">
        <div className="messages">
          {messages.map((message) => (
            <article className={message.role} key={message.id}>{message.content}</article>
          ))}
        </div>
        <form onSubmit={(event) => { event.preventDefault(); void sendMessage(input); }}>
          <button type="button" className={recording ? "recording" : ""} onClick={() => void toggleMic()}>{recording ? "Stop" : "Mic"}</button>
          <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask Mantle to work..." />
          <button type="submit">Send</button>
        </form>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);

const style = document.createElement("style");
style.textContent = `
  :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #09090b; color: #e4e4e7; }
  body { margin: 0; }
  .shell { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
  aside { padding: 28px; border-right: 1px solid #27272a; background: #0f0f12; }
  .brand { font-size: 20px; font-weight: 700; margin-bottom: 14px; }
  .muted { color: #a1a1aa; line-height: 1.5; font-size: 14px; }
  .chat { display: flex; flex-direction: column; min-height: 100vh; }
  .messages { flex: 1; padding: 28px; display: flex; flex-direction: column; gap: 14px; overflow: auto; }
  article { max-width: 720px; padding: 12px 14px; border-radius: 14px; border: 1px solid #3f3f46; white-space: pre-wrap; }
  article.user { align-self: flex-end; background: #f4f4f5; color: #18181b; }
  article.agent { align-self: flex-start; background: #18181b; color: #e4e4e7; }
  form { display: flex; gap: 10px; padding: 18px; border-top: 1px solid #27272a; background: #0f0f12; }
  input { flex: 1; border: 1px solid #3f3f46; background: #09090b; color: #e4e4e7; padding: 12px; border-radius: 10px; }
  button { border: 0; border-radius: 10px; padding: 0 16px; background: #e4e4e7; color: #18181b; font-weight: 700; }
  button.recording { background: #ef4444; color: white; }
`;
document.head.appendChild(style);
