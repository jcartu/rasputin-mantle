"use client";

import { useState, useEffect } from "react";

export function ComputerView() {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [key, setKey] = useState(0);

  const nekoUrl = process.env.NEXT_PUBLIC_NEKO_URL || "http://127.0.0.1:8080";
  const iframeSrc = `${nekoUrl}/?user=mantle&pass=mantle-dev`;

  useEffect(() => {
    setIsLoading(true);
    setHasError(false);
  }, [key]);

  const handleLoad = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  const handleReconnect = () => {
    setKey((prev) => prev + 1);
  };

  return (
    <div className="w-full h-full bg-zinc-950 flex items-center justify-center relative overflow-hidden">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-zinc-900 z-10">
          <div className="w-full max-w-4xl aspect-video bg-zinc-800 animate-pulse rounded-lg shadow-lg border border-zinc-700 flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-zinc-600 border-t-zinc-300 rounded-full animate-spin"></div>
          </div>
        </div>
      )}

      {hasError && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-zinc-900 z-20 text-zinc-300">
          <div className="mb-4 text-lg">Connection lost</div>
          <button
            onClick={handleReconnect}
            className="px-4 py-2 bg-zinc-100 text-zinc-900 rounded hover:bg-zinc-200 transition-colors font-medium"
          >
            Reconnect
          </button>
        </div>
      )}

      <div className="w-full h-full max-h-full flex items-center justify-center p-4">
        <div className="w-full aspect-video max-h-full relative shadow-2xl ring-1 ring-zinc-800 rounded overflow-hidden bg-black">
          <iframe
            key={key}
            src={iframeSrc}
            className="w-full h-full border-0"
            onLoad={handleLoad}
            onError={handleError}
            allow="clipboard-read; clipboard-write; display-capture"
          />
        </div>
      </div>
    </div>
  );
}
