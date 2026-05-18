import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { PlaybookCard } from "./playbook-card"
import { PlaybookGrid } from "./playbook-grid"
import { SaveAsPlaybookButton } from "./save-as-playbook-button"
import * as playbooksApi from "@/lib/playbooks"

// Mock the toast hook
vi.mock("@/components/ui/toast", () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}))

// Mock the API
vi.mock("@/lib/playbooks", () => ({
  savePlaybook: vi.fn(),
}))

const mockPlaybook = {
  id: "1",
  title: "Test Playbook",
  description: "Test description",
  intent: "Research",
  prompt_template: "Test prompt",
  created_by: "system",
  created_at: "2026-05-19T00:00:00Z",
}

describe("PlaybookCard", () => {
  it("renders correctly", () => {
    render(<PlaybookCard playbook={mockPlaybook} />)
    expect(screen.getByText("Test Playbook")).toBeInTheDocument()
    expect(screen.getByText("Test description")).toBeInTheDocument()
    expect(screen.getByText("Research")).toBeInTheDocument()
  })

  it("shows 'by you' badge for user playbooks", () => {
    render(<PlaybookCard playbook={{ ...mockPlaybook, created_by: "you" }} />)
    expect(screen.getByText("by you")).toBeInTheDocument()
  })

  it("handles run click", () => {
    const onRun = vi.fn()
    render(<PlaybookCard playbook={mockPlaybook} onRun={onRun} />)
    fireEvent.click(screen.getByRole("button", { name: /run/i }))
    expect(onRun).toHaveBeenCalledWith(mockPlaybook)
  })
})

describe("PlaybookGrid", () => {
  it("renders empty state when no playbooks", () => {
    render(<PlaybookGrid playbooks={[]} />)
    expect(screen.getByText("No playbooks found")).toBeInTheDocument()
  })

  it("renders playbooks", () => {
    render(<PlaybookGrid playbooks={[mockPlaybook]} />)
    expect(screen.getByText("Test Playbook")).toBeInTheDocument()
  })
})

describe("SaveAsPlaybookButton", () => {
  it("renders trigger button", () => {
    render(<SaveAsPlaybookButton sessionId="123" />)
    expect(screen.getByRole("button", { name: /save as playbook/i })).toBeInTheDocument()
  })

  it("opens dialog and saves", async () => {
    vi.mocked(playbooksApi.savePlaybook).mockResolvedValueOnce({
      ...mockPlaybook,
      id: "new-id",
    })

    render(<SaveAsPlaybookButton sessionId="123" />)
    
    // Open dialog
    fireEvent.click(screen.getByRole("button", { name: /save as playbook/i }))
    
    // Fill form
    const titleInput = screen.getByLabelText(/title/i)
    fireEvent.change(titleInput, { target: { value: "My Playbook" } })
    
    // Submit
    fireEvent.click(screen.getByRole("button", { name: "Save Playbook" }))
    
    await waitFor(() => {
      expect(playbooksApi.savePlaybook).toHaveBeenCalledWith({
        session_id: "123",
        title: "My Playbook",
        description: "",
      })
    })
  })
})
