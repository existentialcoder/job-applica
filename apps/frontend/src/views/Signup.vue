<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod';
import { useForm } from 'vee-validate';
import { ref, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import * as z from 'zod';
import AppLogo from '@/components/core/AppLogo.vue';
import AuthSplitLayout from '@/components/core/AuthSplitLayout.vue';
import { Button } from '@/components/ui/button';
import { FormControl, FormField, FormLabel, FormItem, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const signupError = ref('');
const isLoading = ref(false);

const securityQuestions = ref<string[]>([]);
onMounted(async () => {
  securityQuestions.value = await authStore.getSecurityQuestions();
});

const formSchema = toTypedSchema(
  z
    .object({
      first_name: z.string().min(1, 'First name is required'),
      last_name: z.string().min(1, 'Last name is required'),
      user_name: z
        .string()
        .min(3, 'Username must be at least 3 characters')
        .regex(/^\S+$/, 'No spaces allowed'),
      email: z.string().email('Invalid email').optional().or(z.literal('')),
      password: z.string().min(6, 'Password must be at least 6 characters'),
      confirm_password: z.string().min(1, 'Please confirm your password'),
      security_question: z.string().optional().or(z.literal('')),
      security_answer: z.string().optional().or(z.literal(''))
    })
    .refine((data) => data.password === data.confirm_password, {
      message: 'Passwords do not match',
      path: ['confirm_password']
    })
    .refine((data) => !!data.email || !!data.security_question, {
      message: 'Required when not providing an email',
      path: ['security_question']
    })
    .refine((data) => !!data.email || !!data.security_answer, {
      message: 'Required when not providing an email',
      path: ['security_answer']
    })
);

const form = useForm({ validationSchema: formSchema });

// ── Username availability ────────────────────────────────────────────────────
const usernameStatus = ref<'idle' | 'checking' | 'available' | 'taken'>('idle');
let usernameCheckTimer: ReturnType<typeof setTimeout> | null = null;
let usernameCheckToken = 0; // guards against a stale response overwriting a newer check

watch(
  () => form.values.user_name,
  (userName) => {
    if (usernameCheckTimer) clearTimeout(usernameCheckTimer);
    usernameStatus.value = 'idle';

    // Don't bother checking until it's at least plausibly valid — matches the zod rule.
    if (!userName || userName.length < 3 || /\s/.test(userName)) return;

    usernameCheckTimer = setTimeout(async () => {
      usernameStatus.value = 'checking';
      const myToken = ++usernameCheckToken;
      const isAvailable = await authStore.checkUsernameAvailability(userName);
      if (myToken !== usernameCheckToken) return;

      if (isAvailable === null) {
        usernameStatus.value = 'idle';
        return;
      }
      usernameStatus.value = isAvailable ? 'available' : 'taken';
      if (!isAvailable) {
        form.setFieldError('user_name', 'Username is already taken');
      }
    }, 500);
  }
);

const onSubmit = form.handleSubmit(async (values) => {
  if (usernameStatus.value === 'taken') {
    form.setFieldError('user_name', 'Username is already taken');
    return;
  }

  signupError.value = '';
  isLoading.value = true;

  const result = await authStore.signup({
    first_name: values.first_name,
    last_name: values.last_name,
    user_name: values.user_name,
    email: values.email || undefined,
    password: values.password,
    signup_key: values.email ? 'EMAIL' : 'USER_NAME',
    security_question: values.security_question || undefined,
    security_answer: values.security_answer || undefined
  });

  isLoading.value = false;

  if (result.ok) {
    // Auto-login after signup
    const loginResult = await authStore.login(values.user_name, values.password);
    if (loginResult.ok) {
      router.push('/applications');
    } else {
      router.push('/login');
    }
  } else {
    signupError.value = result.error || 'Signup failed. Please try again.';
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
    <div class="flex flex-col w-full max-w-[420px] gap-8">
      <!-- Logo -->
      <div class="flex justify-center">
        <AppLogo :showBrandName="false" />
      </div>

      <!-- Heading + sub -->
      <div class="flex flex-col items-center gap-1">
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Create your account</h1>
        <p class="text-sm text-muted-foreground">
          Already have an account?
          <router-link
            to="/login"
            class="text-primary hover:underline font-medium inline-flex items-center gap-1"
          >
            Sign in
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

      <form @submit="onSubmit" class="flex flex-col gap-3">
        <div class="grid grid-cols-2 gap-3">
          <FormField v-slot="{ componentField }" name="first_name">
            <FormItem>
              <FormLabel>First name</FormLabel>
              <FormControl>
                <Input type="text" placeholder="John" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField v-slot="{ componentField }" name="last_name">
            <FormItem>
              <FormLabel>Last name</FormLabel>
              <FormControl>
                <Input type="text" placeholder="Doe" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>

        <FormField v-slot="{ componentField }" name="user_name">
          <FormItem>
            <FormLabel>Username</FormLabel>
            <FormControl>
              <Input type="text" placeholder="johndoe" v-bind="componentField" />
            </FormControl>
            <p v-if="usernameStatus === 'checking'" class="text-xs text-muted-foreground">
              Checking availability…
            </p>
            <p
              v-else-if="usernameStatus === 'available'"
              class="text-xs text-emerald-600 dark:text-emerald-400"
            >
              ✓ Username is available
            </p>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="email">
          <FormItem>
            <FormLabel
              >Email <span class="text-muted-foreground font-normal">(optional)</span></FormLabel
            >
            <FormControl>
              <Input type="email" placeholder="john@example.com" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="security_question">
          <FormItem>
            <FormLabel>
              Security question
              <span v-if="!form.values.email" class="text-destructive">*</span>
              <span v-else class="text-muted-foreground font-normal">(optional)</span>
            </FormLabel>
            <FormControl>
              <Select v-bind="componentField">
                <SelectTrigger>
                  <SelectValue placeholder="Choose a security question" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem v-for="q in securityQuestions" :key="q" :value="q">{{
                      q
                    }}</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </FormControl>
            <p class="text-xs text-muted-foreground">
              Used to recover your account if you don't provide an email.
            </p>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField
          v-if="form.values.security_question"
          v-slot="{ componentField }"
          name="security_answer"
        >
          <FormItem>
            <FormLabel>
              Answer
              <span v-if="!form.values.email" class="text-destructive">*</span>
              <span v-else class="text-muted-foreground font-normal">(optional)</span>
            </FormLabel>
            <FormControl>
              <Input type="text" placeholder="Your answer" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="password">
          <FormItem>
            <FormLabel>Password</FormLabel>
            <FormControl>
              <Input type="password" placeholder="••••••••" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="confirm_password">
          <FormItem>
            <FormLabel>Confirm password</FormLabel>
            <FormControl>
              <Input type="password" placeholder="••••••••" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <p v-if="signupError" class="text-sm text-destructive text-center">{{ signupError }}</p>

        <Button class="w-full" type="submit" :disabled="isLoading || usernameStatus === 'checking'">
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
          {{ isLoading ? 'Creating account...' : 'Continue' }}
        </Button>
      </form>

      <!-- Terms -->
      <p class="text-center text-xs text-muted-foreground text-pretty">
        By signing up, you agree to the
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
