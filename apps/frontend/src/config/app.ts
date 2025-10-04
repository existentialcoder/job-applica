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
    path: 'home',
  },
  {
    title: 'Applications',
    icon: 'IdCard',
    path: 'applications',
    description: 'Manage Applications'
  },
  {
    title: 'Profile',
    icon: 'User',
    path: 'profile',
    description: 'Manage Profile',
  },
  {
    title: 'Plugins',
    icon: 'Workflow',
    path: 'plugins',
    description: 'Manage Plugins, Workflows and Integrations'
  },
  {
    title: 'Settings',
    icon: 'Settings',
    path: 'settings',
    description: 'Manage Settings',
  }
];

export const globalSearch = {

};
