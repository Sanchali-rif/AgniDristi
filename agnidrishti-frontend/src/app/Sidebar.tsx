import { useEffect, useRef, useState } from 'react'
import { AlertCircle, Bell, FileSearch, FileText, Layers, LayoutDashboard, Search, Settings, TrendingUp, X } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import gsap from 'gsap'
import { useUIStore } from '../stores/uiStore'

const sections = [
  { label: 'GENERAL', items: [{ label: 'Dashboard', to: '/dashboard', end: true, icon: LayoutDashboard }, { label: 'Search & Discovery', to: '/search', icon: Search }, { label: 'Source Investigation', to: '/investigation', icon: FileSearch }, { label: 'Event Assessment', to: '/assessment', icon: AlertCircle }, { label: 'Change & Anomaly', to: '/anomaly', icon: TrendingUp }, { label: 'Alerts', to: '/alerts', icon: Bell }] },
  { label: 'REPORTING', items: [{ label: 'Intelligence Reports', to: '/reports', icon: FileText }, { label: 'Data Layers', to: '/data-layers', icon: Layers }] },
  { label: 'SYSTEM', items: [{ label: 'System / Model', to: '/system', icon: Settings }] },
]

export function Sidebar() {
  const sidebarOpen = useUIStore((state) => state.sidebarOpen)
  const toggleSidebar = useUIStore((state) => state.toggleSidebar)
  const [shouldRender, setShouldRender] = useState(sidebarOpen)
  const mobileRef = useRef<HTMLElement>(null)
  const desktopRef = useRef<HTMLElement>(null)
  const isFirstRender = useRef(true)

  useEffect(() => {
    if (sidebarOpen) setShouldRender(true)
    else {
      if (isFirstRender.current) { isFirstRender.current = false; setShouldRender(false); return }
      let done = 0
      const finish = () => { done++; if (done >= ((desktopRef.current ? 1 : 0) + (mobileRef.current ? 1 : 0) || 1)) setShouldRender(false) }
      if (desktopRef.current) gsap.to(desktopRef.current, { x: '-100%', opacity: 0, duration: 0.3, ease: 'power3.in', onComplete: finish })
      if (mobileRef.current) gsap.to(mobileRef.current, { y: '-100%', opacity: 0, duration: 0.3, ease: 'power3.in', onComplete: finish })
    }
  }, [sidebarOpen])

  useEffect(() => {
    if (shouldRender && sidebarOpen) {
      const animate = (el: HTMLElement | null, axis: 'x' | 'y') => {
        if (!el) return
        gsap.fromTo(el, { [axis]: '-100%', opacity: 0 }, { [axis]: '0%', opacity: 1, duration: 0.35, ease: 'power3.out' })
        const items = el.querySelectorAll('.sidebar-nav-item')
        if (items.length > 0) gsap.fromTo(items, { [axis]: -15, opacity: 0 }, { [axis]: 0, opacity: 1, duration: 0.25, stagger: 0.02, ease: 'power2.out' })
      }
      animate(desktopRef.current, 'x')
      animate(mobileRef.current, 'y')
    }
  }, [shouldRender, sidebarOpen])

  const renderNav = (isMobile = false) => (
    <nav aria-label="Primary navigation" className={isMobile ? 'max-w-md mx-auto py-2' : ''}>
      {isMobile && (
        <div className="flex items-center justify-between pb-4 mb-4 border-b-2 border-black">
          <span className="text-lg font-black tracking-widest uppercase">AGNI<span className="text-[#d8f5a9] bg-black px-1.5 py-0.5 ml-1">MENU</span></span>
          <button type="button" onClick={toggleSidebar} aria-label="Close menu" className="p-2 border-2 border-black bg-black text-white hover:bg-zinc-800"><X size={20} /></button>
        </div>
      )}
      {sections.map(({ label: sectionLabel, items }) => (
        <section key={sectionLabel} className="mt-5 first:mt-0">
          <h2 className="px-3 pb-1.5 text-[10px] font-black uppercase tracking-[0.18em] text-text-secondary">{sectionLabel}</h2>
          <div className="space-y-1">
            {items.map(({ label, to, end, icon: Icon }) => (
              <NavLink key={to} to={to} end={end} onClick={() => { if (isMobile) toggleSidebar() }}
                className={({ isActive }) => `sidebar-nav-item flex items-center gap-3 rounded-none border-2 px-4 py-2.5 text-xs font-black uppercase tracking-wide transition-all ${isActive ? 'border-black bg-black text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'border-transparent text-text-secondary hover:border-black hover:bg-zinc-100 hover:text-text-primary'}`}>
                {({ isActive }) => (
                  <>
                    <Icon size={18} className={isActive ? 'text-[#d8f5a9]' : 'text-text-primary'} aria-hidden="true" />
                    {label}
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </section>
      ))}
    </nav>
  )

  if (!shouldRender) return null

  return (
    <>
      <aside ref={desktopRef} className="hidden h-full w-64 shrink-0 border-r-2 border-black bg-surface p-4 md:block">
        {renderNav(false)}
      </aside>
      <aside ref={mobileRef} className="fixed inset-0 z-50 h-full w-full overflow-y-auto border-b-2 border-black bg-surface p-6 shadow-2xl md:hidden">
        {renderNav(true)}
      </aside>
    </>
  )
}




