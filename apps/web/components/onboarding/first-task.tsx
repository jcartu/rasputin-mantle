import * as React from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Play } from "lucide-react"

export interface FirstTaskProps {
  initialPrompt: string
  onSubmit: (prompt: string) => void
  isLoading?: boolean
}

export function FirstTask({
  initialPrompt,
  onSubmit,
  isLoading,
}: FirstTaskProps) {
  const [prompt, setPrompt] = React.useState(initialPrompt)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim()) {
      onSubmit(prompt)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label
          htmlFor="prompt"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Customize your prompt
        </label>
        <Textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="What would you like to do?"
          className="min-h-[150px] resize-none"
          disabled={isLoading}
        />
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={!prompt.trim() || isLoading}>
          {isLoading ? (
            "Starting..."
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Run Task
            </>
          )}
        </Button>
      </div>
    </form>
  )
}
