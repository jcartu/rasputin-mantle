import { Spinner } from '@/components/ui/spinner';

export default function SpinnerVisualTest() {
  return (
    <div className="p-8 space-y-8" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <div id="spinner-indeterminate" style={{ display: 'flex', gap: '16px' }}>
        <Spinner size="xs" />
        <Spinner size="sm" />
        <Spinner size="md" />
        <Spinner size="lg" />
        <Spinner size="xl" />
      </div>
      <div id="spinner-determinate" style={{ display: 'flex', gap: '16px' }}>
        <Spinner variant="determinate" progress={0} size="md" />
        <Spinner variant="determinate" progress={25} size="md" />
        <Spinner variant="determinate" progress={50} size="md" />
        <Spinner variant="determinate" progress={75} size="md" />
        <Spinner variant="determinate" progress={100} size="md" />
      </div>
    </div>
  );
}
