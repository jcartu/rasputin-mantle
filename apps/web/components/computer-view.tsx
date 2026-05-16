"use client";
import { Monitor, Maximize2 } from "lucide-react";

export function ComputerView() {
  return (
    <div className="flex flex-col h-full bg-[#0a0a0f]">
      <div className="p-4 border-b border-white/10 font-medium text-sm flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-accent" />
          <span>Live Computer View</span>
        </div>
        <button className="text-white/50 hover:text-white transition-colors">
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex-1 p-4 flex items-center justify-center">
        <div className="w-full h-full max-w-4xl max-h-[600px] bg-black border border-white/10 rounded-lg flex items-center justify-center shadow-2xl relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjMDAwIj48L3JlY3Q+CjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiMzMzMiPjwvcmVjdD4KPC9zdmc+')] opacity-50"></div>
          <div className="flex flex-col items-center gap-3 z-10">
            <Monitor className="w-12 h-12 text-white/20" />
            <div className="text-white/40 text-sm font-mono">Neko WebRTC Stream Placeholder</div>
            <div className="flex items-center gap-2 mt-2">
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
              <span className="text-xs text-white/30 uppercase tracking-wider">Disconnected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
