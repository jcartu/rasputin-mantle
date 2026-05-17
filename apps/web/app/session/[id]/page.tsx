"use client";

import { use } from "react";
import { Sidebar } from "@/components/sidebar";
import { ComputerView } from "@/components/computer-view";
import { ChatPanel } from "@/components/chat-panel";
import { SessionStream } from "@/components/session-stream";
import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from "react-resizable-panels";

export default function SessionPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const sessionId = resolvedParams.id;

  return (
    <>
      <Sidebar />
      <main className="flex-1 h-full overflow-hidden bg-zinc-950">
        <PanelGroup orientation="vertical">
          <Panel defaultSize={60} minSize={30}>
            <ComputerView />
          </Panel>
          <PanelResizeHandle className="h-1 bg-zinc-800 hover:bg-zinc-700 transition-colors cursor-row-resize" />
          <Panel defaultSize={40} minSize={20}>
            <PanelGroup orientation="horizontal">
              <Panel defaultSize={50} minSize={20}>
                <SessionStream sessionId={sessionId} />
              </Panel>
              <PanelResizeHandle className="w-1 bg-zinc-800 hover:bg-zinc-700 transition-colors cursor-col-resize" />
              <Panel defaultSize={50} minSize={20}>
                <ChatPanel sessionId={sessionId} />
              </Panel>
            </PanelGroup>
          </Panel>
        </PanelGroup>
      </main>
    </>
  );
}
