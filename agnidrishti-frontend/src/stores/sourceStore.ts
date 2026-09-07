import { create } from 'zustand'

type SourceState = {
  selectedSourceId: string | null
  isPanelOpen: boolean
  setSelectedSourceId: (sourceId: string | null) => void
  setPanelOpen: (isOpen: boolean) => void
  openPanel: (sourceId: string) => void
  closePanel: () => void
}

export const useSourceStore = create<SourceState>((set) => ({
  selectedSourceId: null,
  isPanelOpen: false,
  setSelectedSourceId: (selectedSourceId) => set({ selectedSourceId }),
  setPanelOpen: (isPanelOpen) => set({ isPanelOpen }),
  openPanel: (selectedSourceId) => set({ selectedSourceId, isPanelOpen: true }),
  closePanel: () => set({ isPanelOpen: false }),
}))
