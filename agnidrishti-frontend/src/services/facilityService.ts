import { useQuery } from '@tanstack/react-query'
import { axiosClient } from '../lib/axiosClient'

export interface NearbyFacility {
  name: string
  type: string
  industry: string
  distanceKm: number
  direction: string
  nearbyInfrastructure: string
}

export function useNearbyFacilities(sourceId?: string | null) {
  return useQuery({
    queryKey: ['nearby-facilities', sourceId],
    enabled: Boolean(sourceId),
    queryFn: async (): Promise<NearbyFacility[]> => {
      if (!sourceId) throw new Error('Source ID is required')
      try {
        const res = await axiosClient.get<NearbyFacility[]>(
          `/sources/${encodeURIComponent(sourceId)}/facilities`
        )
        return res.data
      } catch {
        return []
      }
    },
  })
}
