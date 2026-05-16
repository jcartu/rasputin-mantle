"use client";

import { useState } from "react";
import { ListTree, FolderTree, FileCode, CheckCircle2, Circle, ChevronRight, ChevronDown } from "lucide-react";

export function PanelRight() {
  const [activeTab, setActiveTab] = useState<"plan" | "files">("plan");

  return (
    <div className="flex flex-col h-full bg-[#0f0f14] border-l border-white/10">
      <div className="flex border-b border-white/10">
        <button 
          onClick={() => setActiveTab("plan")}
          className={`flex-1 p-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${
            activeTab === "plan" ? "border-accent text-white" : "border-transparent text-white/50 hover:text-white/80"
          }`}
        >
          <ListTree className="w-4 h-4" />
          Plan Tree
        </button>
        <button 
          onClick={() => setActiveTab("files")}
          className={`flex-1 p-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${
            activeTab === "files" ? "border-accent text-white" : "border-transparent text-white/50 hover:text-white/80"
          }`}
        >
          <FolderTree className="w-4 h-4" />
          File Tree
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === "plan" ? (
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-2">Current Objective</div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                <span className="text-sm text-white/80 line-through">Analyze repository structure</span>
              </div>
              <div className="flex items-start gap-2">
                <Circle className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                <span className="text-sm text-white">Implement database connection</span>
              </div>
              <div className="flex items-start gap-2 pl-6">
                <Circle className="w-3 h-3 text-white/30 mt-1 shrink-0" />
                <span className="text-sm text-white/60">Read config files</span>
              </div>
              <div className="flex items-start gap-2 pl-6">
                <Circle className="w-3 h-3 text-white/30 mt-1 shrink-0" />
                <span className="text-sm text-white/60">Write connection logic</span>
              </div>
              <div className="flex items-start gap-2">
                <Circle className="w-4 h-4 text-white/30 mt-0.5 shrink-0" />
                <span className="text-sm text-white/60">Run tests</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-1 font-mono text-sm">
            <div className="flex items-center gap-1 text-white/80 hover:bg-white/5 p-1 rounded cursor-pointer">
              <ChevronDown className="w-4 h-4 text-white/50" />
              <FolderTree className="w-4 h-4 text-accent/70" />
              <span>src</span>
            </div>
            <div className="flex items-center gap-1 text-white/60 hover:bg-white/5 p-1 rounded cursor-pointer pl-5">
              <ChevronRight className="w-4 h-4 text-white/50" />
              <FolderTree className="w-4 h-4 text-accent/70" />
              <span>components</span>
            </div>
            <div className="flex items-center gap-1 text-white/60 hover:bg-white/5 p-1 rounded cursor-pointer pl-5">
              <ChevronDown className="w-4 h-4 text-white/50" />
              <FolderTree className="w-4 h-4 text-accent/70" />
              <span>lib</span>
            </div>
            <div className="flex items-center gap-1 text-white/80 hover:bg-white/5 p-1 rounded cursor-pointer pl-10 bg-white/5">
              <FileCode className="w-4 h-4 text-blue-400" />
              <span>db.ts</span>
            </div>
            <div className="flex items-center gap-1 text-white/60 hover:bg-white/5 p-1 rounded cursor-pointer pl-10">
              <FileCode className="w-4 h-4 text-blue-400" />
              <span>utils.ts</span>
            </div>
            <div className="flex items-center gap-1 text-white/60 hover:bg-white/5 p-1 rounded cursor-pointer pl-5">
              <FileCode className="w-4 h-4 text-yellow-400" />
              <span>index.ts</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
