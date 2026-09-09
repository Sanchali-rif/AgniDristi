import { create } from 'zustand'

export type DatasetMode = 'FIRMS' | 'VNF'

type SourceState = {
  selectedSourceId: string | null
  isPanelOpen: boolean
  isPanelCollapsed: boolean
  datasetMode: DatasetMode
  activeLayerIds: string[]
  setSelectedSourceId: (sourceId: string | null) => void
  setPanelOpen: (isOpen: boolean) => void
  setPanelCollapsed: (collapsed: boolean) => void
  togglePanelCollapse: () => void
  setDatasetMode: (mode: DatasetMode) => void
  toggleLayerId: (id: string) => void
  setAllLayers: (ids: string[]) => void
  openPanel: (sourceId: string) => void
  closePanel: () => void
}

export const useSourceStore = create<SourceState>((set) => ({
  selectedSourceId: null,
  isPanelOpen: false,
  isPanelCollapsed: false,
  datasetMode: 'FIRMS',
  activeLayerIds: ['firms', 'persistent', 'facilities'],
  setSelectedSourceId: (selectedSourceId) => set({ selectedSourceId }),
  setPanelOpen: (isPanelOpen) => set({ isPanelOpen }),
  setPanelCollapsed: (isPanelCollapsed) => set({ isPanelCollapsed }),
  togglePanelCollapse: () => set((s) => ({ isPanelCollapsed: !s.isPanelCollapsed })),
  setDatasetMode: (datasetMode) => set({ datasetMode }),
  toggleLayerId: (id) => set((s) => ({
    activeLayerIds: s.activeLayerIds.includes(id)
      ? s.activeLayerIds.filter((item) => item !== id)
      : [...s.activeLayerIds, id],
  })),
  setAllLayers: (activeLayerIds) => set({ activeLayerIds }),
  openPanel: (selectedSourceId) => set({ selectedSourceId, isPanelOpen: true, isPanelCollapsed: false }),
  closePanel: () => set({ isPanelOpen: false }),
}))
