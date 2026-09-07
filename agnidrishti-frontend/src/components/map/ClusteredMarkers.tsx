import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.markercluster'
import { useSourceStore } from '../../stores/sourceStore'
import type { SourceSummary } from '../../types/source'
import {
  getMapCategory,
  getShapeClipPath,
  MAP_CATEGORY_COLORS,
  MAP_CATEGORY_SHAPES,
} from '../../lib/mapColors'

function createMarkerIcon(source: SourceSummary) {
  const category = getMapCategory(source.category)
  const color = MAP_CATEGORY_COLORS[category]
  const shape = MAP_CATEGORY_SHAPES[category]

  return L.divIcon({
    className: 'thermal-marker',
    html: `<span style="display:block;width:16px;height:16px;background:${color};clip-path:${getShapeClipPath(shape)};border:2px solid white;box-shadow:0 1px 4px rgba(15,23,42,.45)"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  })
}

export function ClusteredMarkers({ sources }: { sources: SourceSummary[] }) {
  const map = useMap()
  const openPanel = useSourceStore((state) => state.openPanel)

  useEffect(() => {
    const clusterGroup = (L as unknown as { markerClusterGroup: () => L.LayerGroup }).markerClusterGroup()

    sources.forEach((source) => {
      const marker = L.marker([source.lat, source.lon], {
        icon: createMarkerIcon(source),
        title: source.id,
        alt: `${source.id}, ${source.category}`,
      })
      marker.bindTooltip(`${source.id} · ${source.industrySubtype ?? source.category} · ${source.confidence}% confidence`, { direction: 'top' })
      marker.on('click', () => openPanel(source.id))
      clusterGroup.addLayer(marker)
    })

    map.addLayer(clusterGroup)
    return () => { map.removeLayer(clusterGroup) }
  }, [map, openPanel, sources])

  return null
}
