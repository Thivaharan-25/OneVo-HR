import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WorkforceFilters {
  department: string | null;
  status: string[];
}

interface FilterStore {
  workforce: WorkforceFilters;
  setWorkforceFilters: (filters: Partial<WorkforceFilters>) => void;
  resetFilters: () => void;
}

const defaults: WorkforceFilters = { department: null, status: [] };

export const useFilterStore = create<FilterStore>()(
  persist(
    (set) => ({
      workforce: defaults,
      setWorkforceFilters: (filters) =>
        set(state => ({ workforce: { ...state.workforce, ...filters } })),
      resetFilters: () => set({ workforce: defaults }),
    }),
    { name: 'onevo-filters' }
  )
);
