/**
 * Minimal WebExtension API type declarations for cross-browser compatibility.
 * These are intentionally narrow — only the APIs we actually use.
 * Full types: install @types/webextension-polyfill or @types/chrome.
 */

declare namespace WebExtension {
  interface StorageArea {
    get(keys: string | string[] | null): Promise<Record<string, any>>;
    set(items: Record<string, any>): Promise<void>;
    remove(keys: string | string[]): Promise<void>;
  }

  interface Storage {
    local: StorageArea;
    onChanged: {
      addListener(callback: (changes: Record<string, { newValue?: any; oldValue?: any }>, areaName: string) => void): void;
      removeListener(callback: (...args: any[]) => void): void;
    };
  }

  interface Tab {
    id?: number;
    url?: string;
    active?: boolean;
  }

  interface Tabs {
    query(queryInfo: { active?: boolean; currentWindow?: boolean }): Promise<Tab[]>;
    create(createProperties: { url?: string; active?: boolean }): Promise<Tab>;
    remove(tabIds: number | number[]): Promise<void>;
    onUpdated: {
      addListener(callback: (tabId: number, changeInfo: { status?: string; url?: string }, tab: Tab) => void): void;
      removeListener(callback: (...args: any[]) => void): void;
    };
  }

  interface ScriptInjection {
    target: { tabId: number };
    files?: string[];
    func?: () => void;
  }

  interface Scripting {
    executeScript(injection: ScriptInjection): Promise<any[]>;
  }

  interface Runtime {
    sendMessage(message: any): Promise<any>;
    onMessage: {
      addListener(callback: (message: any, sender: any, sendResponse: (response?: any) => void) => void): void;
      removeListener(callback: (...args: any[]) => void): void;
    };
  }
}

interface BrowserExtension {
  storage: WebExtension.Storage;
  tabs: WebExtension.Tabs;
  scripting: WebExtension.Scripting;
  runtime: WebExtension.Runtime;
}

declare const browser: BrowserExtension;
declare const chrome: BrowserExtension & {
  storage: WebExtension.Storage & {
    local: WebExtension.StorageArea & {
      get(keys: string | string[], callback: (result: Record<string, any>) => void): void;
    };
  };
  tabs: WebExtension.Tabs & {
    query(queryInfo: { active?: boolean; currentWindow?: boolean }, callback: (tabs: WebExtension.Tab[]) => void): void;
  };
};
