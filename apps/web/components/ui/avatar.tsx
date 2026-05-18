import * as React from 'react';

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  initials?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  status?: 'online' | 'away' | 'busy' | 'offline';
}

export const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ src, alt, initials, size = 'md', status, className, style, ...props }, ref) => {
    const [imageError, setImageError] = React.useState(false);

    let diameter = '32px';
    let fontSize = '12px';

    switch (size) {
      case 'xs':
        diameter = '20px';
        fontSize = '8px';
        break;
      case 'sm':
        diameter = '24px';
        fontSize = '10px';
        break;
      case 'lg':
        diameter = '40px';
        fontSize = '14px';
        break;
      case 'xl':
        diameter = '48px';
        fontSize = '16px';
        break;
      case 'md':
      default:
        diameter = '32px';
        fontSize = '12px';
        break;
    }

    let statusColor = '';
    switch (status) {
      case 'online':
        statusColor = 'var(--color-success)';
        break;
      case 'away':
        statusColor = 'var(--color-warning)';
        break;
      case 'busy':
        statusColor = 'var(--color-destructive)';
        break;
      case 'offline':
        statusColor = 'var(--color-foreground-faint)';
        break;
    }

    const displayInitials = initials ? initials.slice(0, 2).toUpperCase() : '';

    return (
      <div
        ref={ref}
        style={{
          position: 'relative',
          display: 'inline-flex',
          width: diameter,
          height: diameter,
          ...style,
        }}
        className={className}
        {...props}
      >
        <div
          style={{
            width: '100%',
            height: '100%',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-muted)',
            color: 'var(--color-foreground-muted)',
            fontWeight: 'var(--font-weight-semibold)',
            fontSize,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
          }}
        >
          {src && !imageError ? (
            <img
              src={src}
              alt={alt || ''}
              onError={() => setImageError(true)}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
          ) : (
            <span>{displayInitials}</span>
          )}
        </div>
        {status && (
          <span
            style={{
              position: 'absolute',
              bottom: 0,
              right: 0,
              width: '8px',
              height: '8px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: statusColor,
              border: '2px solid var(--color-background)',
              boxSizing: 'content-box',
              transform: 'translate(10%, 10%)',
            }}
          />
        )}
      </div>
    );
  }
);
Avatar.displayName = 'Avatar';
