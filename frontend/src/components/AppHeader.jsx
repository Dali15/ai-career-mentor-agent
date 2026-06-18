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
    <header className="glass-panel glass-border animate-fade-up relative overflow-hidden rounded-[1.75rem] px-6 py-8 md:px-8 md:py-12">
      {/* Gradient background */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-transparent" />
      <div className="pointer-events-none absolute -top-40 -right-40 h-80 w-80 rounded-full bg-blue-500/5 blur-3xl" />
      
      <div className="relative flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-400 via-blue-500 to-indigo-600 shadow-lg shadow-blue-950/40">
              <span className="text-xl font-black text-white">AI</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                AI Career Mentor Agent
              </h1>
              <p className="mt-2 text-sm font-medium text-blue-300 md:text-base">
                Semantic Career Intelligence Engine
              </p>
            </div>
          </div>
          
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-gray-300 md:text-lg">
            Explainable recommendations powered by vector reasoning, intent normalization, and deterministic scoring.
          </p>
        </div>

        <div className="flex flex-col gap-4 md:items-end md:text-right">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/55 px-4 py-2 text-xs font-semibold tracking-[0.16em] text-slate-200 shadow-[0_12px_40px_rgba(2,6,23,0.2)]">
            <span className={`h-2.5 w-2.5 rounded-full bg-gradient-to-r ${aiBadge.tone} animate-pulse`} />
            {aiBadge.label}
          </span>
          <p className="max-w-xl text-sm leading-6 text-slate-400">
            Structured recommendations with transparent reasoning, side-by-side career comparison, and actionable roadmaps.
          </p>
        </div>
      </div>

      <div className="relative mt-8 flex flex-wrap gap-3 text-xs text-slate-300">
        <span className="rounded-full border border-blue-500/30 bg-blue-950/30 px-4 py-2 font-medium">Vector Similarity</span>
        <span className="rounded-full border border-green-500/30 bg-green-950/30 px-4 py-2 font-medium">Intent Detection</span>
        <span className="rounded-full border border-purple-500/30 bg-purple-950/30 px-4 py-2 font-medium">Hybrid Scoring</span>
        <span className="rounded-full border border-yellow-500/30 bg-yellow-950/30 px-4 py-2 font-medium">Explainability</span>
      </div>
    </header>
  )
}