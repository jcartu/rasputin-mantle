# Motion Cookbook — Rasputin Mantle

Reusable framer-motion variants and Tailwind animation classes for common patterns.

---

## Framer-Motion Variants

### Entrance (fade + slight Y translate)

```tsx
export const entrance = {
  hidden: { opacity: 0, y: 8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2, ease: [0, 0, 0.2, 1] },
  },
};
```

**Reduced-motion:** `{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: { duration: 0 } } }`

### Exit (fade + slight Y translate, faster)

```tsx
export const exit = {
  hidden: { opacity: 0, y: 4 },
  visible: {
    opacity: 1,
    y: 0,
  },
  exit: {
    opacity: 0,
    y: 4,
    transition: { duration: 0.15, ease: [0.4, 0, 1, 1] },
  },
};
```

**Reduced-motion:** `{ exit: { opacity: 0, transition: { duration: 0 } } }`

### Modal In

```tsx
export const modalIn = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0, 0, 0.2, 1] },
  },
};
```

**Reduced-motion:** `{ hidden: { opacity: 0 }, visible: { opacity: 1, scale: 1, y: 0, transition: { duration: 0 } } }`

### Modal Out

```tsx
export const modalOut = {
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2, ease: [0.4, 0, 1, 1] },
  },
};
```

**Reduced-motion:** `{ exit: { opacity: 0, transition: { duration: 0 } } }`

### Sheet Slide-In (direction-aware)

```tsx
const directions = { left: -1, right: 1, top: -1, bottom: 1 };
const axes = { left: 'x', right: 'x', top: 'y', bottom: 'y' };

export function sheetIn(direction: 'left' | 'right' | 'top' | 'bottom') {
  const axis = axes[direction];
  return {
    hidden: { opacity: 0, [axis]: `${directions[direction] * 100}%` },
    visible: {
      opacity: 1,
      [axis]: 0,
      transition: { duration: 0.3, ease: [0, 0, 0.2, 1] },
    },
  };
}
```

**Reduced-motion:** `{ hidden: { opacity: 0 }, visible: { opacity: 1, x: 0, y: 0, transition: { duration: 0 } } }`

### Sheet Slide-Out

```tsx
export function sheetOut(direction: 'left' | 'right' | 'top' | 'bottom') {
  const axis = axes[direction];
  return {
    exit: {
      opacity: 0,
      [axis]: `${directions[direction] * 100}%`,
      transition: { duration: 0.2, ease: [0.4, 0, 1, 1] },
    },
  };
}
```

**Reduced-motion:** `{ exit: { opacity: 0, transition: { duration: 0 } } }`

### Tab Indicator Slide

```tsx
export const tabIndicator = {
  layout: {
    transition: {
      type: 'spring',
      stiffness: 500,
      damping: 35,
      duration: 0.2,
    },
  },
};
```

**Reduced-motion:** `{ layout: { transition: { duration: 0 } } }`

### Skeleton Shimmer

```tsx
export const shimmer = {
  animate: {
    opacity: [0.3, 0.6, 0.3],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};
```

**Reduced-motion:** `{ animate: { opacity: 0.3 } }` — static muted background.

### Toast In

```tsx
export const toastIn = {
  hidden: { opacity: 0, y: '100%' },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] },
  },
};
```

**Reduced-motion:** `{ hidden: { opacity: 0 }, visible: { opacity: 1, y: 0, transition: { duration: 0 } } }`

### Toast Out

```tsx
export const toastOut = {
  exit: {
    opacity: 0,
    y: '100%',
    transition: { duration: 0.2, ease: [0.4, 0, 1, 1] },
  },
};
```

**Reduced-motion:** `{ exit: { opacity: 0, transition: { duration: 0 } } }`

### Pulse (thinking states)

```tsx
export const pulse = {
  animate: {
    opacity: [0.4, 1, 0.4],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};
```

**Reduced-motion:** `{ animate: { opacity: 1 } }` — static accent dot.

### Panel Collapse/Expand

```tsx
export const panelCollapse = {
  collapsed: {
    width: 0,
    opacity: 0,
    overflow: 'hidden',
    transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] },
  },
  expanded: {
    width: 'var(--panel-width)',
    opacity: 1,
    transition: { duration: 0.2, ease: [0, 0, 0.2, 1] },
  },
};
```

**Reduced-motion:** `{ collapsed: { width: 0, opacity: 0, overflow: 'hidden', transition: { duration: 0 } }, expanded: { width: 'var(--panel-width)', opacity: 1, transition: { duration: 0 } } }`

---

## Tailwind Animation Classes

### Spinner Rotation

```css
@keyframes spin-accent {
  to { transform: rotate(360deg); }
}

.animate-spin-accent {
  animation: spin-accent 0.8s linear infinite;
}
```

### Skeleton Shimmer (CSS fallback)

```css
@keyframes shimmer {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.animate-shimmer {
  animation: shimmer 1.5s linear infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animate-shimmer {
    animation: none;
    opacity: 0.3;
  }
}
```

### Pulse Dot (CSS fallback)

```css
@keyframes pulse-dot {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

.animate-pulse-dot {
  animation: pulse-dot 2s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animate-pulse-dot {
    animation: none;
    opacity: 1;
  }
}
```

---

## Global Reduced-Motion Hook

```tsx
// apps/web/lib/use-reduced-motion.ts
import { useLayoutEffect } from 'react';

export function useReducedMotion(): boolean {
  let prefersReduced = false;
  useLayoutEffect(() => {
    const mql = window.matchMedia('(prefers-reduced-motion: reduce)');
    prefersReduced = mql.matches;
    const handler = (e: MediaQueryListEvent) => { prefersReduced = e.matches; };
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, []);
  return prefersReduced;
}
```

Use this hook in any component that needs to conditionally disable animations. Pass the result to framer-motion's `suppressHydrationWarning` or use it to swap variants.

---

## CSS Transition Defaults

For non-framer-motion transitions (hover states, focus rings, etc.):

```css
/* Default transition for all interactive elements */
.transition-default {
  transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

/* Fast transition for micro-interactions */
.transition-fast {
  transition: all 150ms cubic-bezier(0.16, 1, 0.3, 1);
}

/* Slow transition for panel/layout changes */
.transition-slow {
  transition: all 300ms cubic-bezier(0, 0, 0.2, 1);
}

@media (prefers-reduced-motion: reduce) {
  .transition-default,
  .transition-fast,
  .transition-slow {
    transition: none;
  }
}
```
