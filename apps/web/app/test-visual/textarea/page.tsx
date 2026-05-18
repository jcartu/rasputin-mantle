import { Textarea } from '@/components/ui/textarea';

export default function TextareaVisualTest() {
  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '400px' }}>
      <div id="default">
        <Textarea placeholder="Default textarea" />
      </div>
      
      <div id="with-label-hint">
        <Textarea label="Bio" hint="Tell us about yourself." placeholder="I am a software engineer..." />
      </div>
      
      <div id="error">
        <Textarea label="Description" error="Description is too short" defaultValue="Short" />
      </div>
      
      <div id="disabled">
        <Textarea label="Disabled" disabled placeholder="Cannot type here" />
      </div>
      
      <div id="with-char-count">
        <Textarea label="Message" maxLength={500} defaultValue="Hello world" />
      </div>
    </div>
  );
}
