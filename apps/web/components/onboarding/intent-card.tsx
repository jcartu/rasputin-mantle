import * as React from "react"
import { Card, CardBody, CardHeader } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export interface IntentCardProps {
  title: string
  description: string
  icon: React.ReactNode
  selected?: boolean
  onClick?: () => void
}

export function IntentCard({
  title,
  description,
  icon,
  selected,
  onClick,
}: IntentCardProps) {
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
      <CardHeader className="flex flex-row items-center gap-4 pb-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
          {icon}
        </div>
        <h3 className="text-lg font-semibold">{title}</h3>
      </CardHeader>
      <CardBody>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardBody>
    </Card>
  )
}
