export {};

type MantleConfig = {
  gatewayUrl: string;
  bearerToken?: string;
  currentSessionId?: string;
};

type SessionEvent = {
  type?: string;
  status?: string;
  message?: string;
  content?: string;
};

const DEFAULT_GATEWAY_URL = "http://localhost:8000";
const statusElement = requiredElement("#status", HTMLElement);
const eventsElement = requiredElement("#events", HTMLElement);

let abortController: AbortController | undefined;

chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === "sync" && (changes.currentSessionId || changes.gatewayUrl || changes.bearerToken)) {
    void connect();
  }
});

void connect();

async function connect(): Promise<void> {
  abortController?.abort();
  abortController = new AbortController();
  eventsElement.replaceChildren();

  const config = await getConfig();
  statusElement.textContent = config.currentSessionId ? `Session ${config.currentSessionId}` : "No current session. Use the context menu or omnibox.";

  if (!config.currentSessionId) return;

  try {
    const streamUrl = `${config.gatewayUrl}/api/sessions/${encodeURIComponent(config.currentSessionId)}/events`;
    const response = await fetch(streamUrl, {
      headers: headers(config),
      signal: abortController.signal,
    });

    if (!response.ok || !response.body) {
      throw new Error(`Gateway returned ${response.status}`);
    }

    await readEventStream(response.body.getReader());
  } catch (error) {
    if (abortController.signal.aborted) return;
    statusElement.textContent = `Gateway stream unavailable: ${String(error)}`;
  }
}

async function readEventStream(reader: ReadableStreamDefaultReader<Uint8Array>): Promise<void> {
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let separatorIndex = buffer.indexOf("\n\n");
    while (separatorIndex >= 0) {
      const rawEvent = buffer.slice(0, separatorIndex);
      buffer = buffer.slice(separatorIndex + 2);
      renderRawEvent(rawEvent);
      separatorIndex = buffer.indexOf("\n\n");
    }
  }
}

function renderRawEvent(rawEvent: string): void {
  const dataLines = rawEvent
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice("data:".length).trim());

  if (dataLines.length === 0) return;

  const data = dataLines.join("\n");
  try {
    const parsed = JSON.parse(data) as SessionEvent;
    if (parsed.status) statusElement.textContent = `Status: ${parsed.status}`;
    appendEvent(parsed.message ?? parsed.content ?? JSON.stringify(parsed, null, 2));
  } catch {
    appendEvent(data);
  }
}

function appendEvent(content: string): void {
  const eventElement = document.createElement("article");
  eventElement.textContent = content;
  eventsElement.prepend(eventElement);
}

async function getConfig(): Promise<MantleConfig> {
  const values = await getStoredValues(["gatewayUrl", "bearerToken", "currentSessionId"]);
  return {
    gatewayUrl: (values.gatewayUrl ?? DEFAULT_GATEWAY_URL).replace(/\/+$/, ""),
    bearerToken: values.bearerToken?.trim() || undefined,
    currentSessionId: values.currentSessionId?.trim() || undefined,
  };
}

function headers(config: MantleConfig): HeadersInit {
  return config.bearerToken ? { Authorization: `Bearer ${config.bearerToken}` } : {};
}

function getStoredValues(keys: string[]): Promise<Record<string, string | undefined>> {
  return new Promise((resolve) => {
    chrome.storage.sync.get(keys, (items) => {
      const result: Record<string, string | undefined> = {};
      for (const key of keys) {
        const value = items[key];
        result[key] = typeof value === "string" ? value : undefined;
      }
      resolve(result);
    });
  });
}

function requiredElement<T extends Element>(selector: string, constructor: { new (): T }): T {
  const element = document.querySelector(selector);
  if (!element || !(element instanceof constructor)) {
    throw new Error(`Missing required element: ${selector}`);
  }
  return element;
}
