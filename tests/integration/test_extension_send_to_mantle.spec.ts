import playwright from '@playwright/test';

const { expect, test } = playwright;

type ContextMenuCreateProperties = {
  id?: string;
  title?: string;
  contexts?: string[];
};

type ContextMenuClickInfo = {
  menuItemId: string;
  selectionText?: string;
  pageUrl?: string;
  linkUrl?: string;
};

type TabInfo = {
  title?: string;
  url?: string;
};

type ExtensionHarness = {
  createdMenu?: ContextMenuCreateProperties;
  installed?: () => void;
  clicked?: (info: ContextMenuClickInfo, tab?: TabInfo) => void;
  stored: Record<string, string>;
  iconTitles: string[];
};

declare global {
  interface Window {
    __mantleExtensionHarness: ExtensionHarness;
    chrome: {
      runtime: {
        onInstalled: { addListener(listener: () => void): void };
        onStartup: { addListener(listener: () => void): void };
      };
      contextMenus: {
        removeAll(callback: () => void): void;
        create(properties: ContextMenuCreateProperties): void;
        onClicked: { addListener(listener: (info: ContextMenuClickInfo, tab?: TabInfo) => void): void };
      };
      sidePanel: { setPanelBehavior(options: { openPanelOnActionClick: boolean }): Promise<void> };
      omnibox: {
        onInputStarted: { addListener(listener: () => void): void };
        onInputEntered: { addListener(listener: (text: string) => void): void };
      };
      storage: {
        sync: {
          get(keys: string[], callback: (items: Record<string, string>) => void): void;
          set(values: Record<string, string>, callback: () => void): void;
        };
        onChanged: { addListener(listener: () => void): void };
      };
      action: {
        setIcon(options: { path: Record<number, string> }): Promise<void>;
        setTitle(options: { title: string }): Promise<void>;
      };
    };
  }
}

const manifestPath = '/home/josh/rasputin-mantle/packages/browser-extension/manifest.json';
const backgroundSourcePath = '/home/josh/rasputin-mantle/packages/browser-extension/src/background.ts';
const builtBackgroundPath = '/home/josh/rasputin-mantle/packages/browser-extension/dist/extension/background.js';

test('browser extension manifest exposes a MV3 background service worker', async ({ page }) => {
  await page.goto(`file://${manifestPath}`);
  const manifestText = await page.locator('body').innerText();
  const manifest = JSON.parse(manifestText) as {
    manifest_version: number;
    permissions: string[];
    host_permissions: string[];
    background: { service_worker: string; type: string };
  };
  await page.goto(`file://${backgroundSourcePath}`);
  const backgroundSource = await page.locator('body').innerText();

  expect(manifest.manifest_version).toBe(3);
  expect(manifest.background).toEqual({ service_worker: 'background.js', type: 'module' });
  expect(manifest.permissions).toContain('contextMenus');
  expect(manifest.host_permissions).toContain('http://localhost:8000/');
  expect(backgroundSource).toContain('chrome.contextMenus.create');
  expect(backgroundSource).toContain('title: "Send to Mantle"');
});

test('Send to Mantle context menu posts a session to the mocked gateway', async ({ page }) => {
  const requests: Array<Record<string, string | undefined>> = [];

  await page.route('http://localhost:8000/api/sessions/current', async (route) => {
    await route.fulfill({ status: 404, json: { error: 'not_found' } });
  });
  await page.route('http://localhost:8000/api/sessions', async (route) => {
    const body = route.request().postDataJSON() as Record<string, string | undefined>;
    requests.push(body);
    await route.fulfill({ json: { session_id: 'extension-session-1', status: 'queued' } });
  });

  await page.goto(`file://${builtBackgroundPath}`);
  const builtBackground = (await page.locator('body').innerText()).replace(/export\s*\{\};?/g, '');

  await page.goto('about:blank');
  await page.evaluate(() => {
    const harness: ExtensionHarness = { stored: {}, iconTitles: [] };
    window.__mantleExtensionHarness = harness;
    window.chrome = {
      runtime: {
        onInstalled: { addListener: (listener) => { harness.installed = listener; } },
        onStartup: { addListener: () => undefined },
      },
      contextMenus: {
        removeAll: (callback) => callback(),
        create: (properties) => { harness.createdMenu = properties; },
        onClicked: { addListener: (listener) => { harness.clicked = listener; } },
      },
      sidePanel: { setPanelBehavior: async () => undefined },
      omnibox: {
        onInputStarted: { addListener: () => undefined },
        onInputEntered: { addListener: () => undefined },
      },
      storage: {
        sync: {
          get: (keys, callback) => {
            const values: Record<string, string> = {};
            for (const key of keys) {
              if (harness.stored[key]) values[key] = harness.stored[key];
            }
            callback(values);
          },
          set: (values, callback) => {
            Object.assign(harness.stored, values);
            callback();
          },
        },
        onChanged: { addListener: () => undefined },
      },
      action: {
        setIcon: async () => undefined,
        setTitle: async ({ title }) => { harness.iconTitles.push(title); },
      },
    };
  });

  await page.evaluate((source) => {
    new Function(source)();
  }, builtBackground);

  const createdMenu = await page.evaluate(() => {
    window.__mantleExtensionHarness.installed?.();
    return window.__mantleExtensionHarness.createdMenu;
  });

  expect(createdMenu).toEqual({ id: 'send-to-mantle', title: 'Send to Mantle', contexts: ['page', 'selection', 'link'] });

  await page.evaluate(() => {
    window.__mantleExtensionHarness.clicked?.(
      {
        menuItemId: 'send-to-mantle',
        selectionText: 'Important launch paragraph',
        pageUrl: 'https://example.test/launch',
      },
      { title: 'Launch Plan', url: 'https://example.test/launch' },
    );
  });

  await expect.poll(() => requests.length).toBe(1);
  expect(requests[0]).toMatchObject({
    client: 'browser-extension',
    source: 'context_menu',
    task: 'Review this selection: Important launch paragraph',
    selection: 'Important launch paragraph',
    title: 'Launch Plan',
    url: 'https://example.test/launch',
  });

  const storedSession = await page.evaluate(() => window.__mantleExtensionHarness.stored.currentSessionId);
  expect(storedSession).toBe('extension-session-1');
});
