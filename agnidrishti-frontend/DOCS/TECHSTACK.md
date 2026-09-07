# TECHSTACK.md — AgniDrishti Frontend

## Overall Stack

The AgniDrishti frontend is a **read-heavy geospatial intelligence dashboard**. It renders data produced by the Backend API (FastAPI, out of scope for this document) — it does not run clustering, classification, or thermal-fingerprinting itself. The stack is chosen for: (1) fast build time given the hackathon deadline, (2) map/chart performance at ~1,000+ markers, and (3) a professional "command-center" visual register appropriate for an NTRO-facing tool.

| Layer | Technology (single choice) | Why |
|---|---|---|
| UI framework | React.js | Already committed on the Technical Approach slide's tech stack |
| Build tool | Vite | Fast dev server, minimal config, no SSR needed since this is an internal dashboard, not a public SEO site |
| Styling | Tailwind CSS | Utility classes map directly to the design tokens below, fast to theme dark/light |
| GIS / Map | Leaflet + React-Leaflet | Free, no API key required, handles 1,000+ clustered markers with `leaflet.markercluster` |
| Charts | Recharts | Idiomatic React API, sufficient for line/bar/histogram needs (Activity Timeline, Thermal Fingerprint, Anomaly Detection) |
| Icons | Lucide React | Single consistent icon set across nav, KPI cards, badges |
| Map tiles | Leaflet tile layers (e.g. OpenStreetMap / Esri satellite) | Free tile providers, no vendor lock-in |
| State (client) | Zustand | Lightweight; holds selected source, active filters, theme toggle — no need for Redux at this scale |
| Server state | React Query (TanStack Query) | Caching, polling, and loading/error states for all Backend API calls |
| Routing | React Router | Multi-page structure, one route per sidebar item (confirmed) |
| Animation | Framer Motion (structural transitions) + React Bits (decorative, sparing use) | Framer Motion for panel slide-ins/page transitions; React Bits used only where explicitly decorative (e.g. one hero/loading effect), not for data components |
| Forms/tables/dialogs | Origin UI | Copy-paste React + Tailwind components for Filters panel, Source Snapshot, Alerts list, Nearby Facilities table |
| Timeline component | Kibo UI | Historical Activity / Source Investigation history view |
| Nav/sidebar | Origin UI | Top nav bar and sidebar navigation shell |
| KPI/stat cards | Magic UI | Total/Persistent/New/Abnormal/Industrial/High-Risk cards |

## Design Tokens

### Light Theme
| Token | Value |
|---|---|
| Background | `#F8FAFC` |
| Surface / Card | `#FFFFFF` |
| Border | `#E2E8F0` |
| Accent / Brand | `#F97316` |
| Primary Text | `#0F172A` |
| Secondary Text | `#64748B` |
| Success | `#16A34A` |
| Warning | `#D97706` |
| Danger | `#DC2626` |
| Info | `#2563EB` |
| UI Font | Inter |
| Monospace Font | JetBrains Mono |
| Border Radius | 8px / `rounded-lg` |

### Dark Theme
| Token | Value |
|---|---|
| Background | `#0B1220` |
| Surface / Card | `#111C2E` |
| Border | `#24344D` |
| Accent / Brand | `#F97316` |
| Primary Text | `#F8FAFC` |
| Secondary Text | `#94A3B8` |
| Success | `#22C55E` |
| Warning | `#F59E0B` |
| Danger | `#EF4444` |
| Info | `#3B82F6` |
| UI Font | Inter |
| Monospace Font | JetBrains Mono |
| Border Radius | 8px / `rounded-lg` |

### Map Category Colors (both themes — fixed, not theme-dependent)
| Category | Color |
|---|---|
| Industrial | `#F97316` |
| Natural / Biomass | `#22C55E` |
| Persistent | `#A855F7` |
| Abnormal | `#EF4444` |
| Unknown | `#F59E0B` |
| FIRMS Detection | `#3B82F6` |

**Implementation note:** Tailwind config defines these as CSS variables (`--color-bg`, `--color-surface`, etc.) switched via a `data-theme` attribute on `<html>`, toggled through a Zustand `themeStore`. Map category colors are defined separately as constants in `lib/mapColors.ts` since they carry semantic meaning independent of light/dark mode.

**Accessibility note:** Map legend must pair each category color with a distinct marker shape (not color alone) per earlier UX review — required for color-blind safety even though exact shapes are `TBD` at implementation time (default: circle/square/triangle/diamond/hexagon/star rotation).

## Numeric Formatting

All KPI values, confidence scores, and coordinates render in **JetBrains Mono** for tabular alignment. Confidence scores capped 0–100%; anomaly scores requiring >100% display as multiplier format (`1.8×`) per earlier design correction — never raw percentages over 100.

## Data Freshness / Disclosure Requirement

Per project constraint: UI must visually separate **FIRMS (live daily feed)** from **VNF (model-training data only, not live)**. Implementation: a small `<DataSourceBadge>` component (Origin UI badge base) rendered near the KPI bar and inside Source Snapshot, reading e.g. "Live: FIRMS · Trained on: VNF" with a tooltip explaining ~7–10hr latency and 375–750m resolution. This is a fixed UI requirement, not `TBD`.

## Package List (initial `package.json` dependencies)

```
react, react-dom, react-router-dom
leaflet, react-leaflet, leaflet.markercluster
recharts
lucide-react
zustand
@tanstack/react-query
framer-motion
tailwindcss, postcss, autoprefixer
```

Origin UI, Kibo UI, and Magic UI components are copy-paste (not npm installs) — vendored directly into `components/ui/` per their respective usage patterns; React Bits components likewise copy-pasted only where used, not bulk-installed.

## Explicitly Deferred / TBD

- **Backend API contract / data shape** — no sample response provided yet. Placeholder TypeScript interfaces defined in `ARCHITECTURE.md` §7 (`types/`), to be replaced once the Backend API (FastAPI) is available. All service functions in `services/` are written against these placeholder types now.
- **Auth flow** — login screen scaffolded but token handling logic marked `TBD` pending backend auth endpoint.
- **Real-time alerts mechanism** — polling via React Query (`refetchInterval`) used for MVP; WebSocket/SSE upgrade is a future enhancement, not required for the hackathon demo since alert volume is low.
