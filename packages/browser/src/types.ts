export interface BrowserElement {
  id: string;
  role: string;
  text?: string;
  attributes?: Record<string, string>;
}

export interface BrowserState {
  url: string;
  elements: BrowserElement[];
}

export interface BrowserBackend {
  open(url: string): Promise<void>;
  getState(): Promise<BrowserState>;
  click(elementId: string): Promise<void>;
  type(elementId: string, text: string): Promise<void>;
  evaluate(script: string): Promise<unknown>;
  close(): Promise<void>;
}
