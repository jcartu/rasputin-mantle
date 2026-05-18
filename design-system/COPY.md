# Voice & Tone Guide — Rasputin Mantle

How we write text in the product. Every user-facing string follows these rules.

---

## Core Principles

1. **Sentence case for headings.** Not Title Case. Not ALL CAPS. Sentence case.
2. **Active voice.** "The agent clicked the button" not "The button was clicked by the agent."
3. **No "Magical AI" language.** We're a tool. Write like Linear or Vercel writes copy.
4. **Error messages name the cause and the next step.** Not "Something went wrong."
5. **Empty states are useful, not coy.** Tell the user what to do.
6. **Loading messages describe what's happening** if it takes >2s.

---

## Do / Don't

### Headings

| Do | Don't |
|---|---|
| Task completed | Task Successfully Completed! 🎉 |
| Create a new task | Create A Brand New Task |
| Session replay | Session Replay Experience |
| Recent tasks | Your Recently Created Tasks |

### Buttons & Actions

| Do | Don't |
|---|---|
| Start task | Launch your magical journey |
| Run again | Supercharge this task |
| Copy link | Share the magic |
| Cancel | Abort mission |
| Try free task | Experience the power of AI |

### Error Messages

| Do | Don't |
|---|---|
| API key invalid. Check your Anthropic key in Settings. | Something went wrong. Please try again. |
| Sandbox timed out after 30 minutes. The task may have hung. | An unexpected error occurred. |
| No browser sessions available. Start a task first. | Oops! Something broke. |
| Rate limit exceeded. Try again in 2 minutes. | Whoops! You went too fast. |

### Empty States

| Do | Don't |
|---|---|
| No tasks yet. Create one to get started. | Your tasks will appear here ✨ |
| No files in this session. Files appear as the agent works. | It's quiet in here... |
| No recent sessions. | Nothing to see here yet! |

### Loading Messages

| Do | Don't |
|---|---|
| Starting sandbox... | Loading... |
| Agent is reading the page | Thinking... |
| Writing report (3 of 7 sections) | Working magic... |
| Connecting to browser | Preparing your experience... |

---

## Forbidden Words

These words never appear in user-facing text:

- magical / magic
- powerful AI
- supercharge
- next-gen / next generation
- revolutionary
- unlock the power of
- AI-powered (as adjective)
- intelligent (as marketing adjective)
- smart (as marketing adjective)
- seamless
- effortless
- game-changing
- cutting-edge
- state-of-the-art
- transformative
- paradigm-shifting

---

## Numerics

- **Thousand separators:** 1,234 (comma, not space or period)
- **Decimal precision:** 2 decimal places for costs ($12.34), 1 for percentages (78.3%)
- **Large numbers:** Abbreviate at 1M+ (1.2M, 3.4B)
- **Zero costs:** "$0.00" not "Free"
- **Durations:** "3 minutes" not "3 mins" or "3m" in prose. "3m" acceptable in dense UI (pills, tables).

---

## Time Formatting

- **Recent events (< 24h):** Relative — "3 minutes ago", "2 hours ago"
- **Older events:** Absolute — "May 17, 2026"
- **Today's events:** "Today at 2:34 PM"
- **Duration of tasks:** "12 minutes" in prose, "12m" in dense UI
- **ETA:** "About 5 minutes" (always approximate, never precise)

---

## Landing Page Copy Rules

The landing page is where the brand lands. No marketing speak.

- **Hero tagline:** Under 8 words. Specific. No adjectives.
- **Sub-headline:** Under 20 words. Explains what it does.
- **CTA:** Action verb + noun. "Try a task" not "Get started."
- **Feature descriptions:** Under 12 words each. Lead with the benefit, not the feature.
- **Honest gaps:** List what we don't do. Be specific. This builds trust.

---

## Onboarding Copy Rules

- **Step titles:** Under 6 words. Imperative.
- **Step descriptions:** Under 20 words. Explain why, not what.
- **Option labels:** Noun phrase. "Research" not "Do research tasks."
- **Error during onboarding:** Name the problem + offer a workaround.

---

## Chat Narration

The agent's chat narration is system-generated but follows tone rules:

- **Tool calls:** "[Click] Sign up button" — bracketed action + target
- **Reasoning:** Italic, muted. "The page loaded a login form. I'll enter the credentials."
- **File touches:** "[Write] report.md (+5 lines)" — action + file + diff stat
- **Screenshots:** Inline thumbnail, no caption needed
- **Errors:** Red accent. "Failed to click: element not found. Retrying with selector..."
- **Completion:** Green. "Task complete. Report saved to report.md."
