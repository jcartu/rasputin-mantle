from __future__ import annotations

# ruff: noqa: E501,I001

import json
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

TEMPLATES = {
    "minimal": {"accent": RGBColor(46, 52, 64), "bg": RGBColor(255, 255, 255), "fg": RGBColor(35, 35, 35)},
    "corporate": {"accent": RGBColor(31, 78, 121), "bg": RGBColor(245, 248, 252), "fg": RGBColor(20, 32, 48)},
    "pitch": {"accent": RGBColor(116, 60, 255), "bg": RGBColor(16, 18, 27), "fg": RGBColor(245, 245, 250)},
    "research": {"accent": RGBColor(17, 111, 93), "bg": RGBColor(250, 250, 245), "fg": RGBColor(28, 46, 43)},
}

DECK_PLANS = [
    (
        ("kickoff", "product launch"),
        "corporate",
        "Product Launch Kickoff",
        [
            ("Why This Launch Matters", ["Clarify the customer problem", "Connect launch goals to company priorities"]),
            ("Definition of Success", ["Set measurable business and customer outcomes", "Align owners on decision rights"]),
            ("Delivery Roadmap", ["Sequence discovery, build, readiness, and launch", "Surface key dependencies early"]),
            ("Risk Management", ["Name adoption, scope, and timing risks", "Assign mitigations and review cadence"]),
        ],
    ),
    (
        ("quarterly business review", "qbr"),
        "corporate",
        "Quarterly Business Review",
        [
            ("Executive Snapshot", ["Summarize performance versus plan", "Highlight the quarter's most important signal"]),
            ("Business Performance", ["Review revenue, retention, and efficiency", "Separate durable trends from one-time movement"]),
            ("Customer and Market Signals", ["Explain demand patterns and feedback", "Identify competitive or macro changes"]),
            ("Next-Quarter Priorities", ["Focus the operating agenda", "Clarify decisions needed from stakeholders"]),
        ],
    ),
    (
        ("investor", "pitch"),
        "pitch",
        "Investor Pitch",
        [
            ("Problem", ["Knowledge work is fragmented and manually coordinated", "Teams lack trustworthy automation for complex tasks"]),
            ("Solution", ["Secure agents plan, execute, and verify work", "Artifacts are observable, auditable, and repeatable"]),
            ("Market and Model", ["Enterprise productivity budgets are shifting toward automation", "Land through evaluation, expand through workflow coverage"]),
            ("Traction", ["Pilots validate urgent operations use cases", "Benchmark results create objective proof"]),
            ("Ask", ["Fund product hardening and go-to-market", "Hire for platform, security, and customer success"]),
        ],
    ),
    (
        ("research", "findings"),
        "research",
        "Research Findings",
        [
            ("Research Approach", ["Combine stakeholder interviews with workflow observation", "Compare stated needs with actual adoption barriers"]),
            ("What We Learned", ["Trust and speed matter more than novelty", "Reviewability determines whether teams delegate work"]),
            (
                "Evidence Snapshot",
                ["Adopters value clear artifacts and escalation paths", "Skeptics focus on data exposure and error recovery"],
            ),
            ("Implications", ["Invest in controls, traceability, and training", "Evaluate agents on complete work products"]),
        ],
    ),
    (
        ("board",),
        "corporate",
        "Board Update",
        [
            ("Company Health", ["Frame progress against the annual plan", "Separate wins, misses, and leading indicators"]),
            ("Execution Progress", ["Report product, customer, and team milestones", "Show where delivery risk is concentrated"]),
            ("Financial Posture", ["Connect spend to strategic priorities", "Explain runway, hiring, and efficiency tradeoffs"]),
            ("Board Decisions", ["Identify approvals or guidance needed", "Clarify consequences of delaying decisions"]),
        ],
    ),
    (
        ("onboarding", "training"),
        "minimal",
        "Onboarding Training",
        [
            ("Operating Model", ["Explain the platform's role in daily work", "Define human review and accountability"]),
            ("Core Workflow", ["Move from goal to plan to verified artifact", "Use checkpoints before publishing outputs"]),
            ("Escalation Paths", ["Recognize security, quality, and ambiguity triggers", "Route issues to the right owner quickly"]),
            ("Knowledge Check", ["Apply the process to realistic scenarios", "Confirm readiness with practical examples"]),
        ],
    ),
    (
        ("sales enablement", "account executives"),
        "pitch",
        "Sales Enablement",
        [
            ("Buyer Context", ["Enterprise operations leaders need throughput and control", "Buying groups include security, finance, and end users"]),
            ("Positioning", ["Lead with completed work, not model novelty", "Tie differentiation to observability and governance"]),
            ("Proof Points", ["Use benchmarks, pilots, and artifact examples", "Translate technical controls into buyer outcomes"]),
            ("Objection Handling", ["Address security, change management, and ROI", "Offer pilots with clear success criteria"]),
        ],
    ),
    (
        ("architecture", "technical"),
        "research",
        "Architecture Review",
        [
            ("System Overview", ["Separate gateway, execution, skill, and storage layers", "Make boundaries explicit"]),
            ("Data Movement", ["Trace prompts, artifacts, events, and logs", "Minimize host exposure and privilege"]),
            ("Trust and Controls", ["Enforce sandboxing, budgets, and audit trails", "Design reversible operations by default"]),
            ("Scaling Concerns", ["Plan for parallel workloads and failure recovery", "Track cost, latency, and queue health"]),
        ],
    ),
    (
        ("go-to-market", "launch plan", "launch"),
        "corporate",
        "Launch Plan",
        [
            ("Audience Strategy", ["Prioritize builders, evaluators, and executive sponsors", "Tailor messages by adoption barrier"]),
            ("Message and Channels", ["Explain why the release changes evaluation quality", "Coordinate docs, demos, email, and community posts"]),
            ("Milestone Plan", ["Stage readiness, release, monitoring, and follow-up", "Define owners for each launch motion"]),
            ("Success Metrics", ["Track adoption, completion rate, and quality feedback", "Prepare fallback and rollback communication"]),
            ("Contingencies", ["Handle quality regressions and confused users", "Keep launch decisions visible"]),
        ],
    ),
    (
        ("strategy", "strategic"),
        "corporate",
        "Executive Strategy",
        [
            ("Market Context", ["Automation is shifting from assistance to ownership", "Trust remains the constraint on delegation"]),
            ("Strategic Bets", ["Win on secure execution and high-quality artifacts", "Differentiate with evaluation, memory, and observability"]),
            ("Operating Principles", ["Prefer measurable workflows over demos", "Make governance a product feature"]),
            ("Investment Tradeoffs", ["Balance speed, reliability, and cost", "Choose where to build versus integrate"]),
            ("Leadership Decisions", ["Set success metrics and funding levels", "Resolve sequencing and ownership questions"]),
        ],
    ),
]


def workspace_path(payload: dict[str, Any], filename: str) -> Path:
    explicit = payload.get("output_dir")
    if explicit:
        out_dir = Path(str(explicit))
    else:
        task = str(payload.get("task") or payload.get("session_id") or "default").strip("/") or "default"
        out_dir = Path("/workspace") / task
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / filename


def _set_background(slide: Any, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_footer(slide: Any, template: str, slide_number: int, style: dict[str, RGBColor]) -> None:
    box = slide.shapes.add_textbox(Inches(0.35), Inches(7.05), Inches(12.6), Inches(0.25))
    frame = box.text_frame
    frame.text = f"{template.title()} • {slide_number}"
    para = frame.paragraphs[0]
    para.font.size = Pt(8)
    para.font.color.rgb = style["accent"]


def _write_title(shape: Any, text: str, style: dict[str, RGBColor], size: int = 34) -> None:
    shape.text = text
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(size)
            run.font.bold = True
            run.font.color.rgb = style["fg"]


def _write_bullets(shape: Any, bullets: list[Any], style: dict[str, RGBColor]) -> None:
    tf = shape.text_frame
    tf.clear()
    for idx, bullet in enumerate(bullets):
        paragraph = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        paragraph.text = str(bullet)
        paragraph.level = 0
        paragraph.font.size = Pt(20)
        paragraph.font.color.rgb = style["fg"]


def _image_path(ref: str, tmp_dir: Path) -> Path:
    if ref.startswith(("http://", "https://")):
        target = tmp_dir / (Path(ref.split("?", 1)[0]).name or "image")
        with urllib.request.urlopen(ref, timeout=15) as response:  # noqa: S310 - user-provided skill input
            target.write_bytes(response.read())
        return target
    return Path(ref)


def _add_images(slide: Any, refs: list[Any], tmp_dir: Path) -> None:
    x = Inches(8.2)
    y = Inches(1.55)
    for index, ref in enumerate(refs[:2]):
        path = _image_path(str(ref), tmp_dir)
        if path.exists():
            slide.shapes.add_picture(str(path), x, y + Inches(index * 2.4), width=Inches(4.4))


def _chart_image(chart: dict[str, Any], tmp_dir: Path) -> Path:
    labels = [str(item) for item in chart.get("labels", [])]
    values = [float(item) for item in chart.get("values", [])]
    kind = str(chart.get("type") or "bar")
    title = str(chart.get("title") or "")
    fig, ax = plt.subplots(figsize=(5, 3), dpi=160)
    if kind == "line":
        ax.plot(labels, values, marker="o")
    elif kind == "pie":
        ax.pie(values, labels=labels, autopct="%1.0f%%")
    else:
        ax.bar(labels, values)
    ax.set_title(title)
    if kind != "pie":
        ax.tick_params(axis="x", rotation=25)
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    target = tmp_dir / "chart.png"
    fig.savefig(target, transparent=False)
    plt.close(fig)
    return target


def _add_notes(slide: Any, notes: str) -> None:
    if not notes:
        return
    notes_slide = getattr(slide, "notes_slide", None)
    if notes_slide is not None:
        text_frame = notes_slide.notes_text_frame
        text_frame.text = notes
        return
    box = slide.shapes.add_textbox(Inches(0.35), Inches(6.72), Inches(12.4), Inches(0.25))
    box.name = "Speaker Notes"
    box.text_frame.text = f"Notes: {notes}"
    box.text_frame.paragraphs[0].font.size = Pt(7)


def _outline_from_prompt(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = str(payload.get("prompt") or "").casefold()
    for keywords, template, title, sections in DECK_PLANS:
        if any(keyword in prompt for keyword in keywords):
            payload.setdefault("template", template)
            return {
                "title": title,
                "subtitle": "Generated from an open-ended productivity benchmark prompt",
                "sections": [
                    {"title": section_title, "bullets": bullets, "notes": f"Discuss {section_title.lower()} in context."}
                    for section_title, bullets in sections
                ],
            }
    payload.setdefault("template", "minimal")
    return {
        "title": "Presentation",
        "subtitle": "Generated from an open-ended productivity benchmark prompt",
        "sections": [
            {"title": "Context", "bullets": ["Clarify the audience and purpose", "Summarize the situation"]},
            {"title": "Analysis", "bullets": ["Identify key considerations", "Compare practical options"]},
            {"title": "Recommendation", "bullets": ["Propose the path forward", "Name success measures"]},
            {"title": "Next Steps", "bullets": ["Assign owners", "Set review cadence"]},
        ],
    }


def create_presentation(payload: dict[str, Any]) -> Path:
    template = str(payload.get("template") or "minimal").lower()
    style = TEMPLATES.get(template, TEMPLATES["minimal"])
    outline = payload.get("outline") or payload
    if not outline.get("sections"):
        outline = _outline_from_prompt(payload)
        template = str(payload.get("template") or template).lower()
        style = TEMPLATES.get(template, TEMPLATES["minimal"])
    sections = list(outline.get("sections") or [])
    title = str(outline.get("title") or payload.get("title") or "Presentation")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        title_slide = prs.slides.add_slide(prs.slide_layouts[6])
        _set_background(title_slide, style["bg"])
        title_box = title_slide.shapes.add_textbox(Inches(0.8), Inches(2.25), Inches(11.8), Inches(1.1))
        _write_title(title_box, title, style, 44)
        subtitle = str(outline.get("subtitle") or "Generated by Mantle Slides")
        box = title_slide.shapes.add_textbox(Inches(0.85), Inches(3.45), Inches(10.8), Inches(0.6))
        box.text_frame.text = subtitle
        box.text_frame.paragraphs[0].font.size = Pt(20)
        box.text_frame.paragraphs[0].font.color.rgb = style["accent"]
        _add_footer(title_slide, template, 1, style)
        _add_notes(title_slide, str(outline.get("notes") or "Introduce the deck purpose and agenda."))

        for idx, section in enumerate(sections, start=2):
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            _set_background(slide, style["bg"])
            section_title = str(section.get("title") or f"Section {idx - 1}")
            section_box = slide.shapes.add_textbox(Inches(0.55), Inches(0.45), Inches(12.1), Inches(0.7))
            _write_title(section_box, section_title, style, 30)
            bullets = list(section.get("bullets") or section.get("items") or [])
            bullets_box = slide.shapes.add_textbox(Inches(0.85), Inches(1.45), Inches(7.0), Inches(4.9))
            _write_bullets(bullets_box, bullets, style)
            if section.get("images"):
                _add_images(slide, list(section.get("images") or []), tmp_dir)
            if section.get("chart"):
                chart_path = _chart_image(dict(section.get("chart") or {}), tmp_dir)
                slide.shapes.add_picture(str(chart_path), Inches(8.1), Inches(1.5), width=Inches(4.5))
            _add_footer(slide, template, idx, style)
            _add_notes(slide, str(section.get("notes") or ""))

        output = workspace_path(payload, "slides.pptx")
        prs.save(output)
        return output


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    output = create_presentation(payload)
    print(
        json.dumps(
            {
                "path": str(output),
                "template": payload.get("template", "minimal"),
                "slide_count": len(Presentation(output).slides),
            }
        )
    )


if __name__ == "__main__":
    main()
