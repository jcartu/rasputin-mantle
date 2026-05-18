import * as React from "react"
import { PlaybookCard } from "./playbook-card"
import { EmptyState } from "@/components/ui/empty-state"
import { BookTemplate } from "lucide-react"
import type { Playbook } from "@/lib/playbooks"

export interface PlaybookGridProps {
  playbooks: Playbook[]
  onRun?: (playbook: Playbook) => void
}

export function PlaybookGrid({ playbooks, onRun }: PlaybookGridProps) {
  if (playbooks.length === 0) {
    return (
      <EmptyState
        icon={<BookTemplate className="h-6 w-6 text-muted-foreground" />}
        title="No playbooks found"
        description="There are no playbooks available right now."
      />
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {playbooks.map((playbook) => (
        <PlaybookCard 
          key={playbook.id} 
          playbook={playbook} 
          onRun={onRun} 
        />
      ))}
    </div>
  )
}
