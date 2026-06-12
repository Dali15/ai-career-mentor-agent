import { useEffect, useState } from 'react'

import AppHeader from './AppHeader'
import LoadingState from './LoadingState'
import CareerMatchScore from './CareerMatchScore'
import CareerComparisonTable from './CareerComparisonTable'
import ProfileForm from './ProfileForm'
import ReasoningTimeline from './ReasoningTimeline'
import ResultCard from './ResultCard'
import ResultsSkeleton from './ResultsSkeleton'
import RoadmapCard from './RoadmapCard'

const initialFormData = {
  education: '',
  skills: '',
  interests: '',
  selectedCareers: ['DevOps Engineer', 'Data Analyst', 'Backend Developer', 'Cloud Engineer'],
}

const thinkingSteps = [
  'Analyzing profile',
  'Matching careers',
  'Calculating scores',
  'Building roadmap',
]

export default function Homepage() {
  const [formData, setFormData] = useState(initialFormData)
  const [careerPlan, setCareerPlan] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeThinkingStep, setActiveThinkingStep] = useState(0)

  const recommendedPaths = Array.isArray(careerPlan?.recommended_paths) ? careerPlan.recommended_paths : []
  const learningResources = Array.isArray(careerPlan?.learning_resources) ? careerPlan.learning_resources : []
  const certifications = Array.isArray(careerPlan?.certifications) ? careerPlan.certifications : []
  const reasoningTrace = Array.isArray(careerPlan?.reasoning_trace) ? careerPlan.reasoning_trace : []
  const reasoningSteps = Array.isArray(careerPlan?.reasoning) ? careerPlan.reasoning : []
  const comparison = Array.isArray(careerPlan?.career_comparison) ? careerPlan.career_comparison : []
  const aiSource = careerPlan?.ai_source || 'mock'

  useEffect(() => {
    if (!isLoading) {
      setActiveThinkingStep(0)
      return undefined
    }

    const timer = window.setInterval(() => {
      setActiveThinkingStep((currentStep) => Math.min(currentStep + 1, thinkingSteps.length - 1))
    }, 850)

    return () => window.clearInterval(timer)
  }, [isLoading])

  async function handleSubmit(event) {
    event.preventDefault()
    setIsLoading(true)
    setError('')
    setCareerPlan(null)

    try {
      const response = await fetch('/api/career', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
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

      setCareerPlan(data)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Something went wrong.')
    } finally {
      setIsLoading(false)
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

  const hasResult = Boolean(careerPlan)

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
              <div className="space-y-6">
                <LoadingState steps={thinkingSteps} activeStep={activeThinkingStep} />
                <ResultsSkeleton />
              </div>
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
                    score={careerPlan?.career_match_score ?? 0}
                    explanation={careerPlan?.career_match_explanation ?? ''}
                    confidenceScore={careerPlan?.confidence_score ?? 0}
                    jobReadyTime={careerPlan?.job_ready_time ?? ''}
                    marketDemand={careerPlan?.market_demand ?? ''}
                    className="shadow-[0_24px_80px_rgba(15,23,42,0.24)]"
                  />
                </div>

                <CareerComparisonTable comparison={comparison} bestCareer={careerPlan?.career_path ?? ''} className="xl:col-span-3" />

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
                  {careerPlan.strengths?.length ? (
                    <ul className="space-y-3">
                      {careerPlan.strengths?.map((strength) => (
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
                  {careerPlan.missing_skills?.length ? (
                    <ul className="space-y-3">
                      {careerPlan.missing_skills?.map((skill) => (
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

                <RoadmapCard roadmap={careerPlan.roadmap} className="xl:col-span-3" />

                <ResultCard
                  eyebrow="Agent memory"
                  title="Reasoning trace"
                  description="The internal decision trail is shown so the recommendation stays transparent."
                  accent="from-fuchsia-400 to-violet-500"
                  className="xl:col-span-3"
                >
                  <ReasoningTimeline steps={reasoningTrace.length ? reasoningTrace : reasoningSteps} />
                </ResultCard>

                <ResultCard
                  eyebrow="Outcome"
                  title="Final advice"
                  description="A concise next step to turn the recommendation into measurable progress."
                  accent="from-sky-400 to-indigo-500"
                  className="xl:col-span-3"
                >
                  <p className="text-sm leading-7 text-slate-200">{careerPlan?.final_advice ?? ''}</p>
                </ResultCard>
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
