type ChromeStorageAreaName = "sync" | "local" | "managed" | "session";

type ChromeStorageChange = {
  oldValue?: unknown;
  newValue?: unknown;
};

type ChromeStorageItems = Record<string, unknown>;

type ChromeEvent<TListener extends (...args: never[]) => void> = {
  addListener(listener: TListener): void;
};

declare namespace chrome {
  namespace contextMenus {
    type ContextType = "page" | "selection" | "link";

    type OnClickData = {
      menuItemId: string | number;
      pageUrl?: string;
      linkUrl?: string;
      selectionText?: string;
    };
  }

  namespace tabs {
    type Tab = {
      id?: number;
      title?: string;
      url?: string;
    };
  }
}

type ChromeApi = {
  action: {
    setIcon(details: { path: Record<number, string> }): Promise<void>;
    setTitle(details: { title: string }): Promise<void>;
  };
  contextMenus: {
    removeAll(callback?: () => void): void;
    create(details: { id: string; title: string; contexts: chrome.contextMenus.ContextType[] }): void;
    onClicked: ChromeEvent<(info: chrome.contextMenus.OnClickData, tab?: chrome.tabs.Tab) => void>;
  };
  omnibox: {
    onInputStarted: ChromeEvent<() => void>;
    onInputEntered: ChromeEvent<(text: string) => void>;
  };
  runtime: {
    onInstalled: ChromeEvent<() => void>;
    onStartup: ChromeEvent<() => void>;
  };
  sidePanel?: {
    setPanelBehavior?(details: { openPanelOnActionClick: boolean }): Promise<void>;
  };
  storage: {
    onChanged: ChromeEvent<(changes: Record<string, ChromeStorageChange>, areaName: ChromeStorageAreaName) => void>;
    sync: {
      get(keys: string[], callback: (items: ChromeStorageItems) => void): void;
      set(values: Record<string, string>, callback?: () => void): void;
    };
  };
};

declare const chrome: ChromeApi;
