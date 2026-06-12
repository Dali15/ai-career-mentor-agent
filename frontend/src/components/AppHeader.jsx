function getAiBadge(aiSource) {
  switch (aiSource) {
    case 'openai':
      return { label: 'OpenAI Active', tone: 'from-sky-400 to-cyan-300' }
    case 'azure':
      return { label: 'Azure AI Active', tone: 'from-indigo-400 to-violet-400' }
    case 'foundry_placeholder':
      return { label: 'Fallback Mode', tone: 'from-amber-400 to-orange-400' }
    default:
      return { label: 'Mock AI', tone: 'from-slate-400 to-slate-200' }
  }
}

export default function AppHeader({ aiSource = 'mock' }) {
  const aiBadge = getAiBadge(aiSource)

  return (
    <header className="glass-panel glass-border animate-fade-up relative overflow-hidden rounded-[1.75rem] px-6 py-5 md:px-7 md:py-6">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.12),transparent_30%),radial-gradient(circle_at_right,rgba(99,102,241,0.12),transparent_26%)]" />
      <div className="relative flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-300 via-sky-500 to-indigo-500 shadow-lg shadow-cyan-950/30">
            <span className="text-lg font-black text-slate-950">AI</span>
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white md:text-[2rem]">
              AI Career Mentor
            </h1>
            <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-400 md:text-[0.95rem]">
              AI-powered career reasoning agent
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 md:items-end md:text-right">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/55 px-3 py-1.5 text-xs font-semibold tracking-[0.16em] text-slate-200 shadow-[0_12px_40px_rgba(2,6,23,0.2)]">
            <span className={`h-2.5 w-2.5 rounded-full bg-gradient-to-r ${aiBadge.tone} animate-pulse`} />
            {aiBadge.label}
          </span>
          <p className="max-w-xl text-sm leading-6 text-slate-400">
            Clean, structured career planning with transparent reasoning, comparison mode, and a practical roadmap.
          </p>
        </div>
      </div>

      <div className="relative mt-5 flex flex-wrap gap-2 text-xs text-slate-300">
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">Structured JSON output</span>
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">3-month roadmap</span>
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">Career comparison</span>
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">Reasoning trace</span>
      </div>
    </header>
  )
}