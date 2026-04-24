import { createRouter, createWebHistory, type RouteMeta } from 'vue-router'
import AppLayoutVue from '@/layouts/app.vue';
import { useAuthStore } from '@/stores/auth';

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
      meta: { title: 'JobApplica | Login' } as RouteMeta & IRouteMeta,
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/Signup.vue'),
      meta: { title: 'JobApplica | Sign Up' } as RouteMeta & IRouteMeta,
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('@/views/AuthCallback.vue'),
      meta: { title: 'JobApplica | Signing In' } as RouteMeta & IRouteMeta,
    },
    {
      path: '/auth/relay',
      name: 'auth-relay',
      component: () => import('@/views/AuthRelay.vue'),
      meta: { title: 'JobApplica | Extension Sign-In' } as RouteMeta & IRouteMeta,
    },
    {
      path: '/home',
      component: AppLayoutVue,
      meta: {
        title: 'JobApplica | Dashboard',
      },
      children: [
        {
          path: 'home',
          name: 'home',
          component: () => import('@/views/Home.vue'),
          meta: {
            title: 'JobApplica | DashBoard',
          } as RouteMeta & IRouteMeta
        },
        {
          path: '/applications',
          component: () => import('@/views/Applications.vue'),
          meta: {
            title: 'JobApplica | Applications',
          } as RouteMeta & IRouteMeta,
        },
        {
          path: '/profile',
          component: () => import('@/views/Profile.vue'),
          meta: {
            title: 'JobApplica | Profile',
          } as RouteMeta & IRouteMeta,
        },
        {
          path: '/plugins',
          component: () => import('@/views/Plugins.vue'),
          meta: {
            title: 'JobApplica | Plugins',
          } as RouteMeta & IRouteMeta,
        },
        {
          path: '/settings',
          component: () => import('@/views/Settings.vue'),
          meta: {
            title: 'JobApplica | Settings',
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

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title as string;
  const authStore = useAuthStore();
  const publicRoutes = ['login', 'signup', 'not-found', 'auth-callback', 'auth-relay'];
  if (!authStore.isAuthenticated && !publicRoutes.includes(to.name as string) && to.path !== '/login') {
    next('/login');
  } else if (authStore.isAuthenticated && to.path === '/login') {
    next('/applications');
  } else {
    next();
  }
})

export default router
