"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Check, AlertTriangle, AlertCircle, Info, ChevronDown, X,
  Search, Settings, Moon, Sun, Loader2
} from "lucide-react";
import "../../../../design-system/tokens.css";

/* ─────────────────────────────────────────────
   MAIN PAGE
───────────────────────────────────────────── */
export default function DesignSystemPage() {
  const [isLight, setIsLight] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      setIsLight(true);
    }
  }, []);

  if (!mounted) return null;

  const sections = [
    "Color", "Typography", "Spacing", "Borders & Radii", "Elevation",
    "Motion", "Iconography", "Button", "Input", "Textarea",
    "Badge", "Card", "Avatar", "Switch", "Spinner", "Skeleton", "Tab", "Toast", "Tooltip"
  ];

  return (
    <div className={isLight ? "light" : ""} style={{
      backgroundColor: 'var(--color-background)',
      color: 'var(--color-foreground)',
      minHeight: '100vh',
      display: 'flex',
      fontFamily: 'var(--font-sans)',
    }}>
      {/* Sidebar */}
      <aside style={{
        width: '240px', flexShrink: 0,
        borderRight: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-background-elevated)',
        height: '100vh', position: 'sticky', top: 0,
        overflowY: 'auto', display: 'flex', flexDirection: 'column',
      }}>
        <div style={{
          padding: 'var(--spacing-6)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <h1 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-weight-semibold)', margin: 0 }}>
            Mantle v1.2
          </h1>
          <button onClick={() => setIsLight(!isLight)} aria-label="Toggle theme" style={{
            background: 'transparent', border: 'none',
            color: 'var(--color-foreground-muted)', cursor: 'pointer',
            display: 'flex', padding: 'var(--spacing-1)', borderRadius: 'var(--radius-sm)',
          }}>
            {isLight ? <Moon size={16} /> : <Sun size={16} />}
          </button>
        </div>
        <nav style={{ padding: 'var(--spacing-4)', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-1)' }}>
          {sections.map(s => (
            <a key={s} href={`#${s.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`} style={{
              color: 'var(--color-foreground-muted)', textDecoration: 'none',
              fontSize: 'var(--text-sm)', padding: 'var(--spacing-2) var(--spacing-3)',
              borderRadius: 'var(--radius-sm)', display: 'block',
              transition: 'all 0.2s ease',
            }}
              onMouseEnter={e => { e.currentTarget.style.backgroundColor = 'var(--color-background-subtle)'; e.currentTarget.style.color = 'var(--color-foreground)'; }}
              onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = 'var(--color-foreground-muted)'; }}
            >{s}</a>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main style={{
        flex: 1, padding: 'var(--spacing-12) var(--spacing-16)',
        overflowY: 'auto', display: 'flex', flexDirection: 'column',
        gap: 'var(--spacing-16)', maxWidth: '1200px',
      }}>
        <header style={{ marginBottom: 'var(--spacing-8)' }}>
          <h1 style={{ fontSize: 'var(--text-4xl)', fontWeight: 'var(--font-weight-semibold)', marginBottom: 'var(--spacing-4)', marginTop: 0 }}>
            Design System Reference
          </h1>
          <p style={{ fontSize: 'var(--text-lg)', color: 'var(--color-foreground-muted)', margin: 0, maxWidth: '600px', lineHeight: 1.5 }}>
            Canonical reference for Rasputin Mantle v1.2. Every primitive in every state, rendered live.
          </p>
        </header>

        <ColorSection />
        <TypographySection />
        <SpacingSection />
        <BordersRadiiSection />
        <ElevationSection />
        <MotionSection />
        <IconographySection />
        <ButtonSection />
        <InputSection />
        <TextareaSection />
        <BadgeSection />
        <CardSection />
        <AvatarSection />
        <SwitchSection />
        <SpinnerSection />
        <SkeletonSection />
        <TabSection />
        <ToastSection />
        <TooltipSection />
      </main>
    </div>
  );
}

/* ─────────────────────────────────────────────
   SECTIONS
───────────────────────────────────────────── */

function ColorSection() {
  const tokens = [
    { name: "Background", token: "--color-background" },
    { name: "Background Elevated", token: "--color-background-elevated" },
    { name: "Background Subtle", token: "--color-background-subtle" },
    { name: "Foreground", token: "--color-foreground" },
    { name: "Foreground Muted", token: "--color-foreground-muted" },
    { name: "Foreground Faint", token: "--color-foreground-faint" },
    { name: "Muted", token: "--color-muted" },
    { name: "Accent", token: "--color-accent" },
    { name: "Accent Hover", token: "--color-accent-hover" },
    { name: "Accent Subtle", token: "--color-accent-subtle" },
    { name: "Success", token: "--color-success" },
    { name: "Success Subtle", token: "--color-success-subtle" },
    { name: "Warning", token: "--color-warning" },
    { name: "Warning Subtle", token: "--color-warning-subtle" },
    { name: "Destructive", token: "--color-destructive" },
    { name: "Destructive Subtle", token: "--color-destructive-subtle" },
    { name: "Border", token: "--color-border" },
    { name: "Border Strong", token: "--color-border-strong" },
  ];
  return (
    <section id="color">
      <SectionHeader title="Color" description="Semantic roles mapped to 6 hues. Dark mode is default, light mode is a deliberate inversion." />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 'var(--spacing-6)' }}>
        {tokens.map(t => <ColorSwatch key={t.token} name={t.name} token={t.token} />)}
      </div>
    </section>
  );
}

function TypographySection() {
  const specimens = [
    { token: "--text-display", name: "Display", weight: "--font-weight-bold" },
    { token: "--text-5xl", name: "5XL (Hero)", weight: "--font-weight-bold" },
    { token: "--text-4xl", name: "4XL (H1)", weight: "--font-weight-semibold" },
    { token: "--text-3xl", name: "3XL (H2)", weight: "--font-weight-semibold" },
    { token: "--text-2xl", name: "2XL (H3)", weight: "--font-weight-semibold" },
    { token: "--text-xl", name: "XL (H4)", weight: "--font-weight-medium" },
    { token: "--text-lg", name: "LG (H5)", weight: "--font-weight-medium", color: "var(--color-foreground-muted)" },
    { token: "--text-base", name: "Base (Body)", weight: "--font-weight-regular" },
    { token: "--text-sm", name: "SM (Dense)", weight: "--font-weight-regular" },
    { token: "--text-xs", name: "XS (Caption)", weight: "--font-weight-regular", color: "var(--color-foreground-muted)" },
    { token: "--text-sm", name: "Code Inline", weight: "--font-weight-regular", color: "var(--color-accent)", font: "var(--font-mono)" },
  ];
  return (
    <section id="typography">
      <SectionHeader title="Typography" description="10 sizes from xs to display. Geist Sans for UI, IBM Plex Mono for code." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-8)' }}>
        {specimens.map(s => <TypeSpecimen key={s.name} {...s} />)}
      </div>
    </section>
  );
}

function SpacingSection() {
  const items = [
    { token: "--spacing-0", value: "0px" }, { token: "--spacing-1", value: "4px" },
    { token: "--spacing-2", value: "8px" }, { token: "--spacing-3", value: "12px" },
    { token: "--spacing-4", value: "16px" }, { token: "--spacing-5", value: "20px" },
    { token: "--spacing-6", value: "24px" }, { token: "--spacing-8", value: "32px" },
    { token: "--spacing-10", value: "40px" }, { token: "--spacing-12", value: "48px" },
    { token: "--spacing-16", value: "64px" }, { token: "--spacing-20", value: "80px" },
    { token: "--spacing-24", value: "96px" },
  ];
  return (
    <section id="spacing">
      <SectionHeader title="Spacing" description="4px base grid. Every spacing value is a multiple of 4." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-4)' }}>
        {items.map(i => <SpacingBar key={i.token} {...i} />)}
      </div>
    </section>
  );
}

function BordersRadiiSection() {
  const radii = [
    { label: "none", radius: "var(--radius-none)" },
    { label: "sm", radius: "var(--radius-sm)" },
    { label: "md", radius: "var(--radius-md)" },
    { label: "lg", radius: "var(--radius-lg)" },
    { label: "xl", radius: "var(--radius-xl)" },
    { label: "full", radius: "var(--radius-full)" },
  ];
  return (
    <section id="borders--radii">
      <SectionHeader title="Borders & Radii" description="Radius scale from none to full. Default: md (6px)." />
      <div style={{ display: 'flex', gap: 'var(--spacing-4)', alignItems: 'end' }}>
        {radii.map(r => (
          <div key={r.label} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--spacing-2)' }}>
            <div style={{ width: '48px', height: '48px', backgroundColor: 'var(--color-accent-subtle)', border: '1px solid var(--color-accent)', borderRadius: r.radius }} />
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-foreground-muted)' }}>{r.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ElevationSection() {
  return (
    <section id="elevation">
      <SectionHeader title="Elevation" description="Dark mode uses background elevation. Light mode uses shadows." />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 'var(--spacing-6)' }}>
        {[
          { bg: 'var(--color-background-elevated)', label: "Elevated 1", desc: "Cards, panels" },
          { bg: 'var(--color-background-subtle)', label: "Elevated 2", desc: "Dialogs, dropdowns" },
          { bg: 'var(--color-muted)', label: "Elevated 3", desc: "Modals, sheets" },
        ].map(e => (
          <div key={e.label} style={{ padding: 'var(--spacing-6)', borderRadius: 'var(--radius-md)', backgroundColor: e.bg, border: '1px solid var(--color-border)' }}>
            <div style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)' }}>{e.label}</div>
            <div style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>{e.desc}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function MotionSection() {
  return (
    <section id="motion">
      <SectionHeader title="Motion" description="Easing functions and duration scale. See MOTION.md for full cookbook." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-6)' }}>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Duration scale</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-3)' }}>
            <MotionBar label="Fast (150ms)" duration="150ms" />
            <MotionBar label="Default (200ms)" duration="200ms" />
            <MotionBar label="Slow (300ms)" duration="300ms" />
            <MotionBar label="Ceremonial (500ms)" duration="500ms" />
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Easing curves</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-3)' }}>
            <MotionBar label="Default (Linear)" easing="cubic-bezier(0.16, 1, 0.3, 1)" />
            <MotionBar label="Enter (ease-out)" easing="cubic-bezier(0, 0, 0.2, 1)" />
            <MotionBar label="Exit (ease-in)" easing="cubic-bezier(0.4, 0, 1, 1)" />
            <MotionBar label="Spring (overshoot)" easing="cubic-bezier(0.34, 1.56, 0.64, 1)" />
          </div>
        </div>
      </div>
    </section>
  );
}

function IconographySection() {
  return (
    <section id="iconography">
      <SectionHeader title="Iconography" description="Lucide React, stroke mode only. Sizes: 14px (dense), 16px (chrome), 20px (actions)." />
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
        {[14, 16, 20, 24].map(s => (
          <div key={s} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--spacing-2)' }}>
            <Settings size={s} strokeWidth={s >= 20 ? 2 : 1.5} style={{ color: 'var(--color-foreground-muted)' }} />
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-foreground-muted)' }}>{s}px</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ButtonSection() {
  return (
    <section id="button">
      <SectionHeader title="Button" description="5 variants, 4 sizes, 3 icon modes, loading state." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-8)' }}>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-4)' }}>Variants</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
            <Button variant="primary">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="link">Link</Button>
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-4)' }}>Sizes</h3>
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
            <Button size="xs">XS</Button>
            <Button size="sm">SM</Button>
            <Button size="md">MD</Button>
            <Button size="lg">LG</Button>
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-4)' }}>Icon Modes</h3>
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
            <Button iconLeft={<Check size={16} />}>Icon Left</Button>
            <Button iconRight={<ChevronDown size={16} />}>Icon Right</Button>
            <Button iconOnly={<Search size={16} />} aria-label="Search" />
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-4)' }}>States</h3>
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
            <Button disabled>Disabled</Button>
            <Button loading>Loading</Button>
          </div>
        </div>
      </div>
    </section>
  );
}

function InputSection() {
  return (
    <section id="input">
      <SectionHeader title="Input" description="Text input field with states: default, hover, focus, error, disabled, with-icon, with-hint." />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
        <Input label="Default" placeholder="Enter text..." />
        <Input label="Error" placeholder="Invalid input" error="This field is required" />
        <Input label="Disabled" placeholder="Cannot edit" disabled />
        <Input label="With icon" placeholder="Search..." leadingIcon={<Search size={16} />} />
        <Input label="With hint" placeholder="Enter email" hint="We will never share your email" />
      </div>
    </section>
  );
}

function TextareaSection() {
  return (
    <section id="textarea">
      <SectionHeader title="Textarea" description="Multi-line text input. Auto-grow from 80px to 240px." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-4)', maxWidth: '480px' }}>
        <TextArea label="Default" placeholder="Enter a longer message..." />
        <TextArea label="With character count" placeholder="Start typing..." charCount={42} maxChars={200} />
      </div>
    </section>
  );
}

function BadgeSection() {
  return (
    <section id="badge">
      <SectionHeader title="Badge" description="Small status indicator. Variants: default, success, warn, error, outline." />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-3)' }}>
        <Badge variant="default">Default</Badge>
        <Badge variant="success">Success</Badge>
        <Badge variant="warn">Warning</Badge>
        <Badge variant="error">Error</Badge>
        <Badge variant="outline">Outline</Badge>
      </div>
    </section>
  );
}

function CardSection() {
  return (
    <section id="card">
      <SectionHeader title="Card" description="Container with header/body/footer slots. Hover state." />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--spacing-6)' }}>
        <Card>
          <CardHeader>Card Title</CardHeader>
          <CardBody>Cards use background elevation in dark mode and subtle shadows in light mode. Hover to see border change.</CardBody>
          <CardFooter><Button size="sm">Action</Button></CardFooter>
        </Card>
      </div>
    </section>
  );
}

function AvatarSection() {
  return (
    <section id="avatar">
      <SectionHeader title="Avatar" description="Image with fallback initials. Sizes: xs through xl. Status dot overlay." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-8)' }}>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Sizes</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
            {(['xs', 'sm', 'md', 'lg', 'xl'] as const).map(s => <Avatar key={s} initials="AB" size={s} />)}
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Status</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
            <Avatar initials="ON" size="md" status="online" />
            <Avatar initials="AW" size="md" status="away" />
            <Avatar initials="BU" size="md" status="busy" />
            <Avatar initials="OF" size="md" status="offline" />
          </div>
        </div>
      </div>
    </section>
  );
}

function SwitchSection() {
  return (
    <section id="switch">
      <SectionHeader title="Switch" description="Controlled toggle. Sizes: sm, md." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
          <Switch size="md" label="Medium (off)" defaultChecked={false} />
          <Switch size="md" label="Medium (on)" defaultChecked={true} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
          <Switch size="sm" label="Small (off)" defaultChecked={false} />
          <Switch size="sm" label="Small (on)" defaultChecked={true} />
          <Switch size="sm" label="Disabled" defaultChecked={false} disabled />
        </div>
      </div>
    </section>
  );
}

function SpinnerSection() {
  return (
    <section id="spinner">
      <SectionHeader title="Spinner" description="Loading indicator. Determinate and indeterminate variants." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-8)' }}>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Indeterminate</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
            {(['xs', 'sm', 'md', 'lg', 'xl'] as const).map(s => <Spinner key={s} size={s} />)}
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Determinate</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-6)' }}>
            {[25, 50, 75, 100].map(p => <Spinner key={p} size="md" determinate={p} />)}
          </div>
        </div>
      </div>
    </section>
  );
}

function SkeletonSection() {
  return (
    <section id="skeleton">
      <SectionHeader title="Skeleton" description="Loading placeholder. Block, circle, text-line variants." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-8)' }}>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Text lines</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)', maxWidth: '400px' }}>
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="80%" />
            <Skeleton variant="text" width="60%" />
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Block</h3>
          <Skeleton variant="block" width="300px" height="120px" />
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Circle</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
            <Skeleton variant="circle" size="32px" />
            <Skeleton variant="circle" size="40px" />
            <Skeleton variant="circle" size="48px" />
          </div>
        </div>
      </div>
    </section>
  );
}

function TabSection() {
  return (
    <section id="tab">
      <SectionHeader title="Tab" description="Horizontal tab navigation with animated indicator." />
      <TabGroup items={["Overview", "Settings", "Activity", "Members", "Advanced"]} />
    </section>
  );
}

function ToastSection() {
  return (
    <section id="toast">
      <SectionHeader title="Toast" description="Notification variants: info, success, warn, error." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-4)', maxWidth: '420px' }}>
        <ToastPreview variant="info" title="Task started" description="Your agent is now working on the task." />
        <ToastPreview variant="success" title="Task complete" description="Report saved to report.md." />
        <ToastPreview variant="warn" title="Rate limit approaching" description="You have 2 tasks remaining today." />
        <ToastPreview variant="error" title="Connection lost" description="Failed to connect to sandbox." />
      </div>
    </section>
  );
}

function TooltipSection() {
  return (
    <section id="tooltip">
      <SectionHeader title="Tooltip" description="Text with optional shortcut keys. Smart positioning." />
      <div style={{ display: 'flex', gap: 'var(--spacing-6)', alignItems: 'center' }}>
        <TooltipContent text="Toggle theme" shortcut="Cmd+T" />
        <TooltipContent text="Open command palette" shortcut="Cmd+K" />
        <TooltipContent text="This is a longer tooltip that wraps to multiple lines when needed" />
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   SHARED HELPERS
───────────────────────────────────────────── */

function SectionHeader({ title, description }: { title: string; description: string }) {
  return (
    <div style={{ marginBottom: 'var(--spacing-6)' }}>
      <h2 style={{ font: 'var(--font-weight-semibold) var(--text-2xl) var(--font-sans)', margin: '0 0 var(--spacing-2) 0', paddingBottom: 'var(--spacing-4)', borderBottom: '1px solid var(--color-border)' }}>{title}</h2>
      <p style={{ font: 'var(--font-weight-regular) var(--text-base) var(--font-sans)', color: 'var(--color-foreground-muted)', margin: 0 }}>{description}</p>
    </div>
  );
}

function ColorSwatch({ name, token }: { name: string; token: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-3)', padding: 'var(--spacing-4)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-background-elevated)' }}>
      <div style={{ height: '64px', borderRadius: 'var(--radius-sm)', backgroundColor: `var(${token})`, border: '1px solid var(--color-border)' }} />
      <div>
        <div style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)' }}>{name}</div>
        <div style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-mono)', color: 'var(--color-foreground-muted)' }}>{token}</div>
      </div>
    </div>
  );
}

function TypeSpecimen({ token, name, weight, color = 'var(--color-foreground)', font = 'var(--font-sans)' }: { token: string; name: string; weight: string; color?: string; font?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--spacing-6)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--spacing-4)' }}>
      <div style={{ width: '120px', flexShrink: 0 }}>
        <div style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)' }}>{name}</div>
        <div style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-mono)', color: 'var(--color-foreground-muted)' }}>{token}</div>
      </div>
      <div style={{ font: `var(${weight}) var(${token}) ${font}`, color }}>
        The quick brown fox jumps over the lazy dog
      </div>
    </div>
  );
}

function SpacingBar({ token, value }: { token: string; value: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-6)' }}>
      <div style={{ width: '120px', flexShrink: 0 }}>
        <div style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)' }}>{token.replace('--spacing-', 'space-')}</div>
        <div style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-mono)', color: 'var(--color-foreground-muted)' }}>{value}</div>
      </div>
      <div style={{ height: '24px', width: `var(${token})`, backgroundColor: 'var(--color-accent-subtle)', border: '1px solid var(--color-accent)', borderRadius: 'var(--radius-sm)' }} />
    </div>
  );
}

/* ── Button ── */
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive' | 'link';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  iconLeft?: React.ReactNode; iconRight?: React.ReactNode; iconOnly?: React.ReactNode;
  loading?: boolean;
};

function Button({ variant = 'primary', size = 'md', iconLeft, iconRight, iconOnly, loading, children, disabled, ...props }: ButtonProps) {
  const [hovered, setHovered] = useState(false);
  const [active, setActive] = useState(false);
  const [focused, setFocused] = useState(false);

  const sizes: Record<string, React.CSSProperties> = {
    xs: { height: '24px', padding: iconOnly ? '0' : '0 8px', fontSize: 'var(--text-xs)', width: iconOnly ? '24px' : 'auto' },
    sm: { height: '28px', padding: iconOnly ? '0' : '0 10px', fontSize: 'var(--text-sm)', width: iconOnly ? '28px' : 'auto' },
    md: { height: '32px', padding: iconOnly ? '0' : '0 14px', fontSize: 'var(--text-sm)', width: iconOnly ? '32px' : 'auto' },
    lg: { height: '40px', padding: iconOnly ? '0' : '0 20px', fontSize: 'var(--text-base)', width: iconOnly ? '40px' : 'auto' },
  };

  const variants: Record<string, () => React.CSSProperties> = {
    primary: () => ({ backgroundColor: hovered ? 'var(--color-accent-hover)' : 'var(--color-accent)', color: 'var(--color-background)' }),
    secondary: () => ({ backgroundColor: hovered ? 'var(--color-muted)' : 'var(--color-background-subtle)', color: 'var(--color-foreground)', border: hovered ? '1px solid var(--color-border-strong)' : '1px solid var(--color-border)' }),
    ghost: () => ({ backgroundColor: hovered ? 'var(--color-background-subtle)' : 'transparent', color: hovered ? 'var(--color-foreground)' : 'var(--color-foreground-muted)' }),
    destructive: () => ({ backgroundColor: hovered ? 'var(--color-destructive-subtle)' : 'var(--color-destructive)', color: '#FFFFFF' }),
    link: () => ({ backgroundColor: 'transparent', color: hovered ? 'var(--color-accent-hover)' : 'var(--color-accent)', textDecoration: hovered ? 'underline' : 'none' }),
  };

  return (
    <button style={{
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-1)',
      borderRadius: 'var(--radius-md)', fontFamily: 'var(--font-sans)', fontWeight: 'var(--font-weight-semibold)',
      transition: 'all var(--duration-default) var(--ease-default)',
      cursor: disabled || loading ? 'not-allowed' : 'pointer',
      opacity: disabled || loading ? 0.5 : 1, pointerEvents: disabled || loading ? 'none' : 'auto',
      transform: active && !disabled && !loading ? 'scale(0.98)' : 'scale(1)',
      outline: 'none',
      boxShadow: focused ? '0 0 0 2px var(--color-background), 0 0 0 4px var(--color-accent)' : 'none',
      border: 'none', textDecoration: 'none',
      ...sizes[size], ...variants[variant](),
    }}
      onMouseEnter={() => setHovered(true)} onMouseLeave={() => { setHovered(false); setActive(false); }}
      onMouseDown={() => setActive(true)} onMouseUp={() => setActive(false)}
      onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
      disabled={disabled || loading} {...props}
    >
      {loading ? <Loader2 size={size === 'xs' || size === 'sm' ? 14 : 16} style={{ animation: 'spin 1s linear infinite' }} /> :
        iconOnly ? iconOnly : <>{iconLeft}{children}{iconRight}</>}
    </button>
  );
}

/* ── Input ── */
function Input({ label, placeholder, error, hint, disabled, leadingIcon, trailingIcon }: { label?: string; placeholder?: string; error?: string; hint?: string; disabled?: boolean; leadingIcon?: React.ReactNode; trailingIcon?: React.ReactNode }) {
  const [hovered, setHovered] = useState(false);
  const [focused, setFocused] = useState(false);
  const borderColor = error ? 'var(--color-destructive)' : focused ? 'var(--color-accent)' : hovered ? 'var(--color-border-strong)' : 'var(--color-border)';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-1)', minWidth: '200px', flex: '1 1 200px' }}>
      {label && <label style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>{label}</label>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)', height: '32px', padding: '0 var(--spacing-2)', borderRadius: 'var(--radius-md)', border: `${focused ? '2px' : '1px'} solid ${borderColor}`, backgroundColor: disabled ? 'var(--color-muted)' : 'var(--color-background)', transition: 'all var(--duration-default) var(--ease-default)' }}>
        {leadingIcon && <span style={{ color: 'var(--color-foreground-muted)', display: 'flex' }}>{leadingIcon}</span>}
        <input placeholder={placeholder} disabled={disabled} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
          onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
          style={{ flex: 1, border: 'none', outline: 'none', backgroundColor: 'transparent', color: disabled ? 'var(--color-foreground-faint)' : 'var(--color-foreground)', fontFamily: 'var(--font-sans)', fontSize: 'var(--text-sm)', cursor: disabled ? 'not-allowed' : 'text' }} />
        {trailingIcon && <span style={{ color: 'var(--color-foreground-muted)', display: 'flex' }}>{trailingIcon}</span>}
      </div>
      {error && <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-1)', font: 'var(--font-weight-regular) var(--text-xs) var(--font-sans)', color: 'var(--color-destructive)' }}><AlertCircle size={14} /> {error}</div>}
      {hint && !error && <div style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-sans)', color: 'var(--color-foreground-faint)' }}>{hint}</div>}
    </div>
  );
}

/* ── TextArea ── */
function TextArea({ label, placeholder, charCount, maxChars }: { label?: string; placeholder?: string; charCount?: number; maxChars?: number }) {
  const [focused, setFocused] = useState(false);
  const [hovered, setHovered] = useState(false);
  const borderColor = focused ? 'var(--color-accent)' : hovered ? 'var(--color-border-strong)' : 'var(--color-border)';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-1)' }}>
      {label && <label style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>{label}</label>}
      <div style={{ position: 'relative' }}>
        <textarea placeholder={placeholder} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
          onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
          style={{ width: '100%', minHeight: '80px', maxHeight: '240px', padding: 'var(--spacing-2)', borderRadius: 'var(--radius-md)', border: `1px solid ${borderColor}`, backgroundColor: 'var(--color-background)', color: 'var(--color-foreground)', fontFamily: 'var(--font-sans)', fontSize: 'var(--text-sm)', outline: 'none', resize: 'vertical', transition: 'all var(--duration-default) var(--ease-default)', boxSizing: 'border-box' }} />
        {maxChars && <div style={{ position: 'absolute', bottom: 'var(--spacing-2)', right: 'var(--spacing-2)', font: 'var(--font-weight-regular) var(--text-xs) var(--font-mono)', color: 'var(--color-foreground-faint)' }}>{charCount || 0}/{maxChars}</div>}
      </div>
    </div>
  );
}

/* ── Badge ── */
function Badge({ variant = 'default', children }: { variant?: 'default' | 'success' | 'warn' | 'error' | 'outline'; children: React.ReactNode }) {
  const c: Record<string, { bg: string; text: string; border: string }> = {
    default: { bg: 'var(--color-muted)', text: 'var(--color-foreground-muted)', border: 'transparent' },
    success: { bg: 'var(--color-success-subtle)', text: 'var(--color-success)', border: 'transparent' },
    warn: { bg: 'var(--color-warning-subtle)', text: 'var(--color-warning)', border: 'transparent' },
    error: { bg: 'var(--color-destructive-subtle)', text: 'var(--color-destructive)', border: 'transparent' },
    outline: { bg: 'transparent', text: 'var(--color-accent)', border: 'var(--color-accent)' },
  };
  const v = c[variant];
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', height: '22px', padding: '2px 8px', borderRadius: 'var(--radius-full)', backgroundColor: v.bg, color: v.text, border: variant === 'outline' ? '1px solid ' + v.border : 'none', font: 'var(--font-weight-semibold) var(--text-xs) var(--font-sans)' }}>{children}</span>
  );
}

/* ── Card ── */
function Card({ children }: { children: React.ReactNode }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      style={{ backgroundColor: 'var(--color-background-elevated)', border: `1px solid ${hovered ? 'var(--color-border-strong)' : 'var(--color-border)'}`, borderRadius: 'var(--radius-md)', overflow: 'hidden', transition: 'border-color var(--duration-default) var(--ease-default)' }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >{children}</div>
  );
}
function CardHeader({ children }: { children: React.ReactNode }) {
  return <div style={{ padding: 'var(--spacing-4)', borderBottom: '1px solid var(--color-border)', font: 'var(--font-weight-semibold) var(--text-base) var(--font-sans)' }}>{children}</div>;
}
function CardBody({ children }: { children: React.ReactNode }) {
  return <div style={{ padding: 'var(--spacing-4)', font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)', lineHeight: 1.6 }}>{children}</div>;
}
function CardFooter({ children }: { children: React.ReactNode }) {
  return <div style={{ padding: 'var(--spacing-4)', borderTop: '1px solid var(--color-border)', display: 'flex', justifyContent: 'flex-end' }}>{children}</div>;
}

/* ── Avatar ── */
function Avatar({ initials = '?', size = 'md', status }: { initials?: string; size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'; status?: 'online' | 'away' | 'busy' | 'offline' }) {
  const s: Record<string, { d: string; fs: string }> = { xs: { d: '20px', fs: '8px' }, sm: { d: '24px', fs: '10px' }, md: { d: '32px', fs: '12px' }, lg: { d: '40px', fs: '14px' }, xl: { d: '48px', fs: '16px' } };
  const sc: Record<string, string> = { online: 'var(--color-success)', away: 'var(--color-warning)', busy: 'var(--color-destructive)', offline: 'var(--color-foreground-faint)' };
  return (
    <div style={{ position: 'relative', display: 'inline-flex' }}>
      <div style={{ width: s[size].d, height: s[size].d, borderRadius: 'var(--radius-full)', backgroundColor: 'var(--color-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `var(--font-weight-semibold) ${s[size].fs} var(--font-sans)`, color: 'var(--color-foreground-muted)', overflow: 'hidden', flexShrink: 0 }}>{initials.slice(0, 2).toUpperCase()}</div>
      {status && <div style={{ position: 'absolute', bottom: '-2px', right: '-2px', width: '8px', height: '8px', borderRadius: 'var(--radius-full)', backgroundColor: sc[status], border: '2px solid var(--color-background)' }} />}
    </div>
  );
}

/* ── Switch ── */
function Switch({ size = 'md', label, defaultChecked = false, disabled }: { size?: 'sm' | 'md'; label?: string; defaultChecked?: boolean; disabled?: boolean }) {
  const [checked, setChecked] = useState(defaultChecked);
  const d = size === 'md' ? { tw: '40px', th: '22px', tb: '16px' } : { tw: '32px', th: '18px', tb: '12px' };
  const tx = checked ? `calc(${d.tw} - ${d.tb} - 4px)` : '4px';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
      <div role="switch" aria-checked={checked} tabIndex={disabled ? -1 : 0}
        onClick={() => !disabled && setChecked(!checked)}
        onKeyDown={e => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); !disabled && setChecked(!checked); } }}
        style={{ width: d.tw, height: d.th, borderRadius: 'var(--radius-full)', backgroundColor: checked ? 'var(--color-accent)' : 'var(--color-muted)', cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.5 : 1, transition: 'background-color var(--duration-default) var(--ease-default)', position: 'relative', flexShrink: 0 }}>
        <div style={{ width: d.tb, height: d.tb, borderRadius: 'var(--radius-full)', backgroundColor: '#FFFFFF', position: 'absolute', top: `calc((${d.th} - ${d.tb}) / 2)`, left: tx, transition: 'left var(--duration-default) var(--ease-default)' }} />
      </div>
      {label && <span style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>{label}</span>}
    </div>
  );
}

/* ── Spinner ── */
function Spinner({ size = 'md', determinate }: { size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'; determinate?: number }) {
  const dim = ({ xs: 16, sm: 20, md: 24, lg: 32, xl: 40 } as const)[size];
  const r = (dim - 2) / 2;
  const c = 2 * Math.PI * r;
  const off = determinate !== undefined ? c * (1 - determinate / 100) : undefined;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--spacing-1)' }}>
      <svg width={dim} height={dim} viewBox={`0 0 ${dim} ${dim}`}>
        <circle cx={dim / 2} cy={dim / 2} r={r} fill="none" stroke="var(--color-muted)" strokeWidth={2} />
        <circle cx={dim / 2} cy={dim / 2} r={r} fill="none" stroke="var(--color-accent)" strokeWidth={2}
          strokeDasharray={determinate ? c : `${c * 0.75} ${c * 0.25}`} strokeDashoffset={off} strokeLinecap="round"
          style={{ transformOrigin: 'center', transform: 'rotate(-90deg)', animation: determinate ? 'none' : 'spin 0.8s linear infinite', transition: determinate !== undefined ? 'stroke-dashoffset 0.3s ease' : 'none' }} />
      </svg>
      {determinate !== undefined && <span style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-mono)', color: 'var(--color-foreground-muted)' }}>{determinate}%</span>}
    </div>
  );
}

/* ── Skeleton ── */
function Skeleton({ variant = 'text', width, height, size }: { variant?: 'text' | 'block' | 'circle'; width?: string; height?: string; size?: string }) {
  return <div style={{ backgroundColor: 'var(--color-muted)', borderRadius: variant === 'circle' ? 'var(--radius-full)' : 'var(--radius-sm)', width: variant === 'circle' ? size : width, height: variant === 'circle' ? size : height, animation: 'shimmer 1.5s linear infinite' }} />;
}

/* ── TabGroup ── */
function TabGroup({ items }: { items: string[] }) {
  const [active, setActive] = useState(0);
  const [ind, setInd] = useState({ left: 0, width: 0 });
  const refs = useRef<HTMLDivElement[]>([]);
  useEffect(() => { if (refs.current[active]) { const el = refs.current[active]; setInd({ left: el.offsetLeft, width: el.offsetWidth }); } }, [active]);
  return (
    <div style={{ display: 'flex', borderBottom: '1px solid var(--color-border)', position: 'relative', overflowX: 'auto' }}>
      {items.map((item, i) => (
        <div key={item} ref={el => { if (el) refs.current[i] = el; }} onClick={() => setActive(i)}
          style={{ padding: 'var(--spacing-3) var(--spacing-4)', minWidth: '80px', textAlign: 'center', cursor: 'pointer',
            font: `${i === active ? 'var(--font-weight-semibold)' : 'var(--font-weight-medium)'} var(--text-sm) var(--font-sans)`,
            color: i === active ? 'var(--color-foreground)' : 'var(--color-foreground-muted)',
            transition: 'color var(--duration-default) var(--ease-default)', userSelect: 'none', }}
          onMouseEnter={e => { if (i !== active) e.currentTarget.style.color = 'var(--color-foreground)'; }}
          onMouseLeave={e => { if (i !== active) e.currentTarget.style.color = 'var(--color-foreground-muted)'; }}
        >{item}</div>
      ))}
      <div style={{ position: 'absolute', bottom: 0, left: ind.left, width: ind.width, height: '2px', backgroundColor: 'var(--color-accent)', transition: 'left 0.2s var(--ease-default), width 0.2s var(--ease-default)' }} />
    </div>
  );
}

/* ── ToastPreview ── */
function ToastPreview({ variant, title, description }: { variant: 'info' | 'success' | 'warn' | 'error'; title: string; description: string }) {
  const icons: Record<string, React.ReactNode> = { info: <Info size={16} />, success: <Check size={16} />, warn: <AlertTriangle size={16} />, error: <AlertCircle size={16} /> };
  const bc: Record<string, string> = { info: 'var(--color-accent)', success: 'var(--color-success)', warn: 'var(--color-warning)', error: 'var(--color-destructive)' };
  return (
    <div style={{ maxWidth: '420px', backgroundColor: 'var(--color-background-elevated)', border: '1px solid var(--color-border)', borderLeft: `3px solid ${bc[variant]}`, borderRadius: 'var(--radius-md)', padding: 'var(--spacing-3) var(--spacing-4)', display: 'flex', gap: 'var(--spacing-3)', alignItems: 'flex-start', boxShadow: 'var(--shadow-xl)' }}>
      <span style={{ color: bc[variant], display: 'flex', marginTop: '2px', flexShrink: 0 }}>{icons[variant]}</span>
      <div style={{ flex: 1 }}>
        <div style={{ font: 'var(--font-weight-semibold) var(--text-sm) var(--font-sans)', marginBottom: '2px' }}>{title}</div>
        <div style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)', lineHeight: 1.4 }}>{description}</div>
      </div>
      <X size={14} style={{ color: 'var(--color-foreground-faint)', cursor: 'pointer', flexShrink: 0 }} />
    </div>
  );
}

/* ── TooltipContent ── */
function TooltipContent({ text, shortcut }: { text: string; shortcut?: string }) {
  const [show, setShow] = useState(false);
  return (
    <div style={{ position: 'relative', display: 'inline-flex' }}>
      <div onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}
        style={{ padding: 'var(--spacing-2) var(--spacing-3)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', cursor: 'pointer', font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>
        Hover me
      </div>
      {show && (
        <div style={{ position: 'absolute', bottom: 'calc(100% + 8px)', left: '50%', transform: 'translateX(-50%)', backgroundColor: 'var(--color-foreground)', color: 'var(--color-background)', padding: '6px 10px', borderRadius: 'var(--radius-sm)', whiteSpace: 'nowrap', zIndex: 10, display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
          <span style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-sans)' }}>{text}</span>
          {shortcut && <kbd style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-mono)', padding: '1px 4px', borderRadius: '3px', backgroundColor: 'var(--color-muted)', color: 'var(--color-foreground-muted)' }}>{shortcut}</kbd>}
        </div>
      )}
    </div>
  );
}

/* ── MotionBar ── */
function MotionBar({ label, duration = '200ms', easing = 'var(--ease-default)' }: { label: string; duration?: string; easing?: string }) {
  const [key, setKey] = useState(0);
  useEffect(() => { const iv = setInterval(() => setKey(k => k + 1), parseInt(duration) + 300); return () => clearInterval(iv); }, [duration]);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
      <div style={{ width: '160px', flexShrink: 0 }}>
        <span style={{ font: 'var(--font-weight-regular) var(--text-xs) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>{label}</span>
      </div>
      <div style={{ flex: 1, height: '24px', backgroundColor: 'var(--color-muted)', borderRadius: 'var(--radius-sm)', overflow: 'hidden', position: 'relative' }}>
        <div key={key} style={{ width: '40px', height: '100%', backgroundColor: 'var(--color-accent)', borderRadius: 'var(--radius-sm)', animation: `mbar${key} ${duration} ${easing}` }} />
        <style>{`@keyframes mbar${key} { from { transform: translateX(0); } to { transform: translateX(calc(100% + 200px)); } }`}</style>
      </div>
    </div>
  );
}
