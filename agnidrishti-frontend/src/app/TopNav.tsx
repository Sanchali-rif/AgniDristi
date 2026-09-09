import { useState } from 'react'
import agniDrishtiLogo from '../assets/SIH_tech_invaders (3).png'
import { CheckCircle2, Loader2, Menu, Moon, Sun, User, UserPlus, XCircle, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useThemeStore } from '../stores/themeStore'
import { useUIStore } from '../stores/uiStore'
import { triggerMonitoringRun } from '../services/monitoringRunService'

export function TopNav() {
  const theme = useThemeStore((state) => state.theme)
  const toggleTheme = useThemeStore((state) => state.toggleTheme)
  const sidebarOpen = useUIStore((state) => state.sidebarOpen)
  const toggleSidebar = useUIStore((state) => state.toggleSidebar)

  const [syncState, setSyncState] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle')
  const [syncMsg, setSyncMsg] = useState('')

  const handleRunSync = async () => {
    setSyncState('syncing')
    setSyncMsg('Syncing...')
    try {
      await triggerMonitoringRun(1)
      setSyncState('success')
      setSyncMsg('Sync Completed')
      setTimeout(() => { setSyncState('idle'); setSyncMsg('') }, 3500)
    } catch {
      setSyncState('error')
      setSyncMsg('Sync Failed')
      setTimeout(() => { setSyncState('idle'); setSyncMsg('') }, 3500)
    }
  }

  return (
    <header className="flex h-16 w-full items-center justify-between border-b-2 border-black bg-black px-2 text-white sm:px-6">
      <div className="flex min-w-0 items-center gap-1.5 sm:gap-3">
        <button type="button" aria-label={sidebarOpen ? 'Close navigation' : 'Open navigation'} aria-expanded={sidebarOpen} onClick={toggleSidebar}
          className="flex shrink-0 items-center justify-center p-1.5 border border-zinc-700 bg-zinc-900 text-white hover:bg-zinc-800 cursor-pointer sm:p-2">
          <Menu size={17} aria-hidden="true" className="sm:size-[18px]" />
        </button>
        <div className="flex shrink-0 items-center gap-1.5">
          <img src={agniDrishtiLogo} alt="AGNI-DRISHTI" className="h-6 w-auto max-h-7 shrink-0 object-contain sm:h-8 sm:max-h-9 -mt-0.5 sm:-mt-1" />
          <span className="flex items-center whitespace-nowrap text-xs font-black tracking-tight uppercase sm:text-lg sm:tracking-wider md:text-xl shrink-0 leading-none">AGNI<span className="text-[#d8f5a9]">DRISHTI</span></span>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1 sm:gap-2.5">
        {syncState === 'syncing' && <div className="hidden whitespace-nowrap items-center gap-1 font-mono text-[10px] sm:text-xs font-black uppercase text-[#d8f5a9] md:flex"><Loader2 size={14} className="animate-spin" /><span>SYNCING...</span></div>}
        {syncState === 'success' && <div className="hidden whitespace-nowrap items-center gap-1 font-mono text-[10px] sm:text-xs font-black uppercase text-emerald-400 md:flex"><CheckCircle2 size={14} /><span>{syncMsg}</span></div>}
        {syncState === 'error' && <div className="hidden whitespace-nowrap items-center gap-1 font-mono text-[10px] sm:text-xs font-black uppercase text-red-400 md:flex"><XCircle size={14} /><span>{syncMsg}</span></div>}

        <button type="button" disabled={syncState === 'syncing'} onClick={handleRunSync} className="flex shrink-0 whitespace-nowrap items-center gap-1 bg-[#d8f5a9] px-2 py-1 text-[11px] font-black uppercase text-black hover:opacity-90 disabled:opacity-50 cursor-pointer sm:gap-1.5 sm:px-2.5 sm:py-1.5 sm:text-xs">
          {syncState === 'syncing' ? <Loader2 size={12} className="animate-spin sm:size-[13px]" /> : <Zap size={12} className="sm:size-[13px]" />}
          <span className="hidden min-[380px]:inline sm:inline">Sync</span>
        </button>

        <button type="button" aria-label="Toggle theme" onClick={toggleTheme} className="flex shrink-0 whitespace-nowrap items-center justify-center border border-zinc-700 bg-zinc-900 p-1.5 text-xs font-bold text-white hover:bg-[#d8f5a9] hover:text-black sm:px-3 sm:py-1.5 cursor-pointer">
          {theme === 'light' ? <Moon size={13} /> : <Sun size={13} />}
          <span className="hidden sm:ml-1.5 sm:inline">{theme === 'light' ? 'DARK' : 'LIGHT'}</span>
        </button>

        <div className="flex shrink-0 items-center gap-1 border-l border-zinc-800 pl-1 sm:gap-1.5 sm:pl-2.5">
          <Link to="/login" className="flex shrink-0 whitespace-nowrap items-center gap-1 border border-zinc-700 bg-zinc-900 p-1.5 text-xs font-black uppercase text-white hover:bg-[#d8f5a9] hover:text-black sm:px-2.5 sm:py-1.5"><User size={13} /> <span className="hidden sm:inline">Login</span></Link>
          <Link to="/signup" className="hidden shrink-0 whitespace-nowrap items-center gap-1 border border-[#d8f5a9] bg-black px-2.5 py-1.5 text-xs font-black uppercase text-[#d8f5a9] hover:bg-[#d8f5a9] hover:text-black md:flex"><UserPlus size={13} /> Sign Up</Link>
        </div>
      </div>
    </header>
  )
}




