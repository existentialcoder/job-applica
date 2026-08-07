<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { useAuthStore } from '@/stores/auth'
import AuthSplitLayout from '@/components/core/AuthSplitLayout.vue'
import AppLogo from '@/components/core/AppLogo.vue'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { FormControl, FormField, FormLabel, FormItem, FormMessage } from '@/components/ui/form'
import { Separator } from '@/components/ui/separator'

const router = useRouter()
const authStore = useAuthStore()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const loginError = ref('')
const isLoading = ref(false)

const formSchema = toTypedSchema(
  z.object({
    username: z.string().min(1, 'Username or email is required'),
    password: z.string().min(1, 'Password is required')
  })
)

const form = useForm({ validationSchema: formSchema })

const onSubmit = form.handleSubmit(async (values) => {
  loginError.value = ''
  isLoading.value = true
  const result = await authStore.login(values.username, values.password)
  isLoading.value = false

  if (result.ok) {
    router.push('/home')
  } else {
    loginError.value = result.error || 'Login failed. Please check your credentials.'
  }
})

function loginWithGoogle() {
  window.location.href = `${API_BASE}/auth/google?origin=web`
}

function loginWithLinkedIn() {
  window.location.href = `${API_BASE}/auth/linkedin?origin=web`
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
            <svg
              class="w-3.5 h-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M5 12h14m-7-7l7 7-7 7" />
            </svg>
          </router-link>
        </p>
      </div>

      <!-- OAuth buttons -->
      <div class="flex flex-col gap-3">
        <Button variant="outline" class="w-full gap-2" type="button" @click="loginWithGoogle">
          <svg class="w-4 h-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
          Continue with Google
        </Button>

        <Button variant="outline" class="w-full gap-2" type="button" @click="loginWithLinkedIn">
          <svg
            class="w-4 h-4"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            fill="#0A66C2"
          >
            <path
              d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
            />
          </svg>
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
          <svg
            v-if="isLoading"
            class="w-4 h-4 animate-spin mr-2"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
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
