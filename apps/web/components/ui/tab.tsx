import * as React from 'react';

export interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  defaultValue?: string;
  value?: string;
  onValueChange?: (value: string) => void;
  orientation?: 'horizontal' | 'vertical';
}

const TabsContext = React.createContext<{
  value?: string;
  onValueChange: (value: string) => void;
  orientation: 'horizontal' | 'vertical';
} | null>(null);

export const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
  ({ defaultValue, value, onValueChange, orientation = 'horizontal', className, ...props }, ref) => {
    const [uncontrolledValue, setUncontrolledValue] = React.useState(defaultValue);
    const isControlled = value !== undefined;
    const currentValue = isControlled ? value : uncontrolledValue;

    const handleValueChange = React.useCallback(
      (newValue: string) => {
        if (!isControlled) {
          setUncontrolledValue(newValue);
        }
        onValueChange?.(newValue);
      },
      [isControlled, onValueChange]
    );

    return (
      <TabsContext.Provider value={{ value: currentValue, onValueChange: handleValueChange, orientation }}>
        <div
          ref={ref}
          data-orientation={orientation}
          style={{
            display: 'flex',
            flexDirection: orientation === 'horizontal' ? 'column' : 'row',
          }}
          className={className}
          {...props}
        />
      </TabsContext.Provider>
    );
  }
);
Tabs.displayName = 'Tabs';

export interface TabListProps extends React.HTMLAttributes<HTMLDivElement> {}

export const TabList = React.forwardRef<HTMLDivElement, TabListProps>(
  ({ className, children, ...props }, ref) => {
    const context = React.useContext(TabsContext);
    if (!context) throw new Error('TabList must be used within Tabs');

    const listRef = React.useRef<HTMLDivElement>(null);
    const [indicatorStyle, setIndicatorStyle] = React.useState<React.CSSProperties>({});

    const mergedRef = (node: HTMLDivElement) => {
      if (typeof ref === 'function') ref(node);
      else if (ref) (ref as React.MutableRefObject<HTMLDivElement | null>).current = node;
      listRef.current = node;
    };

    const updateIndicator = React.useCallback(() => {
      if (!listRef.current) return;
      const activeTab = listRef.current.querySelector('[role="tab"][aria-selected="true"]') as HTMLElement;
      if (!activeTab) {
        setIndicatorStyle({ opacity: 0 });
        return;
      }

      if (context.orientation === 'horizontal') {
        setIndicatorStyle({
          left: activeTab.offsetLeft,
          width: activeTab.offsetWidth,
          bottom: 0,
          height: '2px',
          opacity: 1,
        });
      } else {
        setIndicatorStyle({
          top: activeTab.offsetTop,
          height: activeTab.offsetHeight,
          left: 0,
          width: '2px',
          opacity: 1,
        });
      }
    }, [context.orientation]);

    React.useEffect(() => {
      updateIndicator();
      window.addEventListener('resize', updateIndicator);
      return () => window.removeEventListener('resize', updateIndicator);
    }, [context.value, updateIndicator]);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (!listRef.current) return;
      const triggers = Array.from(listRef.current.querySelectorAll('[role="tab"]:not([disabled])')) as HTMLElement[];
      const currentIndex = triggers.findIndex((t) => t === document.activeElement);
      if (currentIndex === -1) return;

      let nextIndex = currentIndex;
      if (context.orientation === 'horizontal') {
        if (e.key === 'ArrowRight') nextIndex = (currentIndex + 1) % triggers.length;
        if (e.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + triggers.length) % triggers.length;
      } else {
        if (e.key === 'ArrowDown') nextIndex = (currentIndex + 1) % triggers.length;
        if (e.key === 'ArrowUp') nextIndex = (currentIndex - 1 + triggers.length) % triggers.length;
      }

      if (nextIndex !== currentIndex) {
        e.preventDefault();
        triggers[nextIndex].focus();
      }
    };

    return (
      <div
        ref={mergedRef}
        role="tablist"
        aria-orientation={context.orientation}
        onKeyDown={handleKeyDown}
        style={{
          display: 'flex',
          flexDirection: context.orientation === 'horizontal' ? 'row' : 'column',
          flexWrap: context.orientation === 'horizontal' ? 'nowrap' : undefined,
          overflowX: context.orientation === 'horizontal' ? 'auto' : undefined,
          position: 'relative',
        }}
        className={className}
        {...props}
      >
        {children}
        <div
          style={{
            position: 'absolute',
            backgroundColor: 'var(--color-accent)',
            transition: 'all var(--duration-default) var(--ease-default)',
            pointerEvents: 'none',
            ...indicatorStyle,
          }}
        />
      </div>
    );
  }
);
TabList.displayName = 'TabList';

export interface TabTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string;
}

export const TabTrigger = React.forwardRef<HTMLButtonElement, TabTriggerProps>(
  ({ value, className, disabled, ...props }, ref) => {
    const context = React.useContext(TabsContext);
    if (!context) throw new Error('TabTrigger must be used within Tabs');

    const isSelected = context.value === value;

    return (
      <button
        ref={ref}
        role="tab"
        type="button"
        aria-selected={isSelected}
        disabled={disabled}
        tabIndex={isSelected ? 0 : -1}
        onClick={() => {
          if (!disabled) context.onValueChange(value);
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (!disabled) context.onValueChange(value);
          }
        }}
        style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: context.orientation === 'horizontal' ? 'center' : 'flex-start',
          minWidth: context.orientation === 'horizontal' ? '80px' : undefined,
          padding: context.orientation === 'horizontal' ? '12px 16px' : '8px 16px',
          fontSize: 'var(--text-sm)',
          fontWeight: 'var(--font-weight-semibold)',
          color: isSelected ? 'var(--color-foreground)' : disabled ? 'var(--color-foreground-faint)' : 'var(--color-foreground-muted)',
          cursor: disabled ? 'not-allowed' : 'pointer',
          background: 'transparent',
          border: 'none',
          outline: 'none',
          textAlign: context.orientation === 'horizontal' ? 'center' : 'left',
          transition: 'color var(--duration-fast) var(--ease-default)',
        }}
        onMouseEnter={(e) => {
          if (!disabled && !isSelected) {
            e.currentTarget.style.color = 'var(--color-foreground)';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled && !isSelected) {
            e.currentTarget.style.color = 'var(--color-foreground-muted)';
          }
        }}
        className={className}
        {...props}
      />
    );
  }
);
TabTrigger.displayName = 'TabTrigger';

export interface TabContentProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
}

export const TabContent = React.forwardRef<HTMLDivElement, TabContentProps>(
  ({ value, className, ...props }, ref) => {
    const context = React.useContext(TabsContext);
    if (!context) throw new Error('TabContent must be used within Tabs');

    const isSelected = context.value === value;

    if (!isSelected) return null;

    return (
      <div
        ref={ref}
        role="tabpanel"
        tabIndex={0}
        style={{
          flexGrow: 1,
          outline: 'none',
        }}
        className={className}
        {...props}
      />
    );
  }
);
TabContent.displayName = 'TabContent';
