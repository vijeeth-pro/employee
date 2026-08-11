import { create } from "zustand";

interface AppState {
  themeMode: "light" | "dark";
  collapsedSider: boolean;
  refreshTrigger: number;
  toggleTheme: () => void;
  toggleSider: () => void;
  triggerRefresh: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  themeMode: "light",
  collapsedSider: false,
  refreshTrigger: 0,

  toggleTheme: () =>
    set((state) => ({
      themeMode: state.themeMode === "light" ? "dark" : "light",
    })),

  toggleSider: () =>
    set((state) => ({
      collapsedSider: !state.collapsedSider,
    })),

  triggerRefresh: () =>
    set((state) => ({
      refreshTrigger: state.refreshTrigger + 1,
    })),
}));
