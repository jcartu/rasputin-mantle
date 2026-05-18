export {};

type IconState = "gray" | "teal" | "green";
type SessionStatus = "queued" | "running" | "done" | "failed" | "unknown";

type MantleConfig = {
  gatewayUrl: string;
  bearerToken?: string;
  currentSessionId?: string;
};

type SessionResponse = {
  id?: string;
  session_id?: string;
  status?: string;
  state?: string;
};

const DEFAULT_GATEWAY_URL = "http://localhost:8000";
const CONTEXT_MENU_ID = "send-to-mantle";
const POLL_INTERVAL_MS = 10_000;

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: CONTEXT_MENU_ID,
      title: "Send to Mantle",
      contexts: ["page", "selection", "link"],
    });
  });

  if (chrome.sidePanel?.setPanelBehavior) {
    void chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  }
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId !== CONTEXT_MENU_ID) return;
  void createSessionFromContext(info, tab);
});

chrome.omnibox.onInputStarted.addListener(() => {
  void setIconState("teal");
});

chrome.omnibox.onInputEntered.addListener((text) => {
  void createSession({
    task: text.trim(),
    source: "omnibox",
  });
});

chrome.runtime.onStartup.addListener(() => {
  void pollGateway();
});

chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName !== "sync") return;
  if (changes.currentSessionId || changes.gatewayUrl || changes.bearerToken) {
    void pollGateway();
  }
});

void setIconState("gray");
setInterval(() => {
  void pollGateway();
}, POLL_INTERVAL_MS);

async function createSessionFromContext(info: chrome.contextMenus.OnClickData, tab?: chrome.tabs.Tab): Promise<void> {
  await createSession({
    source: "context_menu",
    task: info.selectionText ? `Review this selection: ${info.selectionText}` : "Review this page in Mantle",
    url: info.linkUrl ?? info.pageUrl ?? tab?.url,
    selection: info.selectionText,
    title: tab?.title,
  });
}

async function createSession(payload: Record<string, string | undefined>): Promise<void> {
  const config = await getConfig();
  await setIconState("teal");

  try {
    const response = await fetch(`${config.gatewayUrl}/api/sessions`, {
      method: "POST",
      headers: headers(config),
      body: JSON.stringify({
        ...payload,
        client: "browser-extension",
      }),
    });

    if (!response.ok) {
      throw new Error(`Gateway returned ${response.status}`);
    }

    const session = (await response.json()) as SessionResponse;
    const sessionId = session.id ?? session.session_id;
    if (sessionId) {
      await setStoredValues({ currentSessionId: sessionId });
    }
    await setIconState(iconStateForStatus(normalizeStatus(session.status ?? session.state)));
  } catch (error) {
    console.warn("Mantle session creation failed", error);
    await setIconState("gray");
  }
}

async function pollGateway(): Promise<void> {
  const config = await getConfig();
  const sessionPath = config.currentSessionId ? `/api/sessions/${encodeURIComponent(config.currentSessionId)}` : "/api/sessions/current";

  try {
    const response = await fetch(`${config.gatewayUrl}${sessionPath}`, { headers: headers(config, false) });
    if (response.status === 404) {
      await setIconState("gray");
      return;
    }
    if (!response.ok) {
      throw new Error(`Gateway returned ${response.status}`);
    }

    const session = (await response.json()) as SessionResponse;
    const sessionId = session.id ?? session.session_id;
    if (sessionId && sessionId !== config.currentSessionId) {
      await setStoredValues({ currentSessionId: sessionId });
    }
    await setIconState(iconStateForStatus(normalizeStatus(session.status ?? session.state)));
  } catch {
    await setIconState("gray");
  }
}

function normalizeStatus(status?: string): SessionStatus {
  switch ((status ?? "").toLowerCase()) {
    case "queued":
      return "queued";
    case "running":
    case "in_progress":
    case "working":
      return "running";
    case "done":
    case "complete":
    case "completed":
    case "succeeded":
      return "done";
    case "failed":
    case "error":
    case "cancelled":
      return "failed";
    default:
      return "unknown";
  }
}

function iconStateForStatus(status: SessionStatus): IconState {
  if (status === "done") return "green";
  if (status === "queued" || status === "running") return "teal";
  return "gray";
}

async function setIconState(state: IconState): Promise<void> {
  await chrome.action.setIcon({
    path: {
      16: `assets/icons/${state}-16.png`,
      32: `assets/icons/${state}-32.png`,
      48: `assets/icons/${state}-48.png`,
      128: `assets/icons/${state}-128.png`,
    },
  });
  await chrome.action.setTitle({ title: `Rasputin Mantle: ${state}` });
}

async function getConfig(): Promise<MantleConfig> {
  const values = await getStoredValues(["gatewayUrl", "bearerToken", "currentSessionId"]);
  return {
    gatewayUrl: sanitizeGatewayUrl(values.gatewayUrl),
    bearerToken: values.bearerToken?.trim() || undefined,
    currentSessionId: values.currentSessionId?.trim() || undefined,
  };
}

function sanitizeGatewayUrl(value?: string): string {
  const trimmed = value?.trim() || DEFAULT_GATEWAY_URL;
  return trimmed.replace(/\/+$/, "");
}

function headers(config: MantleConfig, json = true): HeadersInit {
  const result: Record<string, string> = {};
  if (json) result["Content-Type"] = "application/json";
  if (config.bearerToken) result.Authorization = `Bearer ${config.bearerToken}`;
  return result;
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

function setStoredValues(values: Record<string, string>): Promise<void> {
  return new Promise((resolve) => {
    chrome.storage.sync.set(values, () => resolve());
  });
}
