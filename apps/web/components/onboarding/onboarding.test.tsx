import { render, screen, fireEvent } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { IntentCard } from "./intent-card"
import { TemplateCard } from "./template-card"
import { FirstTask } from "./first-task"

describe("IntentCard", () => {
  it("renders correctly", () => {
    render(
      <IntentCard
        title="Research"
        description="Find information"
        icon={<span data-testid="icon" />}
      />
    )
    expect(screen.getByText("Research")).toBeInTheDocument()
    expect(screen.getByText("Find information")).toBeInTheDocument()
    expect(screen.getByTestId("icon")).toBeInTheDocument()
  })

  it("handles click", () => {
    const onClick = vi.fn()
    render(
      <IntentCard
        title="Research"
        description="Find information"
        icon={<span />}
        onClick={onClick}
      />
    )
    fireEvent.click(screen.getByRole("button"))
    expect(onClick).toHaveBeenCalled()
  })
})

describe("TemplateCard", () => {
  const mockPlaybook = {
    id: "1",
    title: "Test Playbook",
    description: "Test description",
    intent: "Research",
    prompt_template: "Test prompt",
    created_by: "system",
    created_at: "2026-05-19T00:00:00Z",
  }

  it("renders correctly", () => {
    render(<TemplateCard playbook={mockPlaybook} />)
    expect(screen.getByText("Test Playbook")).toBeInTheDocument()
    expect(screen.getByText("Test description")).toBeInTheDocument()
    expect(screen.getByText("Research")).toBeInTheDocument()
  })

  it("handles click", () => {
    const onClick = vi.fn()
    render(<TemplateCard playbook={mockPlaybook} onClick={onClick} />)
    fireEvent.click(screen.getByRole("button"))
    expect(onClick).toHaveBeenCalled()
  })
})

describe("FirstTask", () => {
  it("renders correctly", () => {
    render(<FirstTask initialPrompt="Test prompt" onSubmit={vi.fn()} />)
    expect(screen.getByDisplayValue("Test prompt")).toBeInTheDocument()
  })

  it("handles submit", () => {
    const onSubmit = vi.fn()
    render(<FirstTask initialPrompt="Test prompt" onSubmit={onSubmit} />)
    fireEvent.click(screen.getByRole("button", { name: /run task/i }))
    expect(onSubmit).toHaveBeenCalledWith("Test prompt")
  })

  it("updates prompt on change", () => {
    render(<FirstTask initialPrompt="Test prompt" onSubmit={vi.fn()} />)
    const textarea = screen.getByRole("textbox")
    fireEvent.change(textarea, { target: { value: "New prompt" } })
    expect(screen.getByDisplayValue("New prompt")).toBeInTheDocument()
  })
})
