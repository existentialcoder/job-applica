<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import CityInput from '@/components/onboarding/CityInput.vue';
import EducationForm from '@/components/onboarding/EducationForm.vue';
import ExperienceForm from '@/components/onboarding/ExperienceForm.vue';
import LanguageForm from '@/components/onboarding/LanguageForm.vue';
import { Autocomplete } from '@/components/ui/autocomplete';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Combobox } from '@/components/ui/combobox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { COUNTRY_OPTIONS, DEFAULT_COMPANY_LOGO_URL, ONBOARDING_STEP } from '@/lib/constants';
import { emptyProfile, type ExperienceEntry, type Profile } from '@/lib/profile';
import { useCompaniesStore } from '@/stores/companies';
import { useOnboardingStore } from '@/stores/onboarding';
import { useProfileStore } from '@/stores/profile';
import { useResumesStore } from '@/stores/resumes';
import { useSkillStore } from '@/stores/skills';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const COUNTRIES = COUNTRY_OPTIONS.map((c) => ({ label: c, value: c }));
const CONTACTS = [
  { key: 'email', label: 'Email', placeholder: 'you@example.com', type: 'email' },
  { key: 'phone', label: 'Phone', placeholder: '+49 151 23456789', type: 'tel' },
  { key: 'linkedin_url', label: 'LinkedIn', placeholder: 'linkedin.com/in/your-name', type: 'text' },
  { key: 'github_url', label: 'GitHub', placeholder: 'github.com/your-name', type: 'text' },
  { key: 'portfolio_url', label: 'Portfolio', placeholder: 'yourname.dev', type: 'text' }
] as const;
const BASICS = ['headline', 'current_title', 'years_experience', 'summary'] as const;
type ContactKey = (typeof CONTACTS)[number]['key'] | 'city' | 'country';
type Section = 'experience' | 'education' | 'languages';

const companiesStore = useCompaniesStore();
const profileStore = useProfileStore();
const resumesStore = useResumesStore();
const onboardingStore = useOnboardingStore();
const form = ref<Profile>(emptyProfile());
// Inputs edit strings; empty ones are sent as null.
const basics = ref<Record<(typeof BASICS)[number], string>>({
  headline: '',
  current_title: '',
  years_experience: '',
  summary: ''
});
const contacts = ref<Record<ContactKey, string>>({
  email: '',
  phone: '',
  linkedin_url: '',
  github_url: '',
  portfolio_url: '',
  city: '',
  country: ''
});
const skillsStore = useSkillStore();
const newSkill = ref('');
// Which entry's form is open: index into its list, or -1 for a new one.
const editing = ref<{ section: Section; index: number } | null>(null);
const unreadableName = ref('');
const loading = ref(true);
const saving = ref(false);
const error = ref('');

const autoFilled = computed(() => form.value.auto_filled.length > 0 && !unreadableName.value);
// Skills that start with what's typed first, then ones with a word that does.
const skillSuggestions = computed(() => {
  const q = newSkill.value.trim().toLowerCase();
  if (!q) return [];
  const labels = skillsStore.available.map((s) => s.label);
  const starts = labels.filter((l) => l.toLowerCase().startsWith(q));
  const words = labels.filter((l) => !starts.includes(l) && l.toLowerCase().includes(` ${q}`));
  return [...starts, ...words].slice(0, 10).map((l) => ({ label: l, value: l }));
});

function month(value: string | null) {
  const [year, m] = (value ?? '').split('-');
  return m ? `${MONTHS[Number(m) - 1]} ${year}` : year;
}

function period(e: { start: string | null; end: string | null }, ongoing = 'present') {
  if (!e.start && !e.end) return '';
  return `${month(e.start)} – ${e.end ? month(e.end) : ongoing}`;
}

const logo = (e: ExperienceEntry) => (e.company && form.value.company_logos[e.company]) || DEFAULT_COMPANY_LOGO_URL;
const isEditing = (section: Section, index: number) =>
  editing.value?.section === section && editing.value.index === index;

function load(profile: Profile) {
  form.value = profile;
  for (const k of BASICS) {
    basics.value[k] = String(profile[k] ?? '');
  }
  for (const k of Object.keys(contacts.value) as ContactKey[]) {
    contacts.value[k] = profile.contacts[k] ?? '';
  }
}

function saveEntry<T>(list: T[], entry: T) {
  const index = editing.value?.index ?? -1;
  if (index === -1) list.push(entry);
  else list.splice(index, 1, entry);
  editing.value = null;
}

onMounted(async () => {
  const [profile] = await Promise.all([
    profileStore.fetchProfile(),
    resumesStore.fetch(),
    companiesStore.fetch(),
    // Forced: CV extraction adds skills in the background, so a cached list may be stale.
    skillsStore.refresh()
  ]);
  if (profile) load(profile);
  const resume = resumesStore.current;
  unreadableName.value = resume?.extraction === 'failed' ? resume.original_name : '';
  loading.value = false;
});

async function addSkill(label = newSkill.value) {
  newSkill.value = '';
  await skillsStore.addUserSkillByLabel(label);
}

const orNull = (v: string) => String(v).trim() || null;

async function confirm() {
  saving.value = true;
  error.value = '';
  const f = form.value;
  try {
    load(
      await profileStore.saveProfile({
        headline: orNull(basics.value.headline),
        current_title: orNull(basics.value.current_title),
        current_company: f.current_company,
        years_experience: Number(basics.value.years_experience) || null,
        summary: orNull(basics.value.summary),
        experience: f.experience,
        education: f.education,
        languages: f.languages,
        certifications: f.certifications,
        awards: f.awards,
        contacts: {
          ...f.contacts,
          ...Object.fromEntries(Object.entries(contacts.value).map(([k, v]) => [k, orNull(v)]))
        },
        confirm: true
      })
    );
    await onboardingStore.go('preferences');
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save profile';
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">{{ ONBOARDING_STEP.profile.title }}</h1>
      <p class="mt-1 text-sm text-muted-foreground">{{ ONBOARDING_STEP.profile.hint }}</p>
    </div>

    <div
      v-if="unreadableName"
      role="status"
      class="flex flex-wrap items-center gap-3 px-4 py-3.5 rounded-xl border border-border bg-muted"
    >
      <Icon name="CircleAlert" :size="18" :stroke-width="2" default-class="text-muted-foreground shrink-0" />
      <span class="flex-1 min-w-[200px] flex flex-col gap-0.5">
        <span class="text-sm font-semibold">We couldn't read {{ unreadableName }}</span>
        <span class="text-[13px] text-muted-foreground">Try a PDF or Word file with selectable text.</span>
      </span>
      <Button variant="outline" @click="onboardingStore.go('upload')">Upload another file</Button>
    </div>

    <p v-else-if="autoFilled" class="flex items-center gap-2 text-[13px] text-muted-foreground">
      <Badge variant="secondary">Auto-filled</Badge>
      Check these
    </p>

    <template v-if="!loading">
       <section class="card" aria-labelledby="basics">
        <h2 id="basics" class="section-title">Basics</h2>
        <div class="grid gap-4 md:grid-cols-2">
          <div class="field">
            <Label for="basics-headline">Headline</Label>
            <Input id="basics-headline" v-model="basics.headline" placeholder="e.g. Senior backend engineer, payments" />
          </div>
          <div class="field">
            <Label for="basics-title">Current title</Label>
            <Input id="basics-title" v-model="basics.current_title" placeholder="e.g. Senior Software Engineer" />
          </div>
          <div class="field">
            <Label for="basics-years">Years of experience</Label>
            <Input id="basics-years" v-model="basics.years_experience" type="number" placeholder="e.g. 7" />
          </div>
        </div>
        <div class="field">
          <Label for="basics-summary">Summary</Label>
          <Textarea
            id="basics-summary"
            v-model="basics.summary"
            rows="4"
            placeholder="A few sentences about your experience and what you're best at"
          />
        </div>
      </section>
      
      <section class="card" aria-labelledby="contacts">
        <h2 id="contacts" class="section-title">Contact details</h2>
        <div class="grid gap-4 md:grid-cols-2">
          <div v-for="c in CONTACTS" :key="c.key" class="field">
            <Label :for="`contact-${c.key}`">{{ c.label }}</Label>
            <Input :id="`contact-${c.key}`" v-model="contacts[c.key]" :type="c.type" :placeholder="c.placeholder" />
          </div>
          <div class="field">
            <Label for="contact-city">City</Label>
            <CityInput
              id="contact-city"
              v-model="contacts.city"
              @select="contacts.country = $event.country ?? contacts.country"
            />
          </div>
          <div class="field">
            <Label>Country</Label>
            <Combobox v-model="contacts.country" :options="COUNTRIES" placeholder="Select a country" class="h-10" />
          </div>
        </div>
      </section>

      <section class="card" aria-labelledby="experience">
        <div class="section-head">
          <h2 id="experience" class="section-title">Experience</h2>
          <Button
            v-if="!editing"
            variant="ghost"
            size="sm"
            class="text-primary"
            @click="editing = { section: 'experience', index: -1 }"
          >
            <Icon name="Plus" :size="16" :stroke-width="2" default-class="mr-1.5" />Add experience
          </Button>
        </div>
        <ExperienceForm
          v-if="isEditing('experience', -1)"
          :entry="null"
          :companies="companiesStore.companies"
          @save="saveEntry(form.experience, $event)"
          @cancel="editing = null"
        />
        <ul v-if="form.experience.length" class="flex flex-col">
          <li v-for="(e, i) in form.experience" :key="i" class="entry">
            <ExperienceForm
              v-if="isEditing('experience', i)"
              class="w-full"
              :entry="e"
              :companies="companiesStore.companies"
              @save="saveEntry(form.experience, $event)"
              @cancel="editing = null"
            />
            <template v-else>
              <span class="flex items-center gap-3 min-w-0">
                <img
                  :src="logo(e)"
                  alt=""
                  class="size-9 shrink-0 rounded-full object-contain bg-muted"
                  @error="($event.target as HTMLImageElement).src = DEFAULT_COMPANY_LOGO_URL"
                />
                <span class="flex flex-col gap-0.5 min-w-0">
                  <span class="flex items-center gap-2 text-sm font-semibold">
                    {{ e.title }}
                    <Badge v-if="!e.end" variant="secondary">Current</Badge>
                  </span>
                  <span class="text-[13px] text-muted-foreground">
                    {{ [e.company, period(e)].filter(Boolean).join(' · ') }}
                  </span>
                </span>
              </span>
              <span class="actions">
                <Button
                  variant="ghost"
                  size="icon"
                  :aria-label="`Edit ${e.title}`"
                  @click="editing = { section: 'experience', index: i }"
                >
                  <Icon name="Pencil" :size="16" :stroke-width="2" />
                </Button>
                <Button variant="ghost" size="icon" :aria-label="`Delete ${e.title}`" @click="form.experience.splice(i, 1)">
                  <Icon name="Trash2" :size="16" :stroke-width="2" />
                </Button>
              </span>
            </template>
          </li>
        </ul>
        <p v-else-if="!isEditing('experience', -1)" class="empty">Add the roles you've had, most recent first.</p>
      </section>

      <section class="card" aria-labelledby="education">
        <div class="section-head">
          <h2 id="education" class="section-title">Education</h2>
          <Button
            v-if="!editing"
            variant="ghost"
            size="sm"
            class="text-primary"
            @click="editing = { section: 'education', index: -1 }"
          >
            <Icon name="Plus" :size="16" :stroke-width="2" default-class="mr-1.5" />Add education
          </Button>
        </div>
        <EducationForm
          v-if="isEditing('education', -1)"
          :entry="null"
          @save="saveEntry(form.education, $event)"
          @cancel="editing = null"
        />
        <ul v-if="form.education.length" class="flex flex-col">
          <li v-for="(e, i) in form.education" :key="i" class="entry">
            <EducationForm
              v-if="isEditing('education', i)"
              class="w-full"
              :entry="e"
              @save="saveEntry(form.education, $event)"
              @cancel="editing = null"
            />
            <template v-else>
              <span class="flex flex-col gap-0.5 min-w-0">
                <span class="text-sm font-semibold">
                  {{ [e.degree, e.field].filter(Boolean).join(', ') || e.institution }}
                </span>
                <span class="text-[13px] text-muted-foreground">
                  {{ [e.institution, period(e, '')].filter(Boolean).join(' · ') }}
                </span>
              </span>
              <span class="actions">
                <Button
                  variant="ghost"
                  size="icon"
                  :aria-label="`Edit ${e.institution}`"
                  @click="editing = { section: 'education', index: i }"
                >
                  <Icon name="Pencil" :size="16" :stroke-width="2" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  :aria-label="`Delete ${e.institution}`"
                  @click="form.education.splice(i, 1)"
                >
                  <Icon name="Trash2" :size="16" :stroke-width="2" />
                </Button>
              </span>
            </template>
          </li>
        </ul>
        <p v-else-if="!isEditing('education', -1)" class="empty">Add your degrees or training.</p>
      </section>

      <section class="card" aria-labelledby="skills">
        <h2 id="skills" class="section-title">Skills</h2>
        <ul v-if="skillsStore.userSkills.length" class="flex flex-wrap gap-2">
          <li v-for="skill in skillsStore.userSkills" :key="skill.id">
            <Badge variant="secondary" class="gap-1.5">
            {{ skill.label }}
            <button type="button" class="flex" :aria-label="`Remove ${skill.label}`" @click="skillsStore.removeUserSkill(skill.id)">
              <Icon name="X" :size="12" :stroke-width="2" />
            </button>
            </Badge>
          </li>
        </ul>
        <form class="flex gap-2 md:w-1/2" @submit.prevent="addSkill()">
          <Autocomplete
            v-model="newSkill"
            :suggestions="skillSuggestions"
            class="flex-1"
            placeholder="Add a skill, e.g. Python"
            aria-label="Skill"
            @select="addSkill"
          />
          <Button type="submit" variant="outline" :disabled="!newSkill.trim()">Add</Button>
        </form>
      </section>

      <section class="card" aria-labelledby="languages">
        <div class="section-head">
          <h2 id="languages" class="section-title">Languages</h2>
          <Button
            v-if="!editing"
            variant="ghost"
            size="sm"
            class="text-primary"
            @click="editing = { section: 'languages', index: -1 }"
          >
            <Icon name="Plus" :size="16" :stroke-width="2" default-class="mr-1.5" />Add language
          </Button>
        </div>
        <LanguageForm
          v-if="isEditing('languages', -1)"
          :entry="null"
          @save="saveEntry(form.languages, $event)"
          @cancel="editing = null"
        />
        <ul v-if="form.languages.length" class="flex flex-col">
          <li v-for="(lang, i) in form.languages" :key="i" class="entry">
            <LanguageForm
              v-if="isEditing('languages', i)"
              class="w-full"
              :entry="lang"
              @save="saveEntry(form.languages, $event)"
              @cancel="editing = null"
            />
            <template v-else>
              <span class="text-sm">
                <span class="font-semibold">{{ lang.name }}</span>
                <span v-if="lang.level" class="text-muted-foreground"> · {{ lang.level }}</span>
              </span>
              <span class="actions">
                <Button
                  variant="ghost"
                  size="icon"
                  :aria-label="`Edit ${lang.name}`"
                  @click="editing = { section: 'languages', index: i }"
                >
                  <Icon name="Pencil" :size="16" :stroke-width="2" />
                </Button>
                <Button variant="ghost" size="icon" :aria-label="`Delete ${lang.name}`" @click="form.languages.splice(i, 1)">
                  <Icon name="Trash2" :size="16" :stroke-width="2" />
                </Button>
              </span>
            </template>
          </li>
        </ul>
        <p v-else-if="!isEditing('languages', -1)" class="empty">Add the languages you speak and how well.</p>
      </section>
    </template>

    <Teleport to="#onboarding-actions">
      <p v-if="error" role="alert" class="text-sm text-destructive">{{ error }}</p>
      <Button :disabled="loading || saving || editing !== null" @click="confirm">
        {{ saving ? 'Saving…' : form.completed ? 'Finish' : 'Continue' }}
        <Icon name="ArrowRight" :size="16" :stroke-width="2" default-class="ml-2" />
      </Button>
    </Teleport>
  </div>
</template>

<style scoped>
.card {
  @apply rounded-xl border border-border bg-card p-6 flex flex-col gap-4;
}

.section-head {
  @apply flex items-center justify-between gap-2;
}

.section-title {
  @apply text-sm font-semibold;
}

.field {
  @apply flex flex-col gap-1.5;
}

.entry {
  @apply flex items-center justify-between gap-3 py-3 border-t border-border first:border-t-0 first:pt-0;
}

.actions {
  @apply flex shrink-0 gap-1;
}

.empty {
  @apply text-sm text-muted-foreground;
}
</style>
