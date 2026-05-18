"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { PlaybookGrid } from "@/components/playbook/playbook-grid"
import { listPlaybooks, type Playbook } from "@/lib/playbooks"
import { listSessions, createSession, execCode, type SessionInfo } from "@/lib/api"
import { useToast } from "@/components/ui/toast"
import { Button } from "@/components/ui/button"
import { Plus, Clock } from "lucide-react"
import Link from "next/link"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function AppHomePage() {
  const router = useRouter()
  const { toast } = useToast()
  const [playbooks, setPlaybooks] = React.useState<Playbook[]>([])
  const [sessions, setSessions] = React.useState<SessionInfo[]>([])
  const [isLoading, setIsLoading] = React.useState(true)
  const [isCreating, setIsCreating] = React.useState(false)

  React.useEffect(() => {
    // First-visit detection
    if (typeof window !== "undefined") {
      const hasOnboarded = localStorage.getItem("mantle:onboarding:complete")
      if (!hasOnboarded) {
        router.push("/onboarding")
        return
      }
    }

    Promise.all([listPlaybooks(), listSessions()])
      .then(([playbooksData, sessionsData]) => {
        // Get 3 random playbooks
        const shuffled = [...playbooksData].sort(() => 0.5 - Math.random())
        setPlaybooks(shuffled.slice(0, 3))
        
        // Get 5 most recent sessions
        const sorted = [...sessionsData].sort((a, b) => b.created_at - a.created_at)
        setSessions(sorted.slice(0, 5))
      })
      .catch((error) => {
        toast({
          title: "Failed to load dashboard",
          description: error instanceof Error ? error.message : "Unknown error",
          variant: "destructive",
        })
      })
      .finally(() => setIsLoading(false))
  }, [router, toast])

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

  const handleStartBlank = async () => {
    setIsCreating(true)
    try {
      const session = await createSession()
      router.push(`/session/${session.session_id}`)
    } catch (error) {
      toast({
        title: "Failed to create session",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      })
      setIsCreating(false)
    }
  }

  if (isLoading) {
    return (
      <div className="container py-8 space-y-8">
        <div className="h-8 w-48 bg-muted rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container py-8 space-y-12">
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Try this</h2>
          <Link 
            href="/playbooks" 
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            View all playbooks &rarr;
          </Link>
        </div>
        <PlaybookGrid playbooks={playbooks} onRun={handleRunPlaybook} />
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold tracking-tight">Recent sessions</h2>
        {sessions.length === 0 ? (
          <p className="text-muted-foreground">No recent sessions.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sessions.map((session) => (
              <Link key={session.session_id} href={`/session/${session.session_id}`}>
                <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      {new Date(session.created_at * 1000).toLocaleString()}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Status: {session.status}</span>
                      <span>${(session.cost_dollars ?? 0).toFixed(4)}</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      <div className="flex justify-center pt-8 border-t">
        <Button size="lg" onClick={handleStartBlank} disabled={isCreating}>
          <Plus className="mr-2 h-5 w-5" />
          {isCreating ? "Creating..." : "Start blank session"}
        </Button>
      </div>
    </div>
  )
}
