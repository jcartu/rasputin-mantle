"use client";
"use client";

import { Chat } from "./chat";
import { ComputerView } from "./computer-view";
import { PanelRight } from "./panel-right";
import { Terminal } from "./terminal";

export function AppLayout() {
  return (
    <div className="flex flex-col h-screen w-full overflow-hidden bg-background text-foreground">
      {/* Top Header */}
      <header className="h-12 border-b border-white/10 bg-[#0a0a0f] flex items-center px-4 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-accent flex items-center justify-center text-black font-bold text-xs">R</div>
          <span className="font-semibold tracking-tight">Rasputin Mantle</span>
        </div>
        <div className="ml-auto flex items-center gap-4 text-sm text-white/60">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span>Gateway Connected</span>
          </div>
          <div className="px-2 py-1 rounded bg-white/5 border border-white/10 font-mono text-xs">
            v0.1.0-alpha
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Pane: Chat */}
        <div className="w-full lg:w-80 shrink-0 flex flex-col h-[50vh] lg:h-auto border-b lg:border-b-0 lg:border-r border-white/10">
          <Chat />
        </div>

        {/* Center Pane: Computer View */}
        <div className="flex-1 flex flex-col min-w-0 h-[50vh] lg:h-auto">
          <ComputerView />
        </div>

        {/* Right Pane: Plan/File Tree */}
        <div className="w-full lg:w-72 shrink-0 flex flex-col h-[50vh] lg:h-auto border-t lg:border-t-0 lg:border-l border-white/10">
          <PanelRight />
        </div>
      </div>

      {/* Bottom Drawer: Terminal */}
      <div className="shrink-0 w-full z-10">
        <Terminal />
      </div>
    </div>
  );
}
