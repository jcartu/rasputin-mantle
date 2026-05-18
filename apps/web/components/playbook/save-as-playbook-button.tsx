"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import Dialog from "@/components/ui/dialog"

import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { BookmarkPlus } from "lucide-react"
import { savePlaybook } from "@/lib/playbooks"
import { useToast } from "@/components/ui/toast"

export interface SaveAsPlaybookButtonProps {
  sessionId: string
  defaultTitle?: string
}

export function SaveAsPlaybookButton({
  sessionId,
  defaultTitle = "",
}: SaveAsPlaybookButtonProps) {
  const [open, setOpen] = React.useState(false)
  const [title, setTitle] = React.useState(defaultTitle)
  const [description, setDescription] = React.useState("")
  const [isSaving, setIsSaving] = React.useState(false)
  const { toast } = useToast()

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    setIsSaving(true)
    try {
      await savePlaybook({
        session_id: sessionId,
        title,
        description,
      })
      toast({
        title: "Playbook saved",
        description: "You can now use this playbook from the gallery.",
      })
      setOpen(false)
    } catch (error) {
      toast({
        title: "Failed to save playbook",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
        <BookmarkPlus className="mr-2 h-4 w-4" />
        Save as playbook
      </Button>
      <Dialog
        isOpen={open}
        onClose={() => setOpen(false)}
        title="Save as Playbook"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isSaving}
            >
              Cancel
            </Button>
            <Button type="submit" form="save-playbook-form" disabled={!title.trim() || isSaving}>
              {isSaving ? "Saving..." : "Save Playbook"}
            </Button>
          </>
        }
      >
        <form id="save-playbook-form" onSubmit={handleSave}>
          <p className="text-sm text-muted-foreground mb-4">
            Save this session's plan and initial prompt as a reusable playbook.
          </p>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label htmlFor="title" className="text-sm font-medium">
                Title
              </label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Weekly Report Generator"
                disabled={isSaving}
                required
              />
            </div>
            <div className="grid gap-2">
              <label htmlFor="description" className="text-sm font-medium">
                Description
              </label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Briefly describe what this playbook does..."
                disabled={isSaving}
                className="resize-none"
              />
            </div>
          </div>
        </form>
      </Dialog>
    </>
  )
}
