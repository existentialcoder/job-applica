import type { FeatureFlags } from '@/stores/features';

export interface AppMenu {
  title: string
  icon: string
  path: string
  description?: string
  flag?: keyof FeatureFlags
}

export const ALL_MENU_ITEMS: AppMenu[] = [
  {
    title: 'Dashboard',
    icon: 'CircleGauge',
    path: '/home',
    flag: 'dashboard',
  },
  {
    title: 'Application Boards',
    icon: 'LayoutDashboard',
    path: '/boards',
    description: 'Manage Boards and Applications',
    flag: 'boards',
  },
  {
    title: 'Plugins',
    icon: 'Workflow',
    path: '/plugins',
    description: 'Manage Plugins, Workflows and Integrations',
    flag: 'plugins',
  },
];

export const SETTINGS_MENU_ITEM: AppMenu = {
  title: 'Settings',
  icon: 'Settings',
  path: '/settings',
  description: 'Manage account, skills, CVs and preferences',
};

export const SIDEBAR_EXPAND_WIDTH = 280;
export const SIDEBAR_COLLAPSED_WIDTH = 72;

export const globalSearch = {};
