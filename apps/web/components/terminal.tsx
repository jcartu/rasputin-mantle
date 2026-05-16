"use client";

import { useState } from "react";
import { Terminal as TerminalIcon, ChevronUp, ChevronDown, X } from "lucide-react";

export function Terminal() {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!isExpanded) {
    return (
      <div 
        className="h-10 bg-[#0a0a0f] border-t border-white/10 flex items-center px-4 cursor-pointer hover:bg-white/5 transition-colors"
        onClick={() => setIsExpanded(true)}
      >
        <div className="flex items-center gap-2 text-white/70 text-sm font-medium">
          <TerminalIcon className="w-4 h-4" />
          <span>Terminal</span>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-xs text-white/50 font-mono">0 errors</span>
          </div>
          <ChevronUp className="w-4 h-4 text-white/50 ml-2" />
        </div>
      </div>
    );
  }

  return (
    <div className="h-64 bg-[#0a0a0f] border-t border-white/10 flex flex-col">
      <div className="h-10 border-b border-white/10 flex items-center px-4 justify-between bg-[#0f0f14]">
        <div className="flex items-center gap-2 text-white/90 text-sm font-medium">
          <TerminalIcon className="w-4 h-4 text-accent" />
          <span>Terminal</span>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setIsExpanded(false)}
            className="p-1 text-white/50 hover:text-white transition-colors rounded hover:bg-white/10"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
          <button className="p-1 text-white/50 hover:text-white transition-colors rounded hover:bg-white/10">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="flex-1 p-4 font-mono text-sm overflow-y-auto">
        <div className="text-white/50 mb-2">$ pnpm dev</div>
        <div className="text-green-400 mb-1">ready - started server on 0.0.0.0:3000, url: http://localhost:3000</div>
        <div className="text-white/80 mb-1">event - compiled client and server successfully in 1250 ms (165 modules)</div>
        <div className="text-white/80 mb-1">wait  - compiling...</div>
        <div className="text-white/80 mb-1">event - compiled client and server successfully in 234 ms (165 modules)</div>
        <div className="text-white/50 mt-4 mb-2">$ tail -f /var/log/syslog</div>
        <div className="text-white/70 mb-1">May 16 12:34:56 rasputin systemd[1]: Started Session 42 of user josh.</div>
        <div className="text-blue-400 mb-1">May 16 12:35:01 rasputin CRON[12345]: (root) CMD (command -v debian-sa1 &gt; /dev/null &amp;&amp; debian-sa1 1 1)</div>
        <div className="flex items-center gap-2 mt-2">
          <span className="text-accent">❯</span>
          <span className="w-2 h-4 bg-white/50 animate-pulse"></span>
        </div>
      </div>
    </div>
  );
}
