import type { SourceCategory } from '../types/source'

export const MAP_CATEGORY_COLORS = {
  industrial: '#F97316',
  natural_biomass: '#22C55E',
  persistent: '#A855F7',
  abnormal: '#EF4444',
  unknown: '#F59E0B',
  firms_detection: '#3B82F6',
} as const

export const MAP_CATEGORY_LABELS = {
  industrial: 'Industrial',
  natural_biomass: 'Natural / Biomass',
  persistent: 'Persistent',
  abnormal: 'Abnormal',
  unknown: 'Unknown',
  firms_detection: 'FIRMS Detection',
} as const

export const MAP_CATEGORY_SHAPES = {
  industrial: 'circle',
  natural_biomass: 'square',
  persistent: 'triangle',
  abnormal: 'diamond',
  unknown: 'hexagon',
  firms_detection: 'star',
} as const

export type MapCategory = keyof typeof MAP_CATEGORY_COLORS

export function getMapCategory(category: SourceCategory): MapCategory {
  if (category === 'industrial') return 'industrial'
  if (category === 'natural_biomass') return 'natural_biomass'
  if (category === 'persistent') return 'persistent'
  if (category === 'abnormal') return 'abnormal'
  if (category === 'unknown') return 'unknown'
  return 'firms_detection'
}

export function getShapeClipPath(shape: (typeof MAP_CATEGORY_SHAPES)[MapCategory]) {
  switch (shape) {
    case 'circle':
      return 'circle(50%)'
    case 'square':
      return 'inset(0)'
    case 'triangle':
      return 'polygon(50% 0, 100% 100%, 0 100%)'
    case 'diamond':
      return 'polygon(50% 0, 100% 50%, 50% 100%, 0 50%)'
    case 'hexagon':
      return 'polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%)'
    case 'star':
      return 'polygon(50% 0, 61% 35%, 98% 35%, 68% 57%, 79% 92%, 50% 70%, 21% 92%, 32% 57%, 2% 35%, 39% 35%)'
  }
}
