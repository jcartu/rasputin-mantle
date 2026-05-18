export {};

const DEFAULT_GATEWAY_URL = "http://localhost:8000";

const form = requiredElement("#options-form", HTMLFormElement);
const gatewayUrlInput = requiredElement("#gateway-url", HTMLInputElement);
const bearerTokenInput = requiredElement("#bearer-token", HTMLInputElement);
const statusElement = requiredElement("#status", HTMLElement);

void restoreOptions();

form.addEventListener("submit", (event) => {
  event.preventDefault();
  void saveOptions();
});

async function restoreOptions(): Promise<void> {
  const values = await getStoredValues(["gatewayUrl", "bearerToken"]);
  gatewayUrlInput.value = values.gatewayUrl ?? DEFAULT_GATEWAY_URL;
  bearerTokenInput.value = values.bearerToken ?? "";
}

async function saveOptions(): Promise<void> {
  const gatewayUrl = gatewayUrlInput.value.trim().replace(/\/+$/, "") || DEFAULT_GATEWAY_URL;
  const bearerToken = bearerTokenInput.value.trim();
  await setStoredValues({ gatewayUrl, bearerToken });
  statusElement.textContent = "Saved.";
  window.setTimeout(() => {
    statusElement.textContent = "";
  }, 2_000);
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

function requiredElement<T extends Element>(selector: string, constructor: { new (): T }): T {
  const element = document.querySelector(selector);
  if (!element || !(element instanceof constructor)) {
    throw new Error(`Missing required element: ${selector}`);
  }
  return element;
}
