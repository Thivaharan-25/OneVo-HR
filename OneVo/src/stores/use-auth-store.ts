import { create } from 'zustand';

export interface User {
  id: string;
  email: string;
  fullName: string;
  avatarUrl: string | null;
  tenantId: string;
  activeEntityId: string;
}

interface AuthStore {
  user: User | null;
  permissions: string[];
  features: string[];
  hasPermission: (permission: string) => boolean;
  hasFeature: (feature: string) => boolean;
  setAuth: (user: User, permissions: string[], features: string[]) => void;
  setActiveEntity: (entityId: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  permissions: [],
  features: [],
  hasPermission: (permission) => get().permissions.includes(permission),
  hasFeature: (feature) => get().features.includes(feature),
  setAuth: (user, permissions, features) => set({ user, permissions, features }),
  setActiveEntity: (entityId) =>
    set(state => state.user ? { user: { ...state.user, activeEntityId: entityId } } : {}),
  clear: () => set({ user: null, permissions: [], features: [] }),
}));
