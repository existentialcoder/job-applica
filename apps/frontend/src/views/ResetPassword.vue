<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

const router = useRouter();
const authStore = useAuthStore();

type Step = 'identify' | 'answer_question' | 'otp_consent' | 'otp_input' | 'new_password' | 'success';

const step = ref<Step>('identify');
const isLoading = ref(false);
const formError = ref('');

const identifier = ref('');
const securityQuestion = ref('');
const answer = ref('');
const otp = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const resetToken = ref('');

const OTP_DURATION_SECONDS = 120;
const otpSecondsLeft = ref(0);
let otpTimer: ReturnType<typeof setInterval> | null = null;

const otpTimeDisplay = computed(() => {
  const minutes = Math.floor(otpSecondsLeft.value / 60);
  const seconds = otpSecondsLeft.value % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
});

function startOtpTimer() {
  if (otpTimer) clearInterval(otpTimer);
  otpSecondsLeft.value = OTP_DURATION_SECONDS;
  otpTimer = setInterval(() => {
    otpSecondsLeft.value -= 1;
    if (otpSecondsLeft.value <= 0 && otpTimer) {
      clearInterval(otpTimer);
      otpTimer = null;
    }
  }, 1000);
}

onUnmounted(() => {
  if (otpTimer) clearInterval(otpTimer);
});

async function submitIdentifier() {
  formError.value = '';
  if (!identifier.value.trim()) {
    formError.value = 'Enter your username or email';
    return;
  }

  isLoading.value = true;
  const result = await authStore.getResetMechanism(identifier.value.trim());
  isLoading.value = false;

  if (!result.ok) {
    formError.value = result.error;
    return;
  }

  if (result.mechanism === 'security_question') {
    securityQuestion.value = result.securityQuestion;
    step.value = 'answer_question';
  } else {
    step.value = 'otp_consent';
  }
}

async function submitAnswer() {
  formError.value = '';
  if (!answer.value.trim()) {
    formError.value = 'Enter your answer';
    return;
  }

  isLoading.value = true;
  const result = await authStore.verifyResetMechanism(
    identifier.value.trim(),
    'security_question',
    securityQuestion.value,
    answer.value.trim()
  );
  isLoading.value = false;

  if (!result.ok) {
    formError.value = result.error || 'Incorrect answer';
    return;
  }
  resetToken.value = result.token || '';
  step.value = 'new_password';
}

async function sendOtp() {
  formError.value = '';
  isLoading.value = true;
  const result = await authStore.requestResetOtp(identifier.value.trim());
  isLoading.value = false;

  if (!result.ok) {
    formError.value = result.error || 'Failed to send code';
    return;
  }
  step.value = 'otp_input';
  startOtpTimer();
}

async function submitOtp() {
  formError.value = '';
  if (!otp.value.trim()) {
    formError.value = 'Enter the code we sent you';
    return;
  }

  isLoading.value = true;
  const result = await authStore.verifyResetMechanism(identifier.value.trim(), 'otp', '', otp.value.trim());
  isLoading.value = false;

  if (!result.ok) {
    formError.value = result.error || 'Incorrect or expired code';
    return;
  }
  resetToken.value = result.token || '';
  step.value = 'new_password';
}

async function submitNewPassword() {
  formError.value = '';
  if (newPassword.value.length < 6) {
    formError.value = 'Password must be at least 6 characters';
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    formError.value = 'Passwords do not match';
    return;
  }

  isLoading.value = true;
  const result = await authStore.resetPassword(resetToken.value, newPassword.value);
  isLoading.value = false;

  if (!result.ok) {
    formError.value = result.error || 'Password reset failed';
    return;
  }
  step.value = 'success';
}
</script>

<template>
  <main class="min-h-screen w-screen flex items-center justify-center bg-background py-8">
    <Card class="max-w-[320px] md:max-w-[400px] w-full">
      <CardHeader>
        <div class="flex justify-center mb-2">
          <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <CardTitle class="text-center">Reset your password</CardTitle>
        <p class="text-sm text-muted-foreground text-center">Verify your identity to set a new password</p>
      </CardHeader>

      <CardContent>
        <!-- Step 1: identify -->
        <form v-if="step === 'identify'" @submit.prevent="submitIdentifier" class="flex flex-col gap-3">
          <div class="flex flex-col gap-1.5">
            <Label>Username or email</Label>
            <Input type="text" placeholder="username or email" v-model="identifier" />
          </div>
          <p v-if="formError" class="text-sm text-destructive text-center">{{ formError }}</p>
        </form>

        <!-- Step 2a: security question -->
        <form v-else-if="step === 'answer_question'" @submit.prevent="submitAnswer" class="flex flex-col gap-3">
          <p class="text-sm font-medium">{{ securityQuestion }}</p>
          <div class="flex flex-col gap-1.5">
            <Input type="text" placeholder="Your answer" v-model="answer" />
          </div>
          <p v-if="formError" class="text-sm text-destructive text-center">{{ formError }}</p>
        </form>

        <!-- Step 2b: OTP consent -->
        <div v-else-if="step === 'otp_consent'" class="flex flex-col gap-3">
          <p class="text-sm text-muted-foreground text-center">
            We'll send a verification code to the email on file for <span class="font-medium text-foreground">{{ identifier }}</span>.
          </p>
          <p v-if="formError" class="text-sm text-destructive text-center">{{ formError }}</p>
        </div>

        <!-- Step 2c: OTP input -->
        <form v-else-if="step === 'otp_input'" @submit.prevent="submitOtp" class="flex flex-col gap-3">
          <p class="text-sm text-muted-foreground">Enter the code we sent you.</p>
          <div class="flex flex-col gap-1.5">
            <Label>Verification code</Label>
            <Input type="text" placeholder="123456" v-model="otp" />
          </div>
          <p class="text-sm text-muted-foreground text-center">
            <span v-if="otpSecondsLeft > 0">Code expires in {{ otpTimeDisplay }}</span>
            <span v-else class="text-destructive">Code expired</span>
          </p>
          <p v-if="formError" class="text-sm text-destructive text-center">{{ formError }}</p>
        </form>

        <!-- Step 3: new password -->
        <form v-else-if="step === 'new_password'" @submit.prevent="submitNewPassword" class="flex flex-col gap-3">
          <div class="flex flex-col gap-1.5">
            <Label>New password</Label>
            <Input type="password" placeholder="••••••••" v-model="newPassword" />
          </div>
          <div class="flex flex-col gap-1.5">
            <Label>Confirm new password</Label>
            <Input type="password" placeholder="••••••••" v-model="confirmPassword" />
          </div>
          <p v-if="formError" class="text-sm text-destructive text-center">{{ formError }}</p>
        </form>

        <!-- Step 4: success -->
        <div v-else-if="step === 'success'" class="flex flex-col items-center gap-3 py-4 text-center">
          <p class="text-sm text-foreground">Your password has been reset.</p>
        </div>
      </CardContent>

      <CardFooter class="flex flex-col gap-3">
        <Button v-if="step === 'identify'" class="w-full" @click="submitIdentifier" :disabled="isLoading">
          {{ isLoading ? 'Checking...' : 'Continue' }}
        </Button>
        <Button v-else-if="step === 'answer_question'" class="w-full" @click="submitAnswer" :disabled="isLoading">
          {{ isLoading ? 'Verifying...' : 'Verify' }}
        </Button>
        <Button v-else-if="step === 'otp_consent'" class="w-full" @click="sendOtp" :disabled="isLoading">
          {{ isLoading ? 'Sending...' : 'Send code' }}
        </Button>
        <Button v-else-if="step === 'otp_input' && otpSecondsLeft > 0" class="w-full" @click="submitOtp" :disabled="isLoading">
          {{ isLoading ? 'Verifying...' : 'Verify' }}
        </Button>
        <Button v-else-if="step === 'otp_input'" class="w-full" @click="sendOtp" :disabled="isLoading">
          {{ isLoading ? 'Sending...' : 'Resend code' }}
        </Button>
        <Button v-else-if="step === 'new_password'" class="w-full" @click="submitNewPassword" :disabled="isLoading">
          {{ isLoading ? 'Resetting...' : 'Reset Password' }}
        </Button>
        <Button v-else-if="step === 'success'" class="w-full" @click="router.push('/login')">
          Back to sign in
        </Button>

        <p v-if="step !== 'success'" class="text-sm text-muted-foreground text-center">
          Trying again?
          <router-link to="/login" class="text-primary hover:underline font-medium">Sign in</router-link>
        </p>
      </CardFooter>
    </Card>
  </main>
</template>
