import { useEffect, useRef, useState } from 'react'

const PIPELINE_STEPS = [
  { label: 'Analyzing profile',        icon: '🔍', color: 'from-cyan-400 to-sky-500',     delay: 0   },
  { label: 'Extracting skill vectors',  icon: '🧬', color: 'from-sky-400 to-indigo-500',   delay: 600 },
  { label: 'Computing vector space',    icon: '📐', color: 'from-indigo-400 to-violet-500', delay: 1200 },
  { label: 'Scoring careers',           icon: '⚡', color: 'from-violet-400 to-fuchsia-500', delay: 1900 },
  { label: 'Generating explanation',    icon: '✨', color: 'from-fuchsia-400 to-rose-400',  delay: 2600 },
]

const STEP_DURATION = 650  // ms each step stays "active" before locking as done

/**
 * AIThinkingLoader
 *
 * Visible reasoning simulation — shows each pipeline step fading/sliding
 * in one-by-one with glow, typing dots, and a running progress bar.
 * Calls onComplete() after all steps finish.
 *
 * Props:
 *   steps  – optional string[] override (falls back to PIPELINE_STEPS labels)
 *   onComplete – called once animation cycle finishes (optional)
 */
export default function AIThinkingLoader({ steps: stepOverride, onComplete }) {
  const [visibleCount, setVisibleCount]   = useState(0)   // how many steps are revealed
  const [activeIndex, setActiveIndex]     = useState(0)   // currently "processing" step
  const [doneIndices, setDoneIndices]     = useState([])  // steps marked complete
  const [finished, setFinished]           = useState(false)
  const completedRef = useRef(false)

  const displaySteps = stepOverride
    ? stepOverride.map((label, i) => ({ ...PIPELINE_STEPS[i % PIPELINE_STEPS.length], label }))
    : PIPELINE_STEPS

  // Cascade: reveal steps one at a time, mark each as done before revealing next
  useEffect(() => {
    completedRef.current = false
    setVisibleCount(0)
    setActiveIndex(0)
    setDoneIndices([])
    setFinished(false)

    let step = 0
    let cancelled = false

    function tick() {
      if (cancelled) return
      if (step >= displaySteps.length) {
        // All done
        setFinished(true)
        if (!completedRef.current) {
          completedRef.current = true
          onComplete?.()
        }
        return
      }

      const current = step
      setActiveIndex(current)
      setVisibleCount(current + 1)

      // After STEP_DURATION mark current as done, then advance
      setTimeout(() => {
        if (cancelled) return
        setDoneIndices(prev => [...prev, current])
        step += 1
        setTimeout(tick, 120)   // tiny gap between done flash and next reveal
      }, displaySteps[current].delay === 0 ? STEP_DURATION : STEP_DURATION)
    }

    // First tick immediately
    tick()

    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const progressPct = finished
    ? 100
    : Math.round((doneIndices.length / displaySteps.length) * 100)

  return (
    <div
      id="ai-thinking-loader"
      className="glass-panel glass-border thinking-glow relative overflow-hidden rounded-[1.75rem] px-6 py-7"
      aria-label="AI reasoning pipeline"
      aria-live="polite"
    >
      {/* Ambient scanner sweep */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 overflow-hidden rounded-[1.75rem]"
      >
        <div
          className="scanner-bar absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-cyan-400/10 to-transparent"
        />
      </div>

      {/* Header row */}
      <div className="relative flex items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          {/* Animated logo mark */}
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 to-indigo-500/20 ring-1 ring-white/10">
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-cyan-400" aria-hidden>
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">
              AI Pipeline
            </p>
            <p className="text-sm font-semibold text-white leading-tight">
              {finished ? 'Analysis complete' : 'Processing your profile…'}
            </p>
          </div>
        </div>

        {/* Typing dots (only when not finished) */}
        {!finished && (
          <div className="flex items-end gap-[3px] pb-0.5" aria-hidden>
            <span className="dot-1 h-[5px] w-[5px] rounded-full bg-cyan-400 inline-block" />
            <span className="dot-2 h-[5px] w-[5px] rounded-full bg-cyan-400 inline-block" />
            <span className="dot-3 h-[5px] w-[5px] rounded-full bg-cyan-400 inline-block" />
          </div>
        )}
        {finished && (
          <span className="text-emerald-400 text-sm font-semibold tracking-wide">
            Complete
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="relative mb-6 h-[3px] overflow-hidden rounded-full bg-white/[0.07]">
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-indigo-500 to-fuchsia-500 transition-all duration-500 ease-out"
          style={{ width: `${progressPct}%` }}
          aria-valuenow={progressPct}
          aria-valuemin={0}
          aria-valuemax={100}
          role="progressbar"
        />
      </div>

      {/* Steps list */}
      <ol className="relative space-y-3">
        {displaySteps.map((step, idx) => {
          const isVisible = idx < visibleCount
          const isDone    = doneIndices.includes(idx)
          const isActive  = activeIndex === idx && !isDone && isVisible

          if (!isVisible) return null

          return (
            <li
              key={step.label}
              className="step-slide flex items-center gap-4"
              style={{ animationDelay: '0ms' }}
            >
              {/* Step icon bubble */}
              <div
                className={[
                  'relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-[15px]',
                  isDone
                    ? 'bg-emerald-500/15 ring-1 ring-emerald-500/30'
                    : isActive
                    ? `bg-gradient-to-br ${step.color} bg-opacity-20 ring-1 ring-white/20`
                    : 'bg-white/[0.05] ring-1 ring-white/10',
                ].join(' ')}
              >
                {isDone ? (
                  <svg
                    viewBox="0 0 16 16"
                    fill="none"
                    className="check-pop h-4 w-4 text-emerald-400"
                    aria-hidden
                  >
                    <path
                      d="M3 8.5l3.5 3.5L13 5"
                      stroke="currentColor"
                      strokeWidth="1.75"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                ) : (
                  <span aria-hidden>{step.icon}</span>
                )}

                {/* Active pulse ring */}
                {isActive && (
                  <span
                    aria-hidden
                    className="absolute inset-0 animate-ping rounded-xl bg-cyan-400/20"
                  />
                )}
              </div>

              {/* Label + status */}
              <div className="flex-1 min-w-0">
                <p
                  className={[
                    'text-sm font-medium transition-colors duration-300',
                    isDone   ? 'text-emerald-300' :
                    isActive ? 'text-white'        : 'text-slate-400',
                  ].join(' ')}
                >
                  {step.label}
                </p>
                {isActive && (
                  <p className="mt-0.5 text-[11px] text-cyan-400/80 font-mono tracking-wide animate-fade-in">
                    running…
                  </p>
                )}
                {isDone && (
                  <p className="mt-0.5 text-[11px] text-emerald-400/70 font-mono tracking-wide animate-fade-in">
                    done
                  </p>
                )}
              </div>

              {/* Step number badge */}
              <span
                className={[
                  'shrink-0 text-[10px] font-bold tabular-nums tracking-widest transition-colors duration-300',
                  isDone   ? 'text-emerald-400/60' :
                  isActive ? 'text-cyan-400/80'    : 'text-slate-600',
                ].join(' ')}
              >
                {String(idx + 1).padStart(2, '0')}
              </span>
            </li>
          )
        })}
      </ol>

      {/* Bottom glow strip */}
      <div
        aria-hidden
        className="pointer-events-none absolute bottom-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-cyan-400/40 to-transparent"
      />
    </div>
  )
}
