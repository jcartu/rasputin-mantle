import * as React from "react"
import { Card, CardBody, CardFooter, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Play } from "lucide-react"
import type { Playbook } from "@/lib/playbooks"

export interface PlaybookCardProps {
  playbook: Playbook
  onRun?: (playbook: Playbook) => void
}

export function PlaybookCard({ playbook, onRun }: PlaybookCardProps) {
  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold line-clamp-1" title={playbook.title}>
            {playbook.title}
          </h3>
          <div className="flex gap-1 shrink-0">
            {playbook.created_by === "you" && (
              <Badge variant="outline" className="bg-primary/5">by you</Badge>
            )}
            <Badge variant="secondary">{playbook.intent}</Badge>
          </div>
        </div>
      </CardHeader>
      <CardBody className="flex-1">
        <p className="text-sm text-muted-foreground line-clamp-3" title={playbook.description}>
          {playbook.description}
        </p>
      </CardBody>
      <CardFooter>
        <Button 
          variant="secondary" 
          className="w-full" 
          onClick={() => onRun?.(playbook)}
        >
          <Play className="mr-2 h-4 w-4" />
          Run
        </Button>
      </CardFooter>
    </Card>
  )
}
