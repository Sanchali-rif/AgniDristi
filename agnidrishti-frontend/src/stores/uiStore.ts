import { create } from 'zustand'

interface UIStore {
  sidebarOpen: boolean
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
}

const getInitialSidebarState = () => {
  if (typeof window !== 'undefined') {
    return window.innerWidth >= 768
  }
  return true
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: getInitialSidebarState(),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}))
