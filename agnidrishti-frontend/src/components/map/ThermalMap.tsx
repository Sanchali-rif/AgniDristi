import { useState } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import { useShallow } from 'zustand/react/shallow'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import { useFilterStore } from '../../stores/filterStore'
import { useSources } from '../../services/sourceService'
import { ClusteredMarkers } from './ClusteredMarkers'
import { MapLegend } from './MapLegend'

const mapCenter: [number, number] = [24.15, 87.6]
const mapTileUrl = import.meta.env.VITE_MAP_TILE_URL || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const satelliteTileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

export function ThermalMap() {
  const [isSatellite, setIsSatellite] = useState(false)
  const filters = useFilterStore(
    useShallow((s) => ({
      sourceId: s.sourceId, location: s.location, facility: s.facility,
      from: s.dateRange.from, to: s.dateRange.to, sourceType: s.sourceType,
      industryType: s.industryType, anomalyLevel: s.anomalyLevel,
      confidenceLevel: s.confidenceLevel, persistenceStatus: s.persistenceStatus,
    }))
  )
  const resetFilters = useFilterStore((s) => s.reset)
  const { data: sources = [], isLoading, isError } = useSources(filters)
  const tileUrl = isSatellite ? satelliteTileUrl : mapTileUrl

  return (
    <section className="group relative overflow-hidden rounded-none border-2 border-black bg-surface shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all duration-500 hover:-translate-y-0.5" aria-label="Thermal source map">
      <MapContainer center={mapCenter} zoom={6} scrollWheelZoom className="h-[32rem] w-full transition-transform duration-700 ease-out group-hover:scale-[1.008]">
        <TileLayer key={tileUrl} url={tileUrl} attribution={isSatellite ? 'Tiles &copy; Esri' : '&copy; OpenStreetMap contributors'} />
        {!isLoading && !isError && sources.length > 0 && <ClusteredMarkers sources={sources} />}
      </MapContainer>
      <div className="absolute right-4 top-4 z-[1000] flex border-2 border-black bg-black p-0.5 shadow-md">
        <button type="button" onClick={() => setIsSatellite(false)} aria-pressed={!isSatellite}
          className={`px-3 py-1.5 text-xs font-black uppercase tracking-wider transition-colors ${!isSatellite ? 'bg-[#d8f5a9] text-black' : 'text-white hover:bg-zinc-800'}`}>Map</button>
        <button type="button" onClick={() => setIsSatellite(true)} aria-pressed={isSatellite}
          className={`px-3 py-1.5 text-xs font-black uppercase tracking-wider transition-colors ${isSatellite ? 'bg-[#d8f5a9] text-black' : 'text-white hover:bg-zinc-800'}`}>Satellite</button>
      </div>

      <MapLegend />
      {isLoading && <div className="absolute inset-0 z-[1000] flex items-center justify-center bg-surface/65 backdrop-blur-[1px]"><div className="w-56 border-2 border-black bg-surface p-4 shadow" role="status"><div className="h-3 w-28 animate-pulse rounded-none bg-black/20" /><div className="mt-3 h-2 w-full animate-pulse rounded-none bg-black/20" /><div className="mt-2 h-2 w-4/5 animate-pulse rounded-none bg-black/20" /></div></div>}
      {isError && <p className="absolute left-1/2 top-1/2 z-[1000] -translate-x-1/2 border-2 border-black bg-surface px-3 py-2 text-sm font-bold text-danger shadow">Unable to load sources.</p>}
      {!isLoading && !isError && sources.length === 0 && (
        <div className="absolute inset-0 z-[1000] flex items-center justify-center bg-surface/80 p-6 text-center">
          <div className="border-2 border-black bg-surface p-5 shadow">
            <p className="text-sm font-bold text-text-primary uppercase">No thermal sources found</p>
            <p className="mt-1 text-xs text-text-secondary">Try broadening the current filters.</p>
            <button type="button" onClick={resetFilters} className="mt-3 border-2 border-black bg-black px-3 py-2 text-xs font-black uppercase text-white hover:bg-zinc-800">Reset filters</button>
          </div>
        </div>
      )}
    </section>
  )
}


