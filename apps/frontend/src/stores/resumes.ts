import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import dataservice from '@/lib/dataservice';
import { toast } from '@/lib/toast';
import type { ResumeData } from '@/lib/types';

export const useResumesStore = defineStore('resumes', () => {
  const resumes = ref<ResumeData[]>([]);
  const loaded = ref(false);
  const newResumeUpload = ref(false);
  let inFlight: Promise<void> | null = null;

  async function fetch(force = false) {
    if (loaded.value && !force) {
      return;
    }
    if (inFlight) {
      return inFlight;
    }
    inFlight = (async () => {
      try {
        const result = await dataservice.getResumes();
        resumes.value = Array.isArray(result) ? result : [];
        loaded.value = true;
      } finally {
        inFlight = null;
      }
    })();
    return inFlight;
  }

  async function deleteResume(resumeId: number) {
    try {
      await dataservice.deleteResume(resumeId);
      resumes.value = resumes.value.filter((r) => r.id !== resumeId);
      toast.success('CV deleted');
    } catch {
      toast.error('Failed to delete CV');
    }
  }

  async function addResume(resumeFile: File) {
    newResumeUpload.value = true;

    try{
      const resume = await dataservice.uploadResume(resumeFile);
      resumes.value.unshift(resume);
      toast.success('CV uploaded successfully');
    } catch (err: any) {
      toast.error(err.message ?? 'Upload failed');
    }
    newResumeUpload.value = false;
  }

  // The CV that represents the user: their default one, else the latest.
  const current = computed(() => resumes.value.find((r) => r.is_default) ?? resumes.value[0] ?? null);

  function remember(resume: ResumeData, replacing?: number) {
    resumes.value = [resume, ...resumes.value.filter((r) => r.id !== resume.id && r.id !== replacing)];
  }

  /** Load one CV (e.g. to follow its extraction) and keep the list in step. Throws on failure. */
  async function get(resumeId: number): Promise<ResumeData> {
    const resume = await dataservice.getResume(resumeId);
    resumes.value = resumes.value.map((r) => (r.id === resume.id ? resume : r));
    return resume;
  }

  /** Upload a CV; unlike addResume, failures are thrown for the caller to show. */
  async function upload(file: File): Promise<ResumeData> {
    const resume = await dataservice.uploadResume(file);
    remember(resume);
    return resume;
  }

  /** Swap a CV for a new file; the server rebuilds the profile from it. Throws on failure. */
  async function replace(resumeId: number, file: File): Promise<ResumeData> {
    const resume = await dataservice.replaceResume(resumeId, file);
    remember(resume, resumeId);
    return resume;
  }

  async function setDefault(resumeId: number) {
    try {
      await dataservice.setDefaultResume(resumeId);
      resumes.value = resumes.value.map((r) => ({ ...r, is_default: r.id === resumeId }));
    } catch {
      toast.error('Failed to set default');
    }
  }

  async function refresh() {
    return fetch(true);
  }

  return {
    resumes,
    current,
    get,
    upload,
    replace,
    loaded,
    newResumeUpload,
    fetch,
    setDefault,
    addResume,
    deleteResume,
    refresh
  };
});
