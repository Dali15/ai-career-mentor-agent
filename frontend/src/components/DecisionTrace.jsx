/**
 * DecisionTrace
 *
 * Product-friendly AI transparency panel.
 * Renders the structured decision_trace from the backend with zero
 * technical jargon — presented as a card-based audit trail.
 *
 * Props:
 *   trace  – decision_trace object from the API
 *   topCareer – string name of the top career (for labelling)
 */
export default function DecisionTrace({ trace, topCareer }) {
  if (!trace || !trace.summary) return null

  const { summary, why_top_career_won, why_others_failed = {}, key_drivers = [] } = trace
  const otherEntries = Object.entries(why_others_failed)

  return (
    <div
      id="decision-trace-panel"
      className="glass-panel glass-border animate-fade-up rounded-[1.75rem] overflow-hidden"
      style={{ animationDelay: '80ms' }}
    >
      {/* Header */}
      <div className="px-6 pt-6 pb-4 border-b border-white/[0.07]">
        <div className="flex items-center gap-3">
          {/* Icon */}
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400/20 to-orange-500/20 ring-1 ring-amber-400/30 shrink-0">
            <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-amber-400" aria-hidden>
              <path d="M10 2a1 1 0 011 1v1a1 1 0 01-2 0V3a1 1 0 011-1zm4.22 2.22a1 1 0 011.42 1.42l-.71.7a1 1 0 01-1.42-1.41l.71-.71zM18 9a1 1 0 010 2h-1a1 1 0 010-2h1zM4.93 14.36a1 1 0 011.41 1.41l-.7.71a1 1 0 01-1.42-1.42l.71-.7zM10 15a1 1 0 011 1v1a1 1 0 01-2 0v-1a1 1 0 011-1zM3 9a1 1 0 000 2H2a1 1 0 000-2h1zm2.64-5.07a1 1 0 00-1.42 1.41l.71.71a1 1 0 001.41-1.42l-.7-.7zM10 6a4 4 0 100 8 4 4 0 000-8z"
                fill="currentColor" />
            </svg>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-amber-400/80">
              AI Transparency
            </p>
            <h2 className="text-sm font-semibold text-white leading-tight">Decision Trace</h2>
          </div>
        </div>

        {/* Summary */}
        <p className="mt-4 text-sm leading-7 text-slate-300">{summary}</p>
      </div>

      <div className="px-6 py-5 space-y-6">

        {/* Key Drivers */}
        {key_drivers.length > 0 && (
          <section aria-labelledby="key-drivers-heading">
            <h3
              id="key-drivers-heading"
              className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400 mb-3"
            >
              Key Drivers
            </h3>
            <ol className="space-y-2">
              {key_drivers.map((driver, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-3 rounded-[1rem] border border-white/[0.07] bg-white/[0.03] px-4 py-3"
                >
                  <span
                    className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-500/20 text-[10px] font-bold text-amber-400 ring-1 ring-amber-400/30"
                    aria-hidden
                  >
                    {idx + 1}
                  </span>
                  <p className="text-sm leading-6 text-slate-200">{driver}</p>
                </li>
              ))}
            </ol>
          </section>
        )}

        {/* Why top career won */}
        {why_top_career_won && (
          <section aria-labelledby="why-won-heading">
            <h3
              id="why-won-heading"
              className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400 mb-3"
            >
              Why {topCareer} Was Recommended
            </h3>
            <div className="flex items-start gap-3 rounded-[1rem] border border-emerald-500/20 bg-emerald-500/[0.05] px-4 py-3">
              <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-400" aria-hidden />
              <p className="text-sm leading-7 text-slate-200">{why_top_career_won}</p>
            </div>
          </section>
        )}

        {/* Why others lost */}
        {otherEntries.length > 0 && (
          <section aria-labelledby="why-others-heading">
            <h3
              id="why-others-heading"
              className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400 mb-3"
            >
              Why Other Paths Ranked Lower
            </h3>
            <ul className="space-y-2">
              {otherEntries.map(([career, reason]) => (
                <li
                  key={career}
                  className="rounded-[1rem] border border-white/[0.07] bg-white/[0.03] px-4 py-3"
                >
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500 mb-1">
                    {career}
                  </p>
                  <p className="text-sm leading-6 text-slate-300">{reason}</p>
                </li>
              ))}
            </ul>
          </section>
        )}

      </div>

      {/* Glow foot strip */}
      <div
        aria-hidden
        className="pointer-events-none h-px bg-gradient-to-r from-transparent via-amber-400/30 to-transparent"
      />
    </div>
  )
}
