import * as React from 'react';
import { createPortal } from 'react-dom';

type TriggerProps = {
  ref?: React.Ref<HTMLElement>;
  onMouseEnter?: (e: React.MouseEvent) => void;
  onMouseLeave?: (e: React.MouseEvent) => void;
  onFocus?: (e: React.FocusEvent) => void;
  onBlur?: (e: React.FocusEvent) => void;
};

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement<TriggerProps>;
  shortcuts?: string[];
  delay?: number;
}

export const Tooltip = ({
  content,
  children,
  shortcuts,
  delay = 250,
}: TooltipProps) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [position, setPosition] = React.useState<{ top: number; left: number; placement: 'top' | 'bottom' | 'left' | 'right' } | null>(null);
  const triggerRef = React.useRef<HTMLElement>(null);
  const tooltipRef = React.useRef<HTMLDivElement>(null);
  const timeoutRef = React.useRef<NodeJS.Timeout | null>(null);

  const updatePosition = React.useCallback(() => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const offset = 8;
    const arrowSize = 4;

    let placement: 'top' | 'bottom' | 'left' | 'right' = 'top';
    let top = triggerRect.top - tooltipRect.height - offset - arrowSize;
    let left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;

    // Collision detection
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Top collision
    if (top < 0) {
      placement = 'bottom';
      top = triggerRect.bottom + offset + arrowSize;
      
      // Bottom collision
      if (top + tooltipRect.height > viewportHeight) {
        // Try right
        placement = 'right';
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + offset + arrowSize;
        
        // Right collision
        if (left + tooltipRect.width > viewportWidth) {
          // Try left
          placement = 'left';
          left = triggerRect.left - tooltipRect.width - offset - arrowSize;
        }
      }
    }

    // Horizontal bounds check for top/bottom placement
    if (placement === 'top' || placement === 'bottom') {
      if (left < offset) {
        left = offset;
      } else if (left + tooltipRect.width > viewportWidth - offset) {
        left = viewportWidth - tooltipRect.width - offset;
      }
    }

    // Vertical bounds check for left/right placement
    if (placement === 'left' || placement === 'right') {
      if (top < offset) {
        top = offset;
      } else if (top + tooltipRect.height > viewportHeight - offset) {
        top = viewportHeight - tooltipRect.height - offset;
      }
    }

    setPosition({ top, left, placement });
  }, []);

  const handleMouseEnter = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
      // Need to wait for render to measure
      requestAnimationFrame(() => {
        updatePosition();
      });
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setIsVisible(false);
    setPosition(null);
  };

  const handleFocus = () => {
    handleMouseEnter();
  };

  const handleBlur = () => {
    handleMouseLeave();
  };

  React.useEffect(() => {
    if (isVisible) {
      window.addEventListener('scroll', updatePosition, true);
      window.addEventListener('resize', updatePosition);
      return () => {
        window.removeEventListener('scroll', updatePosition, true);
        window.removeEventListener('resize', updatePosition);
      };
    }
  }, [isVisible, updatePosition]);

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const childProps: TriggerProps = children.props;
  const trigger = React.cloneElement<TriggerProps>(children, {
    ref: (node: HTMLElement | null) => {
      const childRef = (children as React.ReactElement<TriggerProps> & { ref?: React.Ref<HTMLElement> }).ref;
      if (typeof childRef === 'function') {
        childRef(node);
      } else if (childRef && typeof childRef === 'object' && 'current' in childRef) {
        (childRef as React.MutableRefObject<HTMLElement | null>).current = node;
      }
      (triggerRef as React.MutableRefObject<HTMLElement | null>).current = node;
    },
    onMouseEnter: (e: React.MouseEvent) => {
      handleMouseEnter();
      childProps.onMouseEnter?.(e);
    },
    onMouseLeave: (e: React.MouseEvent) => {
      handleMouseLeave();
      childProps.onMouseLeave?.(e);
    },
    onFocus: (e: React.FocusEvent) => {
      handleFocus();
      childProps.onFocus?.(e);
    },
    onBlur: (e: React.FocusEvent) => {
      handleBlur();
      childProps.onBlur?.(e);
    },
  });

  return (
    <>
      {trigger}
      {isVisible &&
        typeof document !== 'undefined' &&
        createPortal(
          <div
            ref={tooltipRef}
            role="tooltip"
            style={{
              position: 'fixed',
              top: position?.top ?? -9999,
              left: position?.left ?? -9999,
              opacity: position ? 1 : 0,
              pointerEvents: 'none',
              zIndex: 50,
              backgroundColor: 'var(--color-foreground)',
              color: 'var(--color-background)',
              fontSize: 'var(--text-xs)',
              fontWeight: 'var(--font-weight-regular)',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              maxWidth: '240px',
              boxShadow: 'var(--shadow-md)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-2)',
              fontFamily: 'var(--font-sans)',
            }}
          >
            <span>{content}</span>
            {shortcuts && shortcuts.length > 0 && (
              <span style={{ display: 'flex', alignItems: 'center', gap: '2px', opacity: 0.8 }}>
                {shortcuts.map((key, i) => (
                  <React.Fragment key={i}>
                    <kbd
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: 'var(--text-xs)',
                      }}
                    >
                      {key}
                    </kbd>
                    {i < shortcuts.length - 1 && <span>+</span>}
                  </React.Fragment>
                ))}
              </span>
            )}
            {/* Arrow */}
            <div
              style={{
                position: 'absolute',
                width: 0,
                height: 0,
                borderStyle: 'solid',
                ...(position?.placement === 'top' && {
                  bottom: '-4px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  borderWidth: '4px 4px 0 4px',
                  borderColor: 'var(--color-foreground) transparent transparent transparent',
                }),
                ...(position?.placement === 'bottom' && {
                  top: '-4px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  borderWidth: '0 4px 4px 4px',
                  borderColor: 'transparent transparent var(--color-foreground) transparent',
                }),
                ...(position?.placement === 'left' && {
                  right: '-4px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  borderWidth: '4px 0 4px 4px',
                  borderColor: 'transparent transparent transparent var(--color-foreground)',
                }),
                ...(position?.placement === 'right' && {
                  left: '-4px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  borderWidth: '4px 4px 4px 0',
                  borderColor: 'transparent var(--color-foreground) transparent transparent',
                }),
              }}
            />
          </div>,
          document.body
        )}
    </>
  );
};

export default Tooltip;
