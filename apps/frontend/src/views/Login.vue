<script setup lang="ts">
import { GoogleLogo, LinkedInLogo } from '@job-applica/ui';
import { toTypedSchema } from '@vee-validate/zod';
import { useForm } from 'vee-validate';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import * as z from 'zod';
import AppLogo from '@/components/core/AppLogo.vue';
import AuthSplitLayout from '@/components/core/AuthSplitLayout.vue';
import { Button } from '@/components/ui/button';
import { FormControl, FormField, FormLabel, FormItem, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const loginError = ref('');
const isLoading = ref(false);

const formSchema = toTypedSchema(
  z.object({
    username: z.string().min(1, 'Username or email is required'),
    password: z.string().min(1, 'Password is required')
  })
);

const form = useForm({ validationSchema: formSchema });

const onSubmit = form.handleSubmit(async (values) => {
  loginError.value = '';
  isLoading.value = true;
  const result = await authStore.login(values.username, values.password);
  isLoading.value = false;

  if (result.ok) {
    router.push('/home');
  } else {
    loginError.value = result.error || 'Login failed. Please check your credentials.';
  }
});

function loginWithGoogle() {
  window.location.href = `${API_BASE}/auth/google?origin=web`;
}

function loginWithLinkedIn() {
  window.location.href = `${API_BASE}/auth/linkedin?origin=web`;
}
</script>

<template>
  <AuthSplitLayout>
    <div class="flex flex-col w-full max-w-[360px] gap-8">
      <!-- Logo -->
      <div class="flex justify-center">
        <AppLogo :showBrandName="false" />
      </div>

      <!-- Heading + sub -->
      <div class="flex flex-col items-center gap-1">
        <h1 class="text-2xl font-bold tracking-tight text-foreground">
          Sign in to <span class="text-foreground">Job</span
          ><span class="text-[#818CF8]">Applica</span>
        </h1>
        <p class="text-sm text-muted-foreground">
          Don't have an account?
          <router-link
            to="/signup"
            class="text-primary hover:underline font-medium inline-flex items-center gap-1"
          >
            Get started
            <Icon name="ChevronRight" :size="14" />
          </router-link>
        </p>
      </div>

      <!-- OAuth buttons -->
      <div class="flex flex-col gap-3">
        <Button variant="outline" class="w-full gap-2" type="button" @click="loginWithGoogle">
          <GoogleLogo :size="16" />
          Continue with Google
        </Button>

        <Button variant="outline" class="w-full gap-2" type="button" @click="loginWithLinkedIn">
          <LinkedInLogo :size="16" />
          Continue with LinkedIn
        </Button>
      </div>

      <!-- Divider -->
      <div class="relative">
        <Separator />
        <span
          class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-2 text-xs text-muted-foreground"
        >
          or
        </span>
      </div>

      <!-- Email/password form -->
      <form @submit="onSubmit" class="flex flex-col gap-4">
        <FormField v-slot="{ componentField }" name="username">
          <FormItem>
            <FormLabel>Username or Email</FormLabel>
            <FormControl>
              <Input type="text" placeholder="username or email" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="password">
          <FormItem>
            <div class="flex items-center justify-between">
              <FormLabel class="mb-0">Password</FormLabel>
              <router-link
                to="/reset-password"
                class="text-xs text-primary hover:underline font-medium"
              >
                Forgot password?
              </router-link>
            </div>
            <FormControl>
              <Input type="password" placeholder="••••••••" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <p v-if="loginError" class="text-sm text-destructive text-center">{{ loginError }}</p>

        <Button class="w-full" type="submit" :disabled="isLoading">
          <Icon v-if="isLoading" name="LoaderCircle" :size="16" default-class="animate-spin mr-2" />
          {{ isLoading ? 'Signing in...' : 'Continue' }}
        </Button>
      </form>

      <!-- Terms -->
      <p class="text-center text-xs text-muted-foreground text-pretty">
        By signing in, you agree to the
        <a href="https://jobapplica.io/terms" target="_blank" class="text-primary hover:underline"
          >Terms of Service</a
        >
        and
        <a href="https://jobapplica.io/privacy" target="_blank" class="text-primary hover:underline"
          >Privacy Policy</a
        >.
      </p>
    </div>
  </AuthSplitLayout>
</template>
