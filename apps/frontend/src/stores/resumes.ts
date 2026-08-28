import { defineStore } from 'pinia';
import { ref } from 'vue';
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
    loaded,
    newResumeUpload,
    fetch,
    setDefault,
    addResume,
    deleteResume,
    refresh
  };
});
