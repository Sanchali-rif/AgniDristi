import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, KeyRound, ShieldCheck, User } from 'lucide-react'
import { FireBackground } from '../components/common/FireBackground'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      navigate('/dashboard')
    }, 600)
  }

  return (
    <div className="relative flex min-h-screen w-screen items-center justify-center bg-bg text-text-primary p-4 overflow-hidden">
      <FireBackground />
      <div className="relative z-10 w-full max-w-md border-2 border-text-primary bg-surface p-5 sm:p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] dark:shadow-[6px_6px_0px_0px_rgba(216,245,169,0.25)]">
        <div className="flex items-center justify-between gap-2 border-b-2 border-text-primary pb-4">
          <div className="flex items-center gap-2.5 min-w-0">
            <ShieldCheck size={24} className="shrink-0 text-text-primary sm:size-7" />
            <div className="min-w-0">
              <h1 className="text-base font-black tracking-wider uppercase text-text-primary sm:text-xl sm:tracking-widest">
                AGNI<span className="ml-1 bg-black px-1.5 py-0.5 text-[#d8f5a9]">AUTH</span>
              </h1>
              <p className="text-[10px] font-black uppercase text-text-secondary truncate">Satellite Intelligence Portal</p>
            </div>
          </div>
          <Link to="/dashboard" className="flex shrink-0 whitespace-nowrap items-center gap-1 border border-text-primary bg-surface px-2 py-1 text-xs font-black uppercase text-text-primary hover:bg-black hover:text-white dark:hover:bg-zinc-800 dark:hover:text-white transition-colors sm:px-2.5">
            <ArrowLeft size={13} /> Back
          </Link>
        </div>

        <form onSubmit={handleLogin} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-black uppercase text-text-primary">Operator ID / Email</label>
            <div className="relative mt-1">
              <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
              <input type="email" value={username} onChange={(e) => setUsername(e.target.value)} required placeholder="operator@agnidrishti.gov"
                className="w-full border-2 border-text-primary bg-surface py-2 pl-9 pr-3 text-xs font-bold text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:ring-2 focus:ring-accent" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-black uppercase text-text-primary">Access Password</label>
            <div className="relative mt-1">
              <KeyRound size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="Enter your access password"
                className="w-full border-2 border-text-primary bg-surface py-2 pl-9 pr-3 text-xs font-bold text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:ring-2 focus:ring-accent" />
            </div>
          </div>

          <div className="border-2 border-text-primary bg-bg/30 p-3.5 text-[11px] font-bold">
            <p className="uppercase font-black text-text-primary">System Notice:</p>
            <p className="mt-0.5 font-mono text-[10px] text-text-primary">Authorized Satellite Intelligence Operator Access Only.</p>
          </div>

          <button type="submit" disabled={loading}
            className="w-full border-2 border-text-primary bg-black dark:bg-[#d8f5a9] py-2.5 text-xs font-black uppercase text-white dark:text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] dark:shadow-[2px_2px_0px_0px_rgba(216,245,169,0.4)] hover:opacity-90 disabled:opacity-50">
            {loading ? 'Authenticating...' : 'Authenticate & Enter Portal'}
          </button>
        </form>

        <div className="mt-5 border-t border-text-primary/20 pt-4 text-center text-xs font-bold uppercase text-text-secondary">
          Don't have an operator ID? <Link to="/signup" className="font-black text-text-primary underline hover:text-accent">Sign Up Here</Link>
        </div>
      </div>
    </div>
  )
}

