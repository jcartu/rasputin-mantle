"use client";

import { useState, useEffect } from "react";

export function ComputerView() {
  const [isAvailable, setIsAvailable] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [key, setKey] = useState(0);

  const nekoUrl = process.env.NEXT_PUBLIC_NEKO_URL || "http://127.0.0.1:8080";
  const iframeSrc = `${nekoUrl}/?user=mantle&pass=mantle-dev`;

  useEffect(() => {
    // Probe Neko availability before showing iframe
    fetch(`${nekoUrl}/health`, { method: "HEAD" })
      .then((res) => {
        if (res.ok) setIsAvailable(true);
        else setHasError(true);
      })
      .catch(() => setHasError(true));
  }, [key, nekoUrl]);

  const handleReconnect = () => {
    setHasError(false);
    setIsAvailable(false);
    setKey((prev) => prev + 1);
  };

  const handleIframeError = () => {
    setHasError(true);
    setIsAvailable(false);
  };

  // Neko is not running — show honest empty state
  if (hasError || !isAvailable) {
    return (
      <div className="w-full h-full bg-zinc-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-zinc-400 max-w-md text-center">
          <div className="text-4xl opacity-30">⏻</div>
          <div className="text-lg font-medium text-zinc-300">Live Computer View</div>
          <div className="text-sm text-zinc-500">
            Neko desktop instance is not available. Deploy Neko to{" "}
            <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-zinc-300">{nekoUrl}</code> to enable
            real-time screen sharing.
          </div>
          <button
            onClick={handleReconnect}
            className="mt-2 px-4 py-2 bg-zinc-800 text-zinc-300 rounded hover:bg-zinc-700 transition-colors text-sm font-medium border border-zinc-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-zinc-950 flex items-center justify-center overflow-hidden">
      <div className="w-full h-full max-h-full flex items-center justify-center p-4">
        <div className="w-full aspect-video max-h-full relative shadow-2xl ring-1 ring-zinc-800 rounded overflow-hidden bg-black">
          <iframe
            key={key}
            src={iframeSrc}
            className="w-full h-full border-0"
            onError={handleIframeError}
            allow="clipboard-read; clipboard-write; display-capture"
          />
        </div>
      </div>
    </div>
  );
}
