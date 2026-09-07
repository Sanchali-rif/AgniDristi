import { Menu, Sun, Moon, Radio, Zap } from 'lucide-react'
import { useThemeStore } from '../stores/themeStore'
import { useUIStore } from '../stores/uiStore'
import { triggerMonitoringRun } from '../services/monitoringRunService'

export function TopNav() {
  const theme = useThemeStore((state) => state.theme)
  const toggleTheme = useThemeStore((state) => state.toggleTheme)
  const sidebarOpen = useUIStore((state) => state.sidebarOpen)
  const toggleSidebar = useUIStore((state) => state.toggleSidebar)

  return (
    <header className="flex items-center justify-between h-16 px-6 text-white bg-black border-b-2 border-black">
      <div className="flex items-center gap-3">
        <button
          type="button"
          aria-label={sidebarOpen ? 'Close navigation' : 'Open navigation'}
          aria-expanded={sidebarOpen}
          onClick={toggleSidebar}
          className="flex items-center justify-center p-2 text-white border border-zinc-700 bg-zinc-900 hover:bg-zinc-800 active:bg-zinc-700 transition-colors"
        >
          <Menu size={20} aria-hidden="true" />
        </button>
        <div className="flex items-center gap-2">
          <span className="text-lg sm:text-xl font-black tracking-widest uppercase">AGNI<span className="text-[#d8f5a9]">DRISHTI</span></span>
        </div>
      </div>

      <div className="hidden items-center gap-3 border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 md:flex">
        <Radio size={14} className="animate-pulse text-[#d8f5a9]" />
        <span className="font-mono text-[11px] font-semibold uppercase tracking-wider">SATELLITE PIPELINE: ONLINE</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => triggerMonitoringRun()}
          className="hidden items-center gap-1.5 bg-[#d8f5a9] px-3 py-1.5 text-xs font-black uppercase tracking-wider text-black transition-opacity hover:opacity-90 sm:flex"
        >
          <Zap size={14} /> Run Sync
        </button>
        <button
          type="button"
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
          aria-pressed={theme === 'dark'}
          onClick={toggleTheme}
          className="flex items-center gap-2 border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-bold text-white transition-colors hover:bg-zinc-800"
        >
          {theme === 'light' ? <Moon size={14} /> : <Sun size={14} />}
          <span>{theme === 'light' ? 'DARK' : 'LIGHT'}</span>
        </button>
      </div>
    </header>
  )
}



