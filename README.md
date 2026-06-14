<div align="center">
  <img src="https://via.placeholder.com/150x150?text=AI+Mentor" alt="AI Career Mentor Logo" width="120" height="120" />
  <h1>🚀 AI Career Mentor Agent</h1>
  <p><strong>A production-grade, deterministic AI advisor that maps your skills to your future.</strong></p>
</div>

<br />

> **“Stop guessing your next career move. Let the AI build your roadmap.”**

---

## 🛑 The Problem

Navigating a career in tech is overwhelming. The industry moves fast, skill overlap is confusing, and generic advice like "just learn Python" doesn't cut it. Junior developers and career switchers are left guessing: *What role actually fits my unique, messy combination of skills? What should I learn next to get hired?*

Traditional quizzes are too rigid, and raw LLM chatbots hallucinate random advice that isn't actionable.

## 💡 The Solution

The **AI Career Mentor Agent** is a multi-layered, deterministic recommendation engine. It takes messy human input (slang, mixed languages, scattered skills) and runs it through a strict 8-layer processing pipeline to output a highly personalized, mathematically grounded career roadmap. 

It feels like chatting with an empathetic human mentor, but under the hood, it’s powered by a rigorous vector-scoring engine and strict schema validation.

---

## 🏗 System Architecture: The 8-Layer Pipeline

This isn't just a wrapper around an LLM API. It's a structured, explainable AI pipeline designed for production stability.

1. **📥 Input Layer**: Captures messy, informal user input (skills, education, interests).
2. **🧹 Intent Normalizer**: Pre-processes raw text using synonym mapping, noise filtering, and confidence scoring. Converts *"idk, je fais du dev web"* into structured vector signals like `[react, node, html, css]`.
3. **🧮 Vector Scoring Engine**: A hybrid deterministic engine that calculates `(0.55 × cosine_sim) + (0.30 × skill_coverage) + (0.15 × alignment_bonus)` to rank careers predictably without LLM hallucinations.
4. **🧠 Explanation Engine**: Decouples the "math" from the "mentorship". Generates human-readable reasoning and transparent decision traces (e.g., *"Why did Data Analyst win? Why did Backend Developer rank lower?"*).
5. **🛡 Final Response Builder**: The ultimate authority layer. Enforces strict JSON contracts, handles fallbacks gracefully, and ensures the UI never receives broken data.
6. **🌐 API Layer (Flask)**: A robust, stateless backend gateway serving the AI inferences.
7. **🖥 Frontend (React)**: A gorgeous, glassmorphism-inspired UI designed for premium user experiences.
8. **✨ AI Thinking UI Layer**: An enterprise-grade UX component that simulates the AI's step-by-step reasoning process (scanner sweeps, pulse effects, cascading steps) before revealing the final recommendation.

---

## 🌟 Key Features

- **Deterministic AI Scoring**: Run the same profile 100 times, get the exact same mathematical ranking. No random LLM drift.
- **Career Matching Engine**: Multidimensional vector space analysis matching your specific stack to real-world roles.
- **Actionable Roadmap Generator**: Dynamic 3-month action plans tailored to close your specific skill gaps.
- **Explainable AI (Reasoning Trace)**: Complete transparency. The AI tells you *exactly* which skills boosted your score and why other roles were rejected.
- **Comparison Mode**: See how you stack up against alternative career paths side-by-side.
- **Fallback-Safe Architecture**: Gracefully degrades. If the LLM goes down, the deterministic mock engine takes over seamlessly.

---

## 🛠 Tech Stack

- **Backend**: Python, Flask, RESTful APIs
- **AI / ML**: Vector Similarity Math, `intent_normalizer`, OpenAI/Groq (Optional for dynamic enrichment)
- **Frontend**: React, Vite, TailwindCSS (Vanilla CSS for core animations)
- **Testing**: `pytest` regression suite for deterministic validation

---

## 📄 Example JSON Contract

The system enforces a strict, UI-safe contract:

```json
{
  "ai_source": "mock",
  "top_career": "Data Analyst",
  "career_scores": [
    {
      "career": "Data Analyst",
      "score": 80,
      "top_positive_factors": ["python", "sql", "data analysis"],
      "missing_critical_skills": ["visualization tools"]
    }
  ],
  "decision_trace": {
    "summary": "This profile is a strong match for Data Analyst...",
    "why_top_career_won": "Data Analyst was selected because this profile showed the strongest alignment in data workflows...",
    "why_others_failed": {
      "Backend Developer": "Scored lower due to: limited exposure to system design..."
    },
    "key_drivers": [
      "Strong foundation in data workflows — the single biggest factor..."
    ]
  },
  "roadmap": {
    "month_1": ["Deep dive into intermediate Data Analyst concepts"],
    "month_2": ["Build a full-stack or complex project"],
    "month_3": ["Prepare for initial interviews"]
  },
  "normalization": {
    "clean_skills": ["python", "sql", "data analysis"],
    "detected_intents": ["data_analytics"],
    "confidence_map": {"python": 0.9, "sql": 0.9}
  }
}
```

---

## 📸 UI Screenshots

> *[Placeholder: Add screenshot of the AI Thinking Loader]*

> *[Placeholder: Add screenshot of the beautiful Glassmorphism Results Dashboard]*

> *[Placeholder: Add screenshot of the Decision Trace & Reasoning Timeline]*

---

## 🏆 Why This Wins Hackathons

Judges see hundreds of "ChatGPT Wrappers". Here is why this architecture stands out:

1. **Production-Style Architecture**: It demonstrates enterprise patterns (Normalization -> Scoring -> Explanation -> Strict Formatting) instead of blindly trusting an LLM zero-shot prompt.
2. **Deterministic & Explainable AI**: The system is mathematically stable and explains its logic transparently, solving the "black box" problem of modern AI.
3. **Full-Stack Polish**: From the complex backend vector engine to the premium React frontend with micro-animations, it’s a complete end-to-end product.
4. **Resilience**: The `FinalResponseBuilder` and fallback-safe design prove an understanding of real-world software engineering constraints.

---

## 🚀 Future Improvements

- **Streaming AI**: Implement Server-Sent Events (SSE) for real-time text streaming in the explanation engine.
- **Azure Foundry Integration**: Connect to Azure OpenAI services for enterprise-grade LLM inference and guardrails.
- **Real Vector DB (FAISS/Pinecone)**: Migrate the in-memory skill vectors to a dedicated vector database to support thousands of nuanced skill dimensions.
