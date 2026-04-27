interface AppMenus {
  title: string
  icon: string
  path: string
  description?: string
  hidden?: boolean
}

export const SIDEBAR_EXPAND_WIDTH = 280;
export const SIDEBAR_COLLAPSED_WIDTH = 72;
export const APP_MENU: AppMenus[] = [
  {
    title: 'Dashboard',
    icon: 'CircleGauge',
    path: '/home',
  },
  {
    title: 'Application Boards',
    icon: 'LayoutDashboard',
    path: '/boards',
    description: 'Manage Boards and Applications'
  },
  {
    title: 'Plugins',
    icon: 'Workflow',
    path: '/plugins',
    description: 'Manage Plugins, Workflows and Integrations'
  },
];

export const SETTINGS_MENU_ITEM: AppMenus = {
  title: 'Settings',
  icon: 'Settings',
  path: '/settings',
  description: 'Manage account, skills, CVs and preferences',
};

export const globalSearch = {

};
