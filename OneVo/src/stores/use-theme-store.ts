import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';

interface ThemeStore {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => {
        set({ theme });
        const root = document.documentElement;
        if (theme === 'dark') root.setAttribute('data-theme', 'dark');
        else if (theme === 'light') root.removeAttribute('data-theme');
        else {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          prefersDark ? root.setAttribute('data-theme', 'dark') : root.removeAttribute('data-theme');
        }
      },
    }),
    { name: 'onevo-theme' }
  )
);
