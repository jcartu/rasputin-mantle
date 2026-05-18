"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { PlaybookGrid } from "@/components/playbook/playbook-grid"
import { listPlaybooks, type Playbook } from "@/lib/playbooks"
import { createSession, execCode } from "@/lib/api"
import { useToast } from "@/components/ui/toast"

export default function PlaybooksPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [playbooks, setPlaybooks] = React.useState<Playbook[]>([])
  const [isLoading, setIsLoading] = React.useState(true)

  React.useEffect(() => {
    listPlaybooks()
      .then(setPlaybooks)
      .catch((error) => {
        toast({
          title: "Failed to load playbooks",
          description: error instanceof Error ? error.message : "Unknown error",
          variant: "destructive",
        })
      })
      .finally(() => setIsLoading(false))
  }, [toast])

  const handleRunPlaybook = async (playbook: Playbook) => {
    try {
      const session = await createSession()
      await execCode(session.session_id, playbook.prompt_template)
      router.push(`/session/${session.session_id}`)
    } catch (error) {
      toast({
        title: "Failed to start playbook",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="container py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Playbooks</h1>
        <p className="text-muted-foreground">
          Curated templates and your saved workflows.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : (
        <PlaybookGrid playbooks={playbooks} onRun={handleRunPlaybook} />
      )}
    </div>
  )
}
