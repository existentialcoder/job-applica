import { createRouter, createWebHistory, type RouteMeta } from 'vue-router'
import AppLayoutVue from '@/layouts/app.vue';
import { useAuthStore } from '@/stores/auth';
import { useFeatureStore } from '@/stores/features';
import type { FeatureFlags } from '@/stores/features';

interface IRouteMeta {
  title: string
  flag?: keyof FeatureFlags
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
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('@/views/ResetPassword.vue'),
      meta: { title: 'JobApplica | Reset Password' } as RouteMeta & IRouteMeta
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
          path: '',
          name: 'home',
          component: () => import('@/views/Home.vue'),
          meta: {
            title: 'JobApplica | Dashboard',
          } as RouteMeta & IRouteMeta
        },
        {
          path: '/boards',
          name: 'boards',
          component: () => import('@/views/Boards.vue'),
          meta: { title: 'JobApplica | Application Boards', flag: 'boards' } as RouteMeta & IRouteMeta,
        },
        {
          path: '/boards/:boardId',
          name: 'board-detail',
          component: () => import('@/views/BoardDetail.vue'),
          meta: { title: 'JobApplica | Board', flag: 'boards' } as RouteMeta & IRouteMeta,
        },
        {
          path: '/applications',
          redirect: '/boards',
        },
        {
          path: '/profile',
          redirect: '/settings?tab=profile',
        },
        {
          path: '/resumes',
          component: () => import('@/views/Resumes.vue'),
          meta: { title: 'JobApplica | Resumes' } as RouteMeta & IRouteMeta,
        },
        {
          path: '/plugins',
          component: () => import('@/views/Plugins.vue'),
          meta: { title: 'JobApplica | Plugins', flag: 'plugins' } as RouteMeta & IRouteMeta,
        },
        {
          path: '/settings',
          component: () => import('@/views/Profile.vue'),
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
  const publicRoutes = ['login', 'signup', 'reset-password', 'not-found', 'auth-callback', 'auth-relay'];

  if (!authStore.isAuthenticated && !publicRoutes.includes(to.name as string) && to.path !== '/login') {
    return next('/login');
  }
  if (authStore.isAuthenticated && to.path === '/login') {
    return next('/boards');
  }

  // Feature flag guard — redirect to home if route's flag is disabled
  const flag = to.meta.flag as keyof FeatureFlags | undefined;
  if (flag) {
    const featureStore = useFeatureStore();
    if (featureStore.loaded && !featureStore.flags[flag]) {
      return next('/home');
    }
  }

  next();
})

export default router
