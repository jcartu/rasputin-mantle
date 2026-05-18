import { Button } from '@/components/ui/button';

export default function ButtonVisualTest() {
  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div id="variants" style={{ display: 'flex', gap: '10px' }}>
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="destructive">Destructive</Button>
        <Button variant="link">Link</Button>
      </div>
      
      <div id="sizes" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <Button size="xs">Extra Small</Button>
        <Button size="sm">Small</Button>
        <Button size="md">Medium</Button>
        <Button size="lg">Large</Button>
      </div>
      
      <div id="icons" style={{ display: 'flex', gap: '10px' }}>
        <Button iconLeft={<span>←</span>}>Left Icon</Button>
        <Button iconRight={<span>→</span>}>Right Icon</Button>
        <Button iconOnly={<span>★</span>} aria-label="Star" />
      </div>
      
      <div id="states" style={{ display: 'flex', gap: '10px' }}>
        <Button disabled>Disabled</Button>
        <Button loading>Loading</Button>
      </div>
    </div>
  );
}
