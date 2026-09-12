<script setup lang="ts">
import { GoogleLogo, LinkedInLogo } from '@job-applica/ui';
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
          <Loader v-if="isLoading" :size="16" class="mr-2" />
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
