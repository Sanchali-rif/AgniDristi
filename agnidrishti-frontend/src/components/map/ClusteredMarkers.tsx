import { useEffect } from 'react'
import L from 'leaflet'
import { useMap } from 'react-leaflet'
import { useSourceStore } from '../../stores/sourceStore'
import type { RecentFirmsDetection, ThermalObject, VnfMapDetection } from '../../types/dashboard'

function getIndustryCategory(label: string | null | undefined): string {
  if (!label) return 'Other Industrial'
  const normalized = label.toUpperCase()
  if (normalized.includes('OIL') || normalized.includes('GAS') || normalized.includes('FLARE')) return 'Oil & Gas'
  if (normalized.includes('METAL') || normalized.includes('STEEL')) return 'Metallurgical'
  if (normalized.includes('MINING') || normalized.includes('EXTRACT')) return 'Mining & Extraction'
  return 'Other Industrial'
}

const industryColors: Record<string, string> = {
  'Oil & Gas': '#dc2626',
  Metallurgical: '#ea580c',
  'Mining & Extraction': '#9333ea',
  'Other Industrial': '#2563eb',
}
const hasValue = (input: unknown) => input !== null && input !== undefined && input !== ''
const shown = (input: unknown) => hasValue(input) ? String(input) : 'Not available'
const objectColor = (object: ThermalObject) => industryColors[getIndustryCategory(object.classification_label || object.industry_name)] || '#2563eb'

function ensurePane(map: L.Map, name: string, zIndex: number) {
  const pane = map.getPane(name) ?? map.createPane(name)
  pane.style.zIndex = String(zIndex)
  return name
}

function firmsIcon() {
  return L.divIcon({
    className: 'firms-marker-dot',
    iconSize: [16, 16],
    iconAnchor: [8, 8],
    html: '<span style="display:block;width:16px;height:16px;background:#0891b2;border:2px solid #082f49;box-shadow:1.5px 1.5px 0 #082f49"></span>',
  })
}

function tooltip(title: string, rows: Array<[string, unknown, string?, boolean?]>) {
  const root = document.createElement('div')
  const heading = document.createElement('strong')
  heading.textContent = title
  root.appendChild(heading)
  rows.filter(([, value, , optional]) => !optional || hasValue(value)).forEach(([label, value, suffix = '']) => {
    const row = document.createElement('div')
    row.textContent = `${label}: ${shown(value)}${hasValue(value) ? suffix : ''}`
    root.appendChild(row)
  })
  return root
}

const lazyTooltip = (title: string, rows: Array<[string, unknown, string?, boolean?]>) => () => tooltip(title, rows)

export function ClusteredMarkers({ objects, detections, vnfDetections }: { objects: ThermalObject[]; detections: RecentFirmsDetection[]; vnfDetections: VnfMapDetection[] }) {
  const map = useMap()
  const openPanel = useSourceStore((state) => state.openPanel)
  const activeLayerIds = useSourceStore((state) => state.activeLayerIds)

  useEffect(() => {
    const firmsPane = ensurePane(map, 'firms-detections-pane', 620)
    const radiusPane = ensurePane(map, 'thermal-radius-pane', 640)
    const objectPane = ensurePane(map, 'thermal-objects-pane', 660)
    const vnfPane = ensurePane(map, 'vnf-detections-pane', 630)
    const radiusLayer = L.layerGroup()
    const objectLayer = L.layerGroup()
    const firmsLayer = L.layerGroup()
    const vnfLayer = L.layerGroup()

    objects.forEach((object) => {
      const color = objectColor(object)
      if (object.object_radius_m != null && Number.isFinite(object.object_radius_m) && object.object_radius_m > 0) {
        radiusLayer.addLayer(L.circle([object.latitude, object.longitude], {
          radius: object.object_radius_m,
          color,
          fillColor: color,
          fillOpacity: 0.12,
          weight: 1.5,
          pane: radiusPane,
        }))
      }

      const industryLabel = object.classification_label || object.industry_name || 'Unclassified industry'
      const marker = L.circleMarker([object.latitude, object.longitude], {
        radius: 6,
        color: '#111827',
        weight: 2,
        fillColor: color,
        fillOpacity: 1,
        pane: objectPane,
      })
      marker.bindTooltip(lazyTooltip(industryLabel, [
        ['Object', object.object_uid],
        ['GEM exact type', object.gem_industry_exact_type, '', true],
        ['GEM facility', object.gem_facility_name, '', true],
        ['GEM match radius', object.gem_match_radius_m, ' m', true],
      ]), { className: 'thermal-tooltip' })
      marker.on('click', () => openPanel(object.object_uid))
      objectLayer.addLayer(marker)
    })

    detections.forEach((detection) => {
      const marker = L.marker([detection.latitude, detection.longitude], {
        icon: firmsIcon(),
        pane: firmsPane,
        title: `Persistent FIRMS detection ${detection.firms_uid}`,
      })
      marker.bindTooltip(lazyTooltip(`FIRMS ${detection.firms_uid}`, [
        ['FRP', detection.frp],
        ['Brightness T4', detection.bright_ti4, ' K'],
        ['Brightness T5', detection.bright_ti5, ' K'],
        ['Confidence', detection.confidence],
        ['Acquisition time', detection.acq_time],
        ['Matched object', detection.matched_object_uid, '', true],
      ]), { className: 'thermal-tooltip' })
      if (detection.matched_object_uid) marker.on('click', () => openPanel(detection.matched_object_uid!))
      firmsLayer.addLayer(marker)
    })

    vnfDetections.forEach((detection) => {
      const marker = L.circleMarker([detection.latitude, detection.longitude], {
        radius: 4,
        color: '#3f3f46',
        weight: 1.5,
        fillColor: '#a1a1aa',
        fillOpacity: 0.9,
        pane: vnfPane,
      })
      marker.bindTooltip(lazyTooltip(`VNF ${detection.id_key || detection.id}`, [
        ['Source state', detection.processing_state],
        ['Position source', detection.position_source],
        ['Matched object', detection.matched_object_uid, '', true],
        ['Primary temperature', detection.temp_primary, ' K'],
        ['Scan date', detection.mscan_date],
        ['Raw latitude', detection.raw_latitude, '', true],
        ['Raw longitude', detection.raw_longitude, '', true],
      ]), { className: 'thermal-tooltip' })
      if (detection.matched_object_uid) marker.on('click', () => openPanel(detection.matched_object_uid!))
      vnfLayer.addLayer(marker)
    })

    if (activeLayerIds.includes('facilities')) map.addLayer(radiusLayer)
    if (activeLayerIds.includes('modis')) map.addLayer(vnfLayer)
    if (activeLayerIds.includes('firms')) map.addLayer(firmsLayer)
    if (activeLayerIds.includes('persistent')) map.addLayer(objectLayer)

    const coordinates = [
      ...objects.map((object) => [object.latitude, object.longitude] as [number, number]),
      ...detections.map((detection) => [detection.latitude, detection.longitude] as [number, number]),
      ...vnfDetections.map((detection) => [detection.latitude, detection.longitude] as [number, number]),
    ].filter(([latitude, longitude]) => Number.isFinite(latitude) && Number.isFinite(longitude))
    if (coordinates.length > 0) {
      map.fitBounds(L.latLngBounds(coordinates).pad(0.08), { maxZoom: 10, animate: false })
    }

    return () => {
      map.removeLayer(radiusLayer)
      map.removeLayer(vnfLayer)
      map.removeLayer(objectLayer)
      map.removeLayer(firmsLayer)
    }
  }, [map, objects, detections, vnfDetections, openPanel, activeLayerIds])

  return null
}
