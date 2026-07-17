import ext from './ext';

export const config = {
  apiBase: import.meta.env.VITE_API_BASE as string,
  appUrl: import.meta.env.VITE_APP_URL as string,
};

const DEFAULTS = {
  apiBase: import.meta.env.VITE_API_BASE as string,
  appUrl: import.meta.env.VITE_APP_URL as string,
};

export async function loadConfig(): Promise<void> {
  const stored = await ext.storage.local.get(['custom_api_url', 'custom_app_url']);
  if (stored.custom_api_url) {
    config.apiBase = stored.custom_api_url as string;
  }
  if (stored.custom_app_url) {
    config.appUrl = stored.custom_app_url as string;
  }
}

export async function saveConfig(apiBase: string, appUrl: string): Promise<void> {
  config.apiBase = apiBase.replace(/\/$/, '');
  config.appUrl = appUrl.replace(/\/$/, '');
  await ext.storage.local.set({ custom_api_url: config.apiBase, custom_app_url: config.appUrl });
}

export async function resetConfig(): Promise<void> {
  config.apiBase = DEFAULTS.apiBase;
  config.appUrl = DEFAULTS.appUrl;
  await ext.storage.local.remove(['custom_api_url', 'custom_app_url']);
}
