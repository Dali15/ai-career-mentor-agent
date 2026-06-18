import { useRef, useState } from 'react'

import AppHeader from './AppHeader'
import AIThinkingLoader from './AIThinkingLoader'
import CareerMatchScore from './CareerMatchScore'
import ComparisonCards from './ComparisonCards'
import DecisionTrace from './DecisionTrace'
import ProfileForm from './ProfileForm'
import ReasoningTimeline from './ReasoningTimeline'
import ResultCard from './ResultCard'
import RoadmapCard from './RoadmapCard'
import PipelineVisualization from './PipelineVisualization'

/**
 * @typedef {Object} FormData
 * @property {string} education - User education background
 * @property {string} skills - Comma-separated or newline-separated skills
 * @property {string} interests - User career interests
 * @property {string[]} selectedCareers - List of careers to compare against
 */

/**
 * @typedef {Object} CareerScore
 * @property {string} career - Career title
 * @property {number} score - Numerical score (0-100)
 * @property {string[]} top_positive_factors - Skills/factors boosting this career
 * @property {string[]} supporting_factors - Additional positive factors
 * @property {string[]} missing_critical_skills - Skills gaps for this career
 * @property {string} reasoning_summary - Explanation of the score
 */

/**
 * @typedef {Object} CareerPlan
 * @property {string} ai_source - "mock" | "groq" | "openai" | "azure"
 * @property {string} top_career - Recommended career
 * @property {CareerScore[]} career_scores - Ranked list of careers
 * @property {Object} decision_trace - Reasoning behind recommendations
 * @property {Object} roadmap - 3-month action plan
 * @property {string[]} reasoning - Structured reasoning steps
 * @property {string[]} strengths - User's key strengths
 * @property {string[]} gaps - Identified skill gaps
 * @property {Object} normalization - Parsing details and confidence scores
 */

const initialFormData = {
  education: '',
  skills: '',
  interests: '',
  selectedCareers: ['DevOps Engineer', 'Data Analyst', 'Backend Developer', 'Cloud Engineer'],
}

/**
 * Homepage component - Main UI for career recommendation engine.
 * Manages form submission, API calls, loading states, and result display.
 * 
 * Race condition handling:
 * - Each API request gets a unique requestId (timestamp)
 * - pendingPlan stores {id, data} to validate response belongs to latest request
 * - handleThinkingComplete only updates state if requestId matches current pending request
 */
export default function Homepage() {
  const [formData, setFormData] = useState(initialFormData)
  /** @type {[CareerPlan | null, Function]} */
  const [careerPlan, setCareerPlan] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [thinkingDone, setThinkingDone] = useState(false)
  /** @type {React.MutableRefObject<{id: number, data: CareerPlan | null} | null>} */
  const pendingPlan = useRef(null)  // Hold result until animation finishes, with requestId for race condition prevention

  const aiSource = careerPlan?.ai_source || 'mock'
  const careerScores = Array.isArray(careerPlan?.career_scores) ? careerPlan.career_scores : []

  // Sort by score descending
  const sortedScores = [...careerScores].sort((a, b) => (b.score || 0) - (a.score || 0))
  const topCareerData = sortedScores[0] || {}

  const recommendedPaths = sortedScores.map(c => c.career).filter(Boolean)
  const comparison = sortedScores
  const topCareer = careerPlan?.top_career || topCareerData.career || ''
  const topCareerScore = topCareerData.score || 0
  const strengths = Array.isArray(topCareerData.top_positive_factors) ? topCareerData.top_positive_factors : []
  const missingSkills = Array.isArray(topCareerData.missing_critical_skills) ? topCareerData.missing_critical_skills : []

  // Legacy/other fields
  const learningResources = Array.isArray(careerPlan?.learning_resources) ? careerPlan.learning_resources : []
  const certifications = Array.isArray(careerPlan?.certifications) ? careerPlan.certifications : []
  const roadmap = careerPlan?.roadmap || {}
  // reasoning is now an array of 4 structured ExplanationEngine steps
  const reasoningSteps = Array.isArray(careerPlan?.reasoning) ? careerPlan.reasoning : []
  const finalExplanation = careerPlan?.final_explanation || ''
  const pipelineSteps = Array.isArray(careerPlan?.pipeline_steps) ? careerPlan.pipeline_steps : null
  const decisionTrace = careerPlan?.decision_trace || null

  // When API returns, store in ref — actual reveal waits for animation to finish
  function handleThinkingComplete() {
    if (pendingPlan.current?.data) {
      setCareerPlan(pendingPlan.current.data)
      pendingPlan.current = null
    }
    setThinkingDone(true)
    setIsLoading(false)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setIsLoading(true)
    setThinkingDone(false)
    setError('')
    setCareerPlan(null)
    
    const requestId = Date.now()  // Unique ID for this request
    pendingPlan.current = { id: requestId, data: null }

    try {
      const response = await fetch('/api/career', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          include_pipeline: true,
          user_data: {
            education: formData.education,
            skills: formData.skills,
            interests: formData.interests,
            selected_careers: formData.selectedCareers,
          },
        }),
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(data?.error || 'Failed to generate a career plan.')
      }
      
      // Validate response structure before storing
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid response structure from backend')
      }
      
      if (!Array.isArray(data.career_scores) || data.career_scores.length === 0) {
        throw new Error('No career scores in response')
      }

      // Store result only if this is still the latest request
      if (requestId === pendingPlan.current?.id) {
        pendingPlan.current = { id: requestId, data }
      }
    } catch (requestError) {
      // Update UI error only if this is still the latest request
      if (requestId === pendingPlan.current?.id) {
        setError(requestError instanceof Error ? requestError.message : 'Something went wrong.')
        setIsLoading(false)
        setThinkingDone(true)
      }
    }
  }

  function handleChange(event) {
    const { name, value } = event.target
    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }))
  }

  function handleCareerToggle(career) {
    setFormData((currentData) => {
      const isSelected = currentData.selectedCareers.includes(career)
      const selectedCareers = isSelected
        ? currentData.selectedCareers.filter((item) => item !== career)
        : [...currentData.selectedCareers, career]

      return {
        ...currentData,
        selectedCareers,
      }
    })
  }

  const hasResult = Boolean(careerPlan && Array.isArray(careerPlan.career_scores) && careerPlan.career_scores.length > 0)

  return (
    <main className="relative min-h-screen overflow-hidden text-slate-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8rem] top-[-8rem] h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute right-[-6rem] top-[12rem] h-80 w-80 rounded-full bg-indigo-500/10 blur-3xl" />
        <div className="absolute bottom-[-8rem] left-[25%] h-72 w-72 rounded-full bg-fuchsia-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <AppHeader aiSource={aiSource} />

        <section className="grid gap-6 xl:grid-cols-[minmax(320px,380px)_minmax(0,1fr)]">
          <div className="xl:sticky xl:top-6 xl:h-fit">
            <ProfileForm
              data={formData}
              onChange={handleChange}
              onCareerToggle={handleCareerToggle}
              onSubmit={handleSubmit}
              isLoading={isLoading}
            />
          </div>

          <div className="space-y-6">
            {isLoading ? (
              <AIThinkingLoader
                steps={pipelineSteps}
                onComplete={handleThinkingComplete}
              />
            ) : null}

            {error ? (
              <div className="glass-panel glass-border animate-fade-up rounded-[1.5rem] border-rose-500/30 px-5 py-4 text-sm leading-6 text-rose-100 shadow-[0_24px_80px_rgba(15,23,42,0.24)]">
                {error}
              </div>
            ) : null}

            {!isLoading && !hasResult && !error ? (
              <ResultCard
                eyebrow="Dashboard"
                title="Ready when you are"
                description="Submit a profile to generate the match score, roadmap, comparison, and reasoning trace."
                accent="from-cyan-400 to-indigo-500"
              >
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] p-4">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Status</p>
                    <p className="mt-2 text-sm font-medium text-white">Ready for analysis</p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">Fill the intake form to generate a career plan.</p>
                  </div>
                  <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] p-4">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Output</p>
                    <p className="mt-2 text-sm font-medium text-white">Structured insights</p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">Comparison, reasoning, and roadmap in one view.</p>
                  </div>
                  <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] p-4 sm:col-span-2 xl:col-span-1">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Source</p>
                    <p className="mt-2 text-sm font-medium text-white">Mock AI</p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">Fallback mode keeps the demo responsive.</p>
                  </div>
                </div>
              </ResultCard>
            ) : null}

            {hasResult ? (
              <div className="grid gap-6 xl:grid-cols-3">
                <div className="xl:col-span-3">
                  <CareerMatchScore
                    score={topCareerScore}
                    explanation={topCareerData?.reasoning_summary || ''}
                    confidenceScore={topCareerScore}
                    jobReadyTime={''}
                    marketDemand={''}
                    className="shadow-[0_24px_80px_rgba(15,23,42,0.24)]"
                  />
                </div>

                <ComparisonCards careers={comparison} className="xl:col-span-3" />

                {/* Pipeline Visualization */}
                <PipelineVisualization className="xl:col-span-3" />

                <ResultCard
                  eyebrow="Signal"
                  title="Recommended career paths"
                  description="The top matches are shown from strongest to weakest."
                  accent="from-cyan-400 to-blue-500"
                >
                  {recommendedPaths.length ? (
                    <div className="space-y-3">
                      {recommendedPaths.map((path, index) => (
                        <div key={path} className="rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3">
                          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">
                            {index === 0 ? 'Primary' : `Option ${index + 1}`}
                          </p>
                          <p className="mt-2 text-sm font-medium text-white">{path}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-[1rem] border border-dashed border-white/12 bg-white/[0.03] px-4 py-5 text-sm leading-6 text-slate-400">
                      No career ranking available yet.
                    </div>
                  )}
                </ResultCard>

                <ResultCard eyebrow="Signal" title="Strengths" accent="from-emerald-400 to-teal-500">
                  {strengths.length ? (
                    <ul className="space-y-3">
                      {strengths.map((strength) => (
                        <li key={strength} className="flex items-start gap-3 rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-slate-200">
                          <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-300" />
                          <span>{strength}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyState label="No strengths surfaced" text="The profile is too sparse to infer strong signals yet." />
                  )}
                </ResultCard>

                <ResultCard eyebrow="Gaps" title="Missing skills" accent="from-amber-400 to-orange-500">
                  {missingSkills.length ? (
                    <ul className="space-y-3">
                      {missingSkills.map((skill) => (
                        <li key={skill} className="flex items-start gap-3 rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-slate-200">
                          <span className="mt-1 h-2.5 w-2.5 rounded-full bg-amber-300" />
                          <span>{skill}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyState label="No obvious gaps" text="The current profile already covers the basics for this path." />
                  )}
                </ResultCard>

                <ResultCard eyebrow="Credentials" title="Certifications" accent="from-indigo-400 to-sky-500">
                  {certifications.length ? (
                    <ul className="space-y-3">
                      {certifications.map((certification) => (
                        <li key={certification} className="flex items-start gap-3 rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-slate-200">
                          <span className="mt-1 h-2.5 w-2.5 rounded-full bg-indigo-300" />
                          <span>{certification}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyState label="No certification suggestions yet" text="The recommendation engine needs a stronger role signal first." />
                  )}
                </ResultCard>

                <ResultCard eyebrow="Resources" title="Learning resources" accent="from-violet-400 to-fuchsia-500">
                  {learningResources.length ? (
                    <ul className="space-y-3">
                      {learningResources.map((resource) => (
                        <li key={resource.title} className="rounded-[1rem] border border-white/10 bg-white/[0.04] p-4 transition-colors duration-200 hover:border-white/20 hover:bg-white/[0.06]">
                          <a
                            href={resource.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-sm font-medium text-white underline-offset-4 hover:underline"
                          >
                            {resource.title}
                          </a>
                          <p className="mt-2 text-[11px] uppercase tracking-[0.16em] text-slate-400">{resource.type}</p>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyState label="No resources available" text="Once the path is clearer, suggested learning links will appear here." />
                  )}
                </ResultCard>

                <RoadmapCard roadmap={roadmap} className="xl:col-span-3" />

                {/* ── AI Transparency: Decision Trace ───────────────── */}
                {decisionTrace?.summary ? (
                  <div className="xl:col-span-3">
                    <DecisionTrace trace={decisionTrace} topCareer={topCareer} />
                  </div>
                ) : null}

                <ResultCard
                  eyebrow="Agent memory"
                  title="Reasoning trace"
                  description="The internal decision trail — showing each inference step the engine made."
                  accent="from-fuchsia-400 to-violet-500"
                  className="xl:col-span-3"
                >
                  <ReasoningTimeline steps={reasoningSteps} />
                </ResultCard>

                {finalExplanation ? (
                  <ResultCard
                    eyebrow="Outcome"
                    title="Final explanation"
                    description="A concise summary of why this career path was selected."
                    accent="from-sky-400 to-indigo-500"
                    className="xl:col-span-3"
                  >
                    <p className="text-sm leading-7 text-slate-200">{finalExplanation}</p>
                  </ResultCard>
                ) : null}
              </div>
            ) : null}
          </div>
        </section>
      </div>
    </main>
  )
}

function EmptyState({ label, text }) {
  return (
    <div className="rounded-[1rem] border border-dashed border-white/12 bg-white/[0.03] px-4 py-5 text-sm leading-6 text-slate-400">
      <p className="text-sm font-medium text-white">{label}</p>
      <p className="mt-2">{text}</p>
    </div>
  )
}
