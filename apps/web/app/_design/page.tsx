"use client";

import React, { useState, useEffect } from "react";
import {
  Check, AlertTriangle, AlertCircle, Info, ChevronDown, X,
  Search, Settings, Moon, Sun, Loader2
} from "lucide-react";
import "../../../../design-system/tokens.css";

import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardBody, CardFooter } from "@/components/ui/card";
import Dialog from "@/components/ui/dialog";
import Input from "@/components/ui/input";
import Select from "@/components/ui/select";
import Sheet from "@/components/ui/sheet";
import Skeleton from "@/components/ui/skeleton";
import Spinner from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabList, TabTrigger, TabContent } from "@/components/ui/tab";
import Textarea from "@/components/ui/textarea";
import ToastProvider, { useToast } from "@/components/ui/toast";
import Tooltip from "@/components/ui/tooltip";

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
    "Motion", "Iconography", "Button", "Input", "Textarea", "Select",
    "Badge", "Card", "Avatar", "Switch", "Spinner", "Skeleton", "Tab", "Dialog", "Sheet", "Toast", "Tooltip"
  ];

  return (
    <ToastProvider>
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
          <SelectSection />
          <BadgeSection />
          <CardSection />
          <AvatarSection />
          <SwitchSection />
          <SpinnerSection />
          <SkeletonSection />
          <TabSection />
          <DialogSection />
          <SheetSection />
          <ToastSection />
          <TooltipSection />
        </main>
      </div>
    </ToastProvider>
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
        <Textarea label="Default" placeholder="Enter a longer message..." />
        <Textarea label="With character count" placeholder="Start typing..." characterCount={42} maxLength={200} />
      </div>
    </section>
  );
}

function SelectSection() {
  const options = [
    { label: "Apple", value: "apple" },
    { label: "Banana", value: "banana" },
    { label: "Cherry", value: "cherry" },
  ];
  return (
    <section id="select">
      <SectionHeader title="Select" description="Dropdown selection. Default, multi-select, searchable." />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
        <div style={{ width: '200px' }}>
          <Select options={options} placeholder="Select fruit" />
        </div>
        <div style={{ width: '200px' }}>
          <Select options={options} placeholder="Multi-select" multiple />
        </div>
        <div style={{ width: '200px' }}>
          <Select options={options} placeholder="Searchable" searchable />
        </div>
      </div>
    </section>
  );
}

function DialogSection() {
  const [openSm, setOpenSm] = useState(false);
  const [openMd, setOpenMd] = useState(false);
  const [openLg, setOpenLg] = useState(false);
  const [openFull, setOpenFull] = useState(false);

  return (
    <section id="dialog">
      <SectionHeader title="Dialog" description="Modal window. Sizes: sm, md, lg, full." />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
        <Button onClick={() => setOpenSm(true)}>Open SM</Button>
        <Dialog isOpen={openSm} onClose={() => setOpenSm(false)} title="Small Dialog" size="sm">
          <p>This is a small dialog.</p>
        </Dialog>

        <Button onClick={() => setOpenMd(true)}>Open MD</Button>
        <Dialog isOpen={openMd} onClose={() => setOpenMd(false)} title="Medium Dialog" size="md">
          <p>This is a medium dialog.</p>
        </Dialog>

        <Button onClick={() => setOpenLg(true)}>Open LG</Button>
        <Dialog isOpen={openLg} onClose={() => setOpenLg(false)} title="Large Dialog" size="lg">
          <p>This is a large dialog.</p>
        </Dialog>

        <Button onClick={() => setOpenFull(true)}>Open Full</Button>
        <Dialog isOpen={openFull} onClose={() => setOpenFull(false)} title="Full Dialog" size="full">
          <p>This is a full screen dialog.</p>
        </Dialog>
      </div>
    </section>
  );
}

function SheetSection() {
  const [openLeft, setOpenLeft] = useState(false);
  const [openRight, setOpenRight] = useState(false);
  const [openTop, setOpenTop] = useState(false);
  const [openBottom, setOpenBottom] = useState(false);

  return (
    <section id="sheet">
      <SectionHeader title="Sheet" description="Slide-out panel. Sides: left, right, top, bottom." />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
        <Button onClick={() => setOpenLeft(true)}>Left Sheet</Button>
        <Sheet isOpen={openLeft} onClose={() => setOpenLeft(false)} side="left">
          <div style={{ padding: 'var(--spacing-4)' }}>Left Sheet Content</div>
        </Sheet>

        <Button onClick={() => setOpenRight(true)}>Right Sheet</Button>
        <Sheet isOpen={openRight} onClose={() => setOpenRight(false)} side="right">
          <div style={{ padding: 'var(--spacing-4)' }}>Right Sheet Content</div>
        </Sheet>

        <Button onClick={() => setOpenTop(true)}>Top Sheet</Button>
        <Sheet isOpen={openTop} onClose={() => setOpenTop(false)} side="top">
          <div style={{ padding: 'var(--spacing-4)' }}>Top Sheet Content</div>
        </Sheet>

        <Button onClick={() => setOpenBottom(true)}>Bottom Sheet</Button>
        <Sheet isOpen={openBottom} onClose={() => setOpenBottom(false)} side="bottom">
          <div style={{ padding: 'var(--spacing-4)' }}>Bottom Sheet Content</div>
        </Sheet>
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
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-3)', marginTop: 'var(--spacing-4)' }}>
        <Badge size="sm">Small</Badge>
        <Badge size="md">Medium</Badge>
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
          <Switch size="md" defaultChecked={false} />
          <span style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>Medium (off)</span>
          <Switch size="md" defaultChecked={true} />
          <span style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>Medium (on)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
          <Switch size="sm" defaultChecked={false} />
          <span style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>Small (off)</span>
          <Switch size="sm" defaultChecked={true} />
          <span style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>Small (on)</span>
          <Switch size="sm" defaultChecked={false} disabled />
          <span style={{ font: 'var(--font-weight-regular) var(--text-sm) var(--font-sans)', color: 'var(--color-foreground-muted)' }}>Disabled</span>
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
            {(['xs', 'sm', 'md', 'lg', 'xl'] as const).map(s => <Spinner key={s} size={s} variant="indeterminate" />)}
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Determinate</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-6)' }}>
            {[25, 50, 75, 100].map(p => <Spinner key={p} size="md" variant="determinate" progress={p} />)}
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
            <Skeleton variant="text" lines={3} />
          </div>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Block</h3>
          <Skeleton variant="block" style={{ width: '300px', height: '120px' }} />
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Circle</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
            <Skeleton variant="circle" size={32} />
            <Skeleton variant="circle" size={40} />
            <Skeleton variant="circle" size={48} />
          </div>
        </div>
      </div>
    </section>
  );
}

function TabSection() {
  return (
    <section id="tab">
      <SectionHeader title="Tab" description="Horizontal and vertical tab navigation." />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-8)' }}>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Horizontal</h3>
          <Tabs defaultValue="overview" orientation="horizontal">
            <TabList>
              <TabTrigger value="overview">Overview</TabTrigger>
              <TabTrigger value="settings">Settings</TabTrigger>
              <TabTrigger value="activity">Activity</TabTrigger>
            </TabList>
            <TabContent value="overview" style={{ padding: 'var(--spacing-4)' }}>Overview Content</TabContent>
            <TabContent value="settings" style={{ padding: 'var(--spacing-4)' }}>Settings Content</TabContent>
            <TabContent value="activity" style={{ padding: 'var(--spacing-4)' }}>Activity Content</TabContent>
          </Tabs>
        </div>
        <div>
          <h3 style={{ font: 'var(--font-weight-medium) var(--text-sm) var(--font-sans)', marginBottom: 'var(--spacing-3)' }}>Vertical</h3>
          <Tabs defaultValue="overview" orientation="vertical">
            <TabList>
              <TabTrigger value="overview">Overview</TabTrigger>
              <TabTrigger value="settings">Settings</TabTrigger>
              <TabTrigger value="activity">Activity</TabTrigger>
            </TabList>
            <TabContent value="overview" style={{ padding: 'var(--spacing-4)' }}>Overview Content</TabContent>
            <TabContent value="settings" style={{ padding: 'var(--spacing-4)' }}>Settings Content</TabContent>
            <TabContent value="activity" style={{ padding: 'var(--spacing-4)' }}>Activity Content</TabContent>
          </Tabs>
        </div>
      </div>
    </section>
  );
}

function ToastSection() {
  const { addToast } = useToast();

  return (
    <section id="toast">
      <SectionHeader title="Toast" description="Notification variants: info, success, warn, error." />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
        <Button onClick={() => addToast({ title: 'Task started', description: 'Your agent is now working on the task.', variant: 'info' })}>Info Toast</Button>
        <Button onClick={() => addToast({ title: 'Task complete', description: 'Report saved to report.md.', variant: 'success' })}>Success Toast</Button>
        <Button onClick={() => addToast({ title: 'Rate limit approaching', description: 'You have 2 tasks remaining today.', variant: 'warn' })}>Warn Toast</Button>
        <Button onClick={() => addToast({ title: 'Connection lost', description: 'Failed to connect to sandbox.', variant: 'error' })}>Error Toast</Button>
      </div>
    </section>
  );
}

function TooltipSection() {
  return (
    <section id="tooltip">
      <SectionHeader title="Tooltip" description="Text with optional shortcut keys. Smart positioning." />
      <div style={{ display: 'flex', gap: 'var(--spacing-6)', alignItems: 'center' }}>
        <Tooltip content="Toggle theme" shortcuts={['Cmd', 'T']}>
          <Button variant="secondary">Hover me</Button>
        </Tooltip>
        <Tooltip content="Open command palette" shortcuts={['Cmd', 'K']}>
          <Button variant="secondary">Hover me</Button>
        </Tooltip>
        <Tooltip content="This is a longer tooltip that wraps to multiple lines when needed">
          <Button variant="secondary">Hover me</Button>
        </Tooltip>
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
