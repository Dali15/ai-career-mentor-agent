import SectionHeader from './SectionHeader'

function getScoreColor(score) {
  if (score >= 80) return { bg: 'bg-emerald-950/40', border: 'border-emerald-500/30', text: 'text-emerald-300', barClass: 'from-emerald-500 to-emerald-400' }
  if (score >= 60) return { bg: 'bg-blue-950/40', border: 'border-blue-500/30', text: 'text-blue-300', barClass: 'from-blue-500 to-blue-400' }
  if (score >= 40) return { bg: 'bg-amber-950/40', border: 'border-amber-500/30', text: 'text-amber-300', barClass: 'from-amber-500 to-amber-400' }
  return { bg: 'bg-slate-950/40', border: 'border-slate-500/30', text: 'text-slate-300', barClass: 'from-slate-500 to-slate-400' }
}

function ScoreBar({ score, animated = true }) {
  const colors = getScoreColor(score)
  const width = Math.min(100, Math.max(0, score))
  
  return (
    <div className="space-y-2">
      <div className="flex items-end justify-between">
        <span className={`text-sm font-semibold ${colors.text}`}>Career fit</span>
        <span className="text-lg font-bold text-white">{Math.round(score)}</span>
      </div>
      <div className="relative h-3 w-full overflow-hidden rounded-full bg-white/5">
        <div
          className={`h-full bg-gradient-to-r ${colors.barClass} transition-all duration-1000 ease-out shadow-lg ${animated ? '' : ''}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  )
}

export default function ComparisonCards({ careers = [], className = '' }) {
  if (!careers || careers.length === 0) {
    return null
  }

  // Sort by score descending
  const sorted = [...careers].sort((a, b) => (b.score || 0) - (a.score || 0))
  
  return (
    <section className={`animate-fade-up ${className}`}>
      <SectionHeader
        eyebrow="Career Comparison"
        title="Path Analysis"
        description="Side-by-side comparison of how your profile aligns with each career path."
      />

      <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {sorted.map((career, idx) => {
          const colors = getScoreColor(career.score || 0)
          const isTop = idx === 0
          const hasStrengths = Array.isArray(career.top_positive_factors) && career.top_positive_factors.length > 0
          const hasGaps = Array.isArray(career.missing_critical_skills) && career.missing_critical_skills.length > 0
          
          return (
            <div
              key={career.career}
              className={`glass-panel glass-border group relative overflow-hidden rounded-xl p-5 transition-all duration-300 hover:shadow-lg hover:shadow-blue-950/30 ${
                isTop ? 'ring-2 ring-blue-500/50 shadow-lg shadow-blue-950/40' : ''
              }`}
              style={{
                animationDelay: `${idx * 75}ms`,
              }}
            >
              {/* Top Badge */}
              {isTop && (
                <div className="absolute top-0 right-0 rounded-bl-lg bg-gradient-to-br from-blue-500 to-indigo-600 px-3 py-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-white">Top Match</span>
                </div>
              )}

              {/* Career Title */}
              <h3 className="pr-16 text-lg font-bold text-white">{career.career}</h3>

              {/* Score Bar */}
              <div className="mt-5">
                <ScoreBar score={career.score || 0} animated={true} />
              </div>

              {/* Strengths */}
              {hasStrengths && (
                <div className="mt-5 space-y-2">
                  <p className="text-xs font-semibold uppercase tracking-wider text-green-300">Strengths</p>
                  <ul className="space-y-1">
                    {career.top_positive_factors.slice(0, 2).map((factor) => (
                      <li key={factor} className="flex items-start gap-2 text-xs text-slate-300">
                        <span className="mt-1.5 flex-shrink-0 h-1.5 w-1.5 rounded-full bg-green-500" />
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Gaps */}
              {hasGaps && (
                <div className="mt-4 space-y-2">
                  <p className="text-xs font-semibold uppercase tracking-wider text-amber-300">Growth Areas</p>
                  <ul className="space-y-1">
                    {career.missing_critical_skills.slice(0, 2).map((gap) => (
                      <li key={gap} className="flex items-start gap-2 text-xs text-slate-400">
                        <span className="mt-1.5 flex-shrink-0 h-1.5 w-1.5 rounded-full bg-amber-500" />
                        <span>{gap}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Hover Effect */}
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-blue-500/0 via-transparent to-white/0 opacity-0 transition-opacity duration-300 group-hover:opacity-5" />
            </div>
          )
        })}
      </div>
    </section>
  )
}
