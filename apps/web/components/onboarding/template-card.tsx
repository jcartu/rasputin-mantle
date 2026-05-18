import * as React from "react"
import { Card, CardBody, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Playbook } from "@/lib/playbooks"

export interface TemplateCardProps {
  playbook: Playbook
  selected?: boolean
  onClick?: () => void
}

export function TemplateCard({
  playbook,
  selected,
  onClick,
}: TemplateCardProps) {
  return (
    <Card
      className={cn(
        "cursor-pointer transition-all hover:border-primary/50",
        selected && "border-primary ring-1 ring-primary"
      )}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onClick?.()
        }
      }}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold">{playbook.title}</h3>
          <Badge variant="secondary">{playbook.intent}</Badge>
        </div>
      </CardHeader>
      <CardBody>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {playbook.description}
        </p>
      </CardBody>
    </Card>
  )
}
