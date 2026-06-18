import SectionHeader from './SectionHeader'

function getStrokeColor(score) {
  if (score >= 80) return 'from-emerald-300 to-cyan-300'
  if (score >= 60) return 'from-cyan-300 to-sky-400'
  if (score >= 40) return 'from-amber-300 to-orange-400'
  return 'from-rose-300 to-orange-400'
}

export default function CareerMatchScore({ score = 0, explanation = '', confidenceScore, jobReadyTime, marketDemand, className = '' }) {
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0))
  const strokeOffset = 314 - (314 * safeScore) / 100
  const accent = getStrokeColor(safeScore)
  
  const matchLabel = safeScore >= 80 ? 'Excellent Match' : 
                     safeScore >= 60 ? 'Good Match' : 
                     safeScore >= 40 ? 'Developing Match' : 
                     'Early-Stage Match'
  
  const confidence = typeof confidenceScore === 'number' 
    ? confidenceScore 
    : Math.min(100, Math.max(20, safeScore * 1.15))

  return (
    <section className={`glass-panel glass-border animate-fade-up rounded-[1.5rem] p-6 shadow-[0_24px_80px_rgba(15,23,42,0.24)] ${className}`}>
      <SectionHeader
        eyebrow="Career Match Analysis"
        title="Readiness Assessment"
        description="How well your profile aligns with the recommended career path based on vector similarity, coverage, and alignment scoring."
      />

      <div className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,260px)_minmax(0,1fr)] lg:items-center">
        {/* Circular Progress */}
        <div
          className="relative mx-auto h-40 w-40 md:h-48 md:w-48"
          role="progressbar"
          aria-label={`Career readiness ${safeScore} out of 100`}
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={safeScore}
        >
          <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90 transform">
            <circle cx="60" cy="60" r="50" className="fill-none stroke-white/10" strokeWidth="8" />
            <circle
              cx="60"
              cy="60"
              r="50"
              stroke="url(#career-match-gradient)"
              className="fill-none transition-all duration-1000 ease-out drop-shadow-lg"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray="314"
              strokeDashoffset={strokeOffset}
              pathLength="314"
            />
            <defs>
              <linearGradient id="career-match-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop
                  offset="0%"
                  stopColor={safeScore >= 80 ? '#10b981' : safeScore >= 60 ? '#06b6d4' : safeScore >= 40 ? '#f59e0b' : '#ef4444'}
                />
                <stop
                  offset="100%"
                  stopColor={safeScore >= 80 ? '#06b6d4' : safeScore >= 60 ? '#0ea5e9' : safeScore >= 40 ? '#f97316' : '#f87171'}
                />
              </linearGradient>
            </defs>
          </svg>

          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-5xl font-bold tracking-tight text-white md:text-6xl">{safeScore}%</span>
            <span className="mt-1 text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Match Score</span>
          </div>
        </div>

        {/* Details Panel */}
        <div className="space-y-5">
          {/* Match Label Badge */}
          <div className="flex items-center gap-3">
            <div className={`inline-flex items-center gap-2 rounded-full bg-gradient-to-r ${accent} px-4 py-2 text-sm font-semibold text-slate-950 shadow-lg`}>
              <span className={`h-2 w-2 rounded-full ${safeScore >= 80 ? 'bg-emerald-200' : safeScore >= 60 ? 'bg-cyan-200' : safeScore >= 40 ? 'bg-yellow-200' : 'bg-red-200'}`} />
              {matchLabel}
            </div>
          </div>

          {/* Main Explanation */}
          <p className="max-w-2xl text-base leading-relaxed text-slate-300">
            {explanation || 'Your profile has been evaluated against this career path using semantic vector analysis and deterministic scoring.'}
          </p>

          {/* Stats Grid */}
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-blue-500/20 bg-blue-950/20 px-4 py-3 backdrop-blur-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-300">Confidence</p>
              <p className="mt-2 text-xl font-bold text-white">{confidence.toFixed(0)}%</p>
            </div>
            {typeof jobReadyTime === 'string' && (
              <div className="rounded-lg border border-green-500/20 bg-green-950/20 px-4 py-3 backdrop-blur-sm">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-green-300">Timeline</p>
                <p className="mt-2 text-xl font-bold text-white">{jobReadyTime}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}