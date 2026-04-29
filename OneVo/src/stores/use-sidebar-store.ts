import { create } from 'zustand';

interface SidebarStore {
  isExpanded: boolean;
  activePillar: string | null;
  setActivePillar: (pillar: string | null) => void;
  collapse: () => void;
}

export const useSidebarStore = create<SidebarStore>((set) => ({
  isExpanded: false,
  activePillar: null,
  setActivePillar: (pillar) => set({ activePillar: pillar, isExpanded: pillar !== null }),
  collapse: () => set({ activePillar: null, isExpanded: false }),
}));
