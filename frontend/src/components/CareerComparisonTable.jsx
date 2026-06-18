/**
 * @typedef {Object} CareerScoreItem
 * @property {string} career - Career title
 * @property {number} score - Match score 0-100
 * @property {string[]} top_positive_factors - Key strengths
 * @property {string[]} missing_critical_skills - Skill gaps
 * @property {string} reasoning_summary - Explanation of match
 */

import ResultCard from './ResultCard'

/**
 * ComparisonRow - Individual row in the career comparison table.
 * @param {Object} props
 * @param {CareerScoreItem} props.item - Career data to display
 * @param {boolean} props.isBest - Whether this is the top-ranked career
 * @returns {React.JSX.Element}
 */
function ComparisonRow({ item, isBest }) {
  // Validate and normalize score to 0-100 range
  const safeScore = Math.max(0, Math.min(100, Number(item?.score) || 0))
  const careerName = String(item?.career || 'Career').trim()
  const strengths = Array.isArray(item?.top_positive_factors) && item.top_positive_factors.length > 0
    ? item.top_positive_factors.join(', ')
    : 'None'
  const gaps = Array.isArray(item?.missing_critical_skills) && item.missing_critical_skills.length > 0
    ? item.missing_critical_skills.join(', ')
    : 'None'

  return (
    <tr className={isBest ? 'bg-cyan-400/10' : ''}>
      <td className="px-4 py-4 align-top">
        <div className="flex items-center gap-3">
          <span className={`h-2.5 w-2.5 rounded-full ${isBest ? 'bg-cyan-300' : 'bg-white/20'}`} />
          <div>
            <p className="font-medium text-white">{careerName}</p>
            {isBest ? <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Best match</p> : null}
          </div>
        </div>
      </td>

      <td className="px-4 py-4 align-top">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm text-slate-200">
            <span>{safeScore}%</span>
            <span className="text-xs text-slate-400">match</span>
          </div>
          <div className="h-2 rounded-full bg-white/10">
            <div
              className={`h-2 rounded-full ${isBest ? 'bg-gradient-to-r from-cyan-300 to-blue-500' : 'bg-slate-400/70'}`}
              style={{ width: `${safeScore}%` }}
            />
          </div>
        </div>
      </td>

      <td className="px-4 py-4 align-top text-sm leading-6 text-slate-300">
        <p className="mb-1"><span className="font-semibold text-emerald-400">Strengths:</span> {strengths}</p>
        <p><span className="font-semibold text-amber-400">Gaps:</span> {gaps}</p>
      </td>
    </tr>
  )
}

export default function CareerComparisonTable({ comparison = [], bestCareer = '', className = '' }) {
  if (!comparison.length) {
    return (
      <ResultCard
        eyebrow="Comparison"
        title="Career comparison mode"
        description="Comparison results will appear here once the backend returns matching career scores."
        accent="from-cyan-400 to-indigo-500"
        className={className}
      >
        <div className="rounded-[1rem] border border-dashed border-white/12 bg-white/[0.03] px-5 py-6 text-sm leading-6 text-slate-400">
          No comparison data yet. Submit the form to compare the selected careers side by side.
        </div>
      </ResultCard>
    )
  }

  return (
    <ResultCard
      eyebrow="Comparison"
      title="Career comparison mode"
      description="The selected paths are scored against your profile so the best fit is easy to compare at a glance."
      accent="from-cyan-400 to-indigo-500"
      className={className}
    >
      <div className="overflow-hidden rounded-[1rem] border border-white/10 bg-slate-950/35">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead className="border-b border-white/10 bg-white/[0.04]">
              <tr>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Career</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400 w-32">Score</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Key Factors</th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((item) => (
                <ComparisonRow key={item?.career || 'career'} item={item} isBest={item?.career === bestCareer} />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </ResultCard>
  )
}