"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Search, Wrench, FileText, Calendar } from "lucide-react"
import { IntentCard } from "@/components/onboarding/intent-card"
import { TemplateCard } from "@/components/onboarding/template-card"
import { FirstTask } from "@/components/onboarding/first-task"
import { listPlaybooks, type Playbook } from "@/lib/playbooks"
import { createSession, execCode } from "@/lib/api"
import { useToast } from "@/components/ui/toast"

const INTENTS = [
  {
    id: "Research",
    title: "Research",
    description: "Find information, analyze competitors, or review literature.",
    icon: <Search className="h-5 w-5" />,
  },
  {
    id: "Build",
    title: "Build",
    description: "Create landing pages, dashboards, or new features.",
    icon: <Wrench className="h-5 w-5" />,
  },
  {
    id: "Summarize",
    title: "Summarize",
    description: "Condense meeting notes, articles, or long documents.",
    icon: <FileText className="h-5 w-5" />,
  },
  {
    id: "Schedule",
    title: "Schedule",
    description: "Plan your day, week, or generate reports.",
    icon: <Calendar className="h-5 w-5" />,
  },
]

export default function OnboardingPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [step, setStep] = React.useState(1)
  const [selectedIntent, setSelectedIntent] = React.useState<string | null>(null)
  const [selectedPlaybook, setSelectedPlaybook] = React.useState<Playbook | null>(null)
  const [playbooks, setPlaybooks] = React.useState<Playbook[]>([])
  const [isLoading, setIsLoading] = React.useState(false)

  React.useEffect(() => {
    listPlaybooks().then(setPlaybooks).catch(console.error)
  }, [])

  const handleSkip = () => {
    localStorage.setItem("mantle:onboarding:complete", "true")
    router.push("/")
  }

  const handleIntentSelect = (intentId: string) => {
    setSelectedIntent(intentId)
    setStep(2)
  }

  const handlePlaybookSelect = (playbook: Playbook) => {
    setSelectedPlaybook(playbook)
    setStep(3)
  }

  const handleRunTask = async (prompt: string) => {
    setIsLoading(true)
    try {
      const session = await createSession()
      await execCode(session.session_id, prompt)
      localStorage.setItem("mantle:onboarding:complete", "true")
      router.push(`/session/${session.session_id}`)
    } catch (error) {
      toast({
        title: "Failed to start task",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      })
      setIsLoading(false)
    }
  }

  const filteredPlaybooks = playbooks.filter((p) => p.intent === selectedIntent)

  return (
    <div className="container max-w-4xl py-12">
      <div className="flex items-center justify-between mb-8">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Welcome to Rasputin Mantle</h1>
          <p className="text-muted-foreground">Let's get you started with your first task.</p>
        </div>
        <button
          onClick={handleSkip}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          I know what I'm doing &rarr;
        </button>
      </div>

      <div className="space-y-8">
        {step === 1 && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
            <h2 className="text-xl font-semibold">What do you want to do today?</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {INTENTS.map((intent) => (
                <IntentCard
                  key={intent.id}
                  title={intent.title}
                  description={intent.description}
                  icon={intent.icon}
                  onClick={() => handleIntentSelect(intent.id)}
                />
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setStep(1)}
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                &larr; Back
              </button>
              <h2 className="text-xl font-semibold">Pick a starting template</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredPlaybooks.map((playbook) => (
                <TemplateCard
                  key={playbook.id}
                  playbook={playbook}
                  onClick={() => handlePlaybookSelect(playbook)}
                />
              ))}
            </div>
          </div>
        )}

        {step === 3 && selectedPlaybook && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setStep(2)}
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                &larr; Back
              </button>
              <h2 className="text-xl font-semibold">First task</h2>
            </div>
            <div className="max-w-2xl">
              <FirstTask
                initialPrompt={selectedPlaybook.prompt_template}
                onSubmit={handleRunTask}
                isLoading={isLoading}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
