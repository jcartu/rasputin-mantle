import { Skeleton } from '@/components/ui/skeleton';

export default function SkeletonVisualTest() {
  return (
    <div className="p-8 space-y-8" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <div id="skeleton-block">
        <Skeleton variant="block" height={64} />
      </div>
      <div id="skeleton-circle">
        <Skeleton variant="circle" size={48} />
      </div>
      <div id="skeleton-text">
        <Skeleton variant="text" lines={3} />
      </div>
    </div>
  );
}
