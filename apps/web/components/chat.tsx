"use client";
import { Send, Bot, User } from "lucide-react";

export function Chat() {
  return (
    <div className="flex flex-col h-full bg-[#0f0f14] border-r border-white/10">
      <div className="p-4 border-b border-white/10 font-medium text-sm flex items-center gap-2">
        <Bot className="w-4 h-4 text-accent" />
        <span>Agent Chat</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="flex gap-3">
          <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center shrink-0">
            <User className="w-4 h-4 text-white/70" />
          </div>
          <div className="flex-1">
            <div className="text-xs text-white/50 mb-1">You</div>
            <div className="text-sm text-white/90">Can you check the logs for the latest deployment?</div>
          </div>
        </div>

        <div className="flex gap-3">
          <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center shrink-0">
            <Bot className="w-4 h-4 text-accent" />
          </div>
          <div className="flex-1">
            <div className="text-xs text-white/50 mb-1">Rasputin</div>
            <div className="text-sm text-white/90">
              I&apos;m looking at the logs now. It seems there was an error connecting to the database during the startup sequence.
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-white/10">
        <div className="relative">
          <input 
            type="text" 
            placeholder="Message agent..." 
            className="w-full bg-white/5 border border-white/10 rounded-md py-2 pl-3 pr-10 text-sm focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/50 transition-all"
          />
          <button className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-white/50 hover:text-accent transition-colors">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
