import { create } from 'zustand'

export type DateRange = {
  from: string
  to: string
}

export type FilterState = {
  sourceId: string
  location: string
  facility: string
  dateRange: DateRange
  sourceType: string
  industryType: string
  anomalyLevel: string
  confidenceLevel: string
  persistenceStatus: string
  setSourceId: (sourceId: string) => void
  setLocation: (location: string) => void
  setFacility: (facility: string) => void
  setDateRange: (dateRange: DateRange) => void
  setSourceType: (sourceType: string) => void
  setIndustryType: (industryType: string) => void
  setAnomalyLevel: (anomalyLevel: string) => void
  setConfidenceLevel: (confidenceLevel: string) => void
  setPersistenceStatus: (persistenceStatus: string) => void
  reset: () => void
}

const initialFilters = {
  sourceId: '',
  location: '',
  facility: '',
  dateRange: { from: '', to: '' },
  sourceType: '',
  industryType: '',
  anomalyLevel: '',
  confidenceLevel: '',
  persistenceStatus: '',
}

export const useFilterStore = create<FilterState>((set) => ({
  ...initialFilters,
  setSourceId: (sourceId) => set({ sourceId }),
  setLocation: (location) => set({ location }),
  setFacility: (facility) => set({ facility }),
  setDateRange: (dateRange) => set({ dateRange }),
  setSourceType: (sourceType) => set({ sourceType }),
  setIndustryType: (industryType) => set({ industryType }),
  setAnomalyLevel: (anomalyLevel) => set({ anomalyLevel }),
  setConfidenceLevel: (confidenceLevel) => set({ confidenceLevel }),
  setPersistenceStatus: (persistenceStatus) => set({ persistenceStatus }),
  reset: () => set(initialFilters),
}))
