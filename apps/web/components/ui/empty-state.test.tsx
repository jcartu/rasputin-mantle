import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { EmptyState } from "./empty-state"

describe("EmptyState", () => {
  it("renders title correctly", () => {
    render(<EmptyState title="No items found" />)
    expect(screen.getByText("No items found")).toBeInTheDocument()
  })

  it("renders description when provided", () => {
    render(
      <EmptyState
        title="No items found"
        description="Try adjusting your search filters."
      />
    )
    expect(screen.getByText("Try adjusting your search filters.")).toBeInTheDocument()
  })

  it("renders action when provided", () => {
    render(
      <EmptyState
        title="No items found"
        action={<button>Create Item</button>}
      />
    )
    expect(screen.getByRole("button", { name: "Create Item" })).toBeInTheDocument()
  })

  it("renders icon when provided", () => {
    render(
      <EmptyState
        title="No items found"
        icon={<svg data-testid="test-icon" />}
      />
    )
    expect(screen.getByTestId("test-icon")).toBeInTheDocument()
  })

  it("applies custom className", () => {
    const { container } = render(
      <EmptyState title="No items found" className="custom-class" />
    )
    expect(container.firstChild).toHaveClass("custom-class")
  })
})
