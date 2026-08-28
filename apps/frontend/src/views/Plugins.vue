<script setup lang="ts">
import { GoogleLogo, LinkedInLogo, GmailLogo, GoogleCalendarLogo } from '@job-applica/ui';
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription
} from '@/components/ui/sheet';
import dataservice from '@/lib/dataservice';
import { toast } from '@/lib/toast';
import type { ConnectedAccount } from '@/lib/types';

const route = useRoute();

// ── State ─────────────────────────────────────────────────────────────────────

const accounts = ref<ConnectedAccount[]>([]);
const loading = ref(true);
const activeSheet = ref<'gmail' | 'calendar' | null>(null);
const connectingFeature = ref<string | null>(null);
const disconnecting = ref<string | null>(null);

// ── Derived connection state ───────────────────────────────────────────────────

const google = computed(() => accounts.value.find((a) => a.provider === 'google') ?? null);
const linkedin = computed(() => accounts.value.find((a) => a.provider === 'linkedin') ?? null);

const gmailConnected = computed(() => google.value?.has_gmail ?? false);
const calendarConnected = computed(() => google.value?.has_calendar ?? false);
const googleConnected = computed(() => !!google.value);
const linkedinConnected = computed(() => !!linkedin.value);

// ── Data loading ──────────────────────────────────────────────────────────────

async function load() {
  loading.value = true;
  accounts.value = await dataservice.getConnectedAccounts();
  loading.value = false;
}

onMounted(async () => {
  await load();
  if (route.query.connected === 'google') {
    toast.success('Google account connected successfully');
    window.history.replaceState({}, '', '/plugins');
  }
});

// ── Actions ───────────────────────────────────────────────────────────────────

async function connectGoogle(features: string[]) {
  const key = features.join(',') || 'google';
  connectingFeature.value = key;
  try {
    const url = await dataservice.getGoogleConnectUrl(features);
    window.location.href = url;
  } catch {
    toast.error('Could not start Google sign-in. Please try again.');
    connectingFeature.value = null;
  }
}

async function disconnect(provider: 'google' | 'linkedin') {
  disconnecting.value = provider;
  try {
    await dataservice.disconnectProvider(provider);
    await load();
    toast.success(`${provider.charAt(0).toUpperCase() + provider.slice(1)} disconnected`);
  } catch {
    toast.error('Disconnect failed. Please try again.');
  } finally {
    disconnecting.value = null;
    activeSheet.value = null;
  }
}
</script>

<template>
  <div class="p-6 max-w-5xl mx-auto space-y-8">
    <!-- Page header -->
    <div>
      <h1 class="text-2xl font-bold">Plugins &amp; Integrations</h1>
      <p class="text-muted-foreground mt-1 text-sm">
        Connect external accounts to automate your job search.
      </p>
    </div>

    <!-- ── Connected Accounts ──────────────────────────────────────────────── -->
    <section>
      <h2 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        Connected Accounts
      </h2>

      <div v-if="loading" class="text-sm text-muted-foreground py-2">Loading…</div>

      <div
        v-else-if="accounts.length === 0"
        class="rounded-lg border border-dashed p-6 text-sm text-muted-foreground text-center"
      >
        No accounts connected yet. Connect Google or LinkedIn below to get started.
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="account in accounts"
          :key="account.provider"
          class="flex items-center justify-between rounded-lg border px-4 py-3 bg-card"
        >
          <div class="flex items-center gap-3 min-w-0">
            <!-- Google -->
            <GoogleLogo v-if="account.provider === 'google'" :size="20" class="flex-shrink-0" />
            <!-- LinkedIn -->
            <LinkedInLogo v-else-if="account.provider === 'linkedin'" :size="20" class="flex-shrink-0" />

            <div class="min-w-0">
              <p class="text-sm font-medium capitalize">{{ account.provider }}</p>
              <p class="text-xs text-muted-foreground truncate">
                {{ account.provider_email ?? account.display_name }}
              </p>
            </div>

            <div class="flex gap-1.5 flex-wrap">
              <Badge v-if="account.has_gmail" variant="secondary" class="text-xs">Gmail</Badge>
              <Badge v-if="account.has_calendar" variant="secondary" class="text-xs"
                >Calendar</Badge
              >
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            class="text-muted-foreground hover:text-destructive flex-shrink-0 ml-2"
            :disabled="disconnecting === account.provider"
            @click="disconnect(account.provider as 'google' | 'linkedin')"
          >
            {{ disconnecting === account.provider ? 'Disconnecting…' : 'Disconnect' }}
          </Button>
        </div>
      </div>
    </section>

    <Separator />

    <!-- ── Email & Calendar Plugins ────────────────────────────────────────── -->
    <section>
      <h2 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        Email &amp; Calendar
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Gmail card -->
        <div class="rounded-xl border bg-card p-5 flex flex-col gap-4">
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-lg bg-red-50 dark:bg-red-900/20 flex items-center justify-center flex-shrink-0"
              >
                <GmailLogo :size="20" />
              </div>
              <div>
                <p class="font-semibold text-sm">Gmail</p>
                <p class="text-xs text-muted-foreground">Auto-track application emails</p>
              </div>
            </div>
            <span
              class="flex items-center gap-1.5 text-xs font-medium whitespace-nowrap"
              :class="gmailConnected ? 'text-green-600' : 'text-muted-foreground'"
            >
              <span
                class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                :class="gmailConnected ? 'bg-green-500' : 'bg-muted-foreground/40'"
              ></span>
              {{ gmailConnected ? 'Connected' : 'Not connected' }}
            </span>
          </div>

          <p class="text-xs text-muted-foreground leading-relaxed flex-1">
            Scan your inbox for job application updates. Detect interview invites, offers, and
            rejections — then update your board automatically.
          </p>

          <Button
            v-if="gmailConnected"
            variant="outline"
            size="sm"
            class="w-full"
            @click="activeSheet = 'gmail'"
          >
            Manage
          </Button>
          <Button
            v-else
            size="sm"
            class="w-full"
            :disabled="connectingFeature === 'gmail'"
            @click="connectGoogle(['gmail'])"
          >
            {{
              connectingFeature === 'gmail'
                ? 'Redirecting…'
                : googleConnected
                  ? 'Add Gmail permissions'
                  : 'Connect Google'
            }}
          </Button>
        </div>

        <!-- Calendar card -->
        <div class="rounded-xl border bg-card p-5 flex flex-col gap-4">
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0"
              >
                <GoogleCalendarLogo :size="20" />
              </div>
              <div>
                <p class="font-semibold text-sm">Google Calendar</p>
                <p class="text-xs text-muted-foreground">Sync interview events</p>
              </div>
            </div>
            <span
              class="flex items-center gap-1.5 text-xs font-medium whitespace-nowrap"
              :class="calendarConnected ? 'text-green-600' : 'text-muted-foreground'"
            >
              <span
                class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                :class="calendarConnected ? 'bg-green-500' : 'bg-muted-foreground/40'"
              ></span>
              {{ calendarConnected ? 'Connected' : 'Not connected' }}
            </span>
          </div>

          <p class="text-xs text-muted-foreground leading-relaxed flex-1">
            Automatically create calendar events when a job moves to Interview, Phone Screen, or
            Technical stage.
          </p>

          <Button
            v-if="calendarConnected"
            variant="outline"
            size="sm"
            class="w-full"
            @click="activeSheet = 'calendar'"
          >
            Manage
          </Button>
          <Button
            v-else
            size="sm"
            class="w-full"
            :disabled="connectingFeature === 'calendar'"
            @click="connectGoogle(['calendar'])"
          >
            {{
              connectingFeature === 'calendar'
                ? 'Redirecting…'
                : googleConnected
                  ? 'Add Calendar permissions'
                  : 'Connect Google'
            }}
          </Button>
        </div>

        <!-- LinkedIn card -->
        <div class="rounded-xl border bg-card p-5 flex flex-col gap-4">
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-lg bg-sky-50 dark:bg-sky-900/20 flex items-center justify-center flex-shrink-0"
              >
                <LinkedInLogo :size="20" />
              </div>
              <div>
                <p class="font-semibold text-sm">LinkedIn</p>
                <p class="text-xs text-muted-foreground">Import jobs via extension</p>
              </div>
            </div>
            <span
              class="flex items-center gap-1.5 text-xs font-medium whitespace-nowrap"
              :class="linkedinConnected ? 'text-green-600' : 'text-muted-foreground'"
            >
              <span
                class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                :class="linkedinConnected ? 'bg-green-500' : 'bg-muted-foreground/40'"
              ></span>
              {{ linkedinConnected ? 'Account linked' : 'Not linked' }}
            </span>
          </div>

          <p class="text-xs text-muted-foreground leading-relaxed flex-1">
            Save jobs from LinkedIn using the browser extension. LinkedIn's API restricts direct
            inbox or job data access.
          </p>

          <Badge variant="outline" class="text-xs w-full justify-center py-1.5">
            Works via Browser Extension
          </Badge>
        </div>
      </div>
    </section>

    <!-- ── Coming Soon ─────────────────────────────────────────────────────── -->
    <section>
      <h2 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        Coming Soon
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="plugin in [
            { name: 'Indeed', desc: 'Discover matching jobs automatically' },
            { name: 'Notion', desc: 'Sync notes and application details' },
            { name: 'Outlook', desc: 'Track emails from your Outlook inbox' }
          ]"
          :key="plugin.name"
          class="rounded-xl border border-dashed bg-card/40 p-5 flex flex-col gap-3 opacity-50 pointer-events-none select-none"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg bg-muted flex items-center justify-center flex-shrink-0"
            >
              <span class="text-base font-bold text-muted-foreground">{{ plugin.name[0] }}</span>
            </div>
            <div>
              <p class="font-semibold text-sm">{{ plugin.name }}</p>
              <p class="text-xs text-muted-foreground">{{ plugin.desc }}</p>
            </div>
          </div>
          <Badge variant="outline" class="text-xs w-fit">Coming soon</Badge>
        </div>
      </div>
    </section>

    <!-- ── Gmail manage sheet ──────────────────────────────────────────────── -->
    <Sheet :open="activeSheet === 'gmail'" @update:open="(v) => !v && (activeSheet = null)">
      <SheetContent class="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Gmail Integration</SheetTitle>
          <SheetDescription>Manage how JobApplica reads your inbox.</SheetDescription>
        </SheetHeader>
        <div class="mt-6 space-y-5">
          <div class="rounded-lg bg-muted/50 p-4 text-sm space-y-0.5">
            <p class="font-medium">Connected as</p>
            <p class="text-muted-foreground">{{ google?.provider_email }}</p>
          </div>
          <Separator />
          <div class="space-y-2">
            <p class="text-sm font-medium">Permissions granted</p>
            <ul class="space-y-1.5 text-xs text-muted-foreground">
              <li class="flex items-start gap-2">
                <span class="text-green-500 mt-0.5">✓</span>Read emails to detect job application
                updates
              </li>
              <li class="flex items-start gap-2">
                <span class="text-green-500 mt-0.5">✓</span>Create and apply a "JobApplica" label
              </li>
              <li class="flex items-start gap-2">
                <span class="text-green-500 mt-0.5">✓</span>Create inbox filters for matched emails
              </li>
            </ul>
          </div>
          <Separator />
          <div class="space-y-2">
            <p class="text-sm font-medium text-muted-foreground">What we never do</p>
            <ul class="space-y-1.5 text-xs text-muted-foreground">
              <li class="flex items-start gap-2">
                <span>✗</span>Read emails unrelated to job applications
              </li>
              <li class="flex items-start gap-2"><span>✗</span>Send emails on your behalf</li>
              <li class="flex items-start gap-2"><span>✗</span>Store full email body content</li>
            </ul>
          </div>
          <Separator />
          <Button
            variant="destructive"
            class="w-full"
            :disabled="disconnecting === 'google'"
            @click="disconnect('google')"
          >
            {{ disconnecting === 'google' ? 'Disconnecting…' : 'Disconnect Google account' }}
          </Button>
        </div>
      </SheetContent>
    </Sheet>

    <!-- ── Calendar manage sheet ───────────────────────────────────────────── -->
    <Sheet :open="activeSheet === 'calendar'" @update:open="(v) => !v && (activeSheet = null)">
      <SheetContent class="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Google Calendar Integration</SheetTitle>
          <SheetDescription>Manage how JobApplica syncs events to your calendar.</SheetDescription>
        </SheetHeader>
        <div class="mt-6 space-y-5">
          <div class="rounded-lg bg-muted/50 p-4 text-sm space-y-0.5">
            <p class="font-medium">Connected as</p>
            <p class="text-muted-foreground">{{ google?.provider_email }}</p>
          </div>
          <Separator />
          <div class="space-y-2">
            <p class="text-sm font-medium">Auto-creates events when status changes to</p>
            <div class="flex flex-wrap gap-2">
              <Badge variant="secondary">Phone Screen</Badge>
              <Badge variant="secondary">Interview</Badge>
              <Badge variant="secondary">Technical</Badge>
            </div>
            <p class="text-xs text-muted-foreground">
              Set an interview date on a job to trigger event creation.
            </p>
          </div>
          <Separator />
          <Button
            variant="destructive"
            class="w-full"
            :disabled="disconnecting === 'google'"
            @click="disconnect('google')"
          >
            {{ disconnecting === 'google' ? 'Disconnecting…' : 'Disconnect Google account' }}
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  </div>
</template>
