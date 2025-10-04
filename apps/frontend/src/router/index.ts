import { createRouter, createWebHistory, type RouteMeta } from 'vue-router'
import AppLayoutVue from '@/layouts/app.vue';

interface IRouteMeta {
  title: string
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: {
        title: 'Login',
      } as RouteMeta & IRouteMeta,
    },
    {
      path: '/home',
      component: AppLayoutVue,
      meta: {
        title: 'Dashboard',
      },
      children: [
        {
          path: 'home',
          name: 'home',
          component: () => import('@/views/Home.vue'),
          meta: {
            title: 'Home',
          } as RouteMeta & IRouteMeta
        },
        {
          path: '/applications',
          component: () => import('@/views/Applications.vue'),
          meta: {
            title: 'Applications',
          } as RouteMeta & IRouteMeta,
        },
        {
          path: '/profile',
          component: () => import('@/views/Profile.vue'),
          meta: {
            title: 'Profile',
          } as RouteMeta & IRouteMeta,
        },
        {
          path: '/plugins',
          component: () => import('@/views/Plugins.vue'),
          meta: {
            title: 'Plugins',
          } as RouteMeta & IRouteMeta,
        },
        {
          path: '/settings',
          component: () => import('@/views/Settings.vue'),
          meta: {
            title: 'Settings',
          } as RouteMeta & IRouteMeta,
        },
      ],
    },
    {
      path: '/:pathMatch(.*)',
      name: 'not-found',
      component: () => import('@/views/404.vue'),
      meta: {
        title: 'Page Not Found',
      } as RouteMeta & IRouteMeta,
    },
  ]
});

router.beforeEach((loc) => {
  document.title = loc.meta.title as string;
})

export default router
