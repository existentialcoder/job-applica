import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import dataservice from '@/lib/dataservice';
import { toast } from '@/lib/toast';
import type { SkillData } from '@/lib/types';

export const useSkillStore = defineStore('skills', () => {
  const skills = ref<SkillData[]>([]);
  const userSkills = ref<SkillData[]>([]);
  const loaded = ref(false);
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
        const [skillsData, userSkillsData] = await Promise.all([
          dataservice.getSkills(),
          dataservice.getUserSkills()
        ]);

        skills.value = Array.isArray(skillsData) ? skillsData : [];
        userSkills.value = Array.isArray(userSkillsData) ? userSkillsData : [];
        loaded.value = true;
      } finally {
        inFlight = null;
      }
    })();
    return inFlight;
  }

  async function addUserSkill(skillId: number): Promise<boolean> {
    try {
      userSkills.value = await dataservice.addUserSkill(skillId);
      return true;
    } catch {
      toast.error('Failed to add skill');
      return false;
    }
  }

  // Skills the user could still add: the catalog minus what they already have.
  const available = computed(() => skills.value.filter((s) => !userSkills.value.some((u) => u.id === s.id)));

  /** Add a skill by its label, creating it in the catalog first if nobody has used it yet. */
  async function addUserSkillByLabel(label: string): Promise<boolean> {
    const name = label.trim();
    if (!name) return false;
    let skill = skills.value.find((s) => s.label.toLowerCase() === name.toLowerCase());
    if (!skill) {
      try {
        skill = await dataservice.createSkill(name);
      } catch {
        toast.error('Failed to add skill');
        return false;
      }
      skills.value.push(skill);
    }
    return addUserSkill(skill.id);
  }

  async function removeUserSkill(skillId: number): Promise<boolean> {
    try {
      userSkills.value = await dataservice.removeUserSkill(skillId);
      return true;
    } catch {
      toast.error('Failed to remove skill');
      return false;
    }
  }

  async function refresh() {
    return fetch(true);
  }

  return {
    skills,
    userSkills,
    available,
    loaded,
    fetch,
    refresh,
    addUserSkill,
    addUserSkillByLabel,
    removeUserSkill
  };
});
