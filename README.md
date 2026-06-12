# AI Career Mentor Agent

A clean full-stack starter for a hackathon project.

## Project Structure

```text
AI-Career-Mentor-Agent/
  backend/   # Flask API
  frontend/  # React + Vite app
  README.md
```

## Backend

Python Flask API with CORS enabled.

### Career Mentor Service Abstraction

```text
Career Mentor Service
├── MockCareerService
├── OpenAIService
├── AzureOpenAIService
└── FoundryIQService (placeholder)
```

The backend currently defaults to `MockCareerService`. To switch providers later, set `CAREER_MENTOR_PROVIDER` to `openai`, `azure_openai`, or `foundry_iq`.

### Stack

- Flask
- flask-cors
- Modular files: `app.py` and `ai_engine.py`

### Install

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

### Route

- `POST /api/career`

Example request:

```json
{
  "user_data": {
    "education": "BSc Computer Science",
    "skills": "Python, React, SQL",
    "interests": "building web apps"
  }
}
```

Example response:

```json
{
  "career_path": "Data Analyst",
  "reasoning": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
  "strengths": ["..."],
  "missing_skills": ["..."],
  "roadmap": {
    "month_1": ["..."],
    "month_2": ["..."],
    "month_3": ["..."]
  },
  "final_advice": "..."
}
```

## Frontend

React app built with Vite.

### Stack

- React
- Vite
- Dev proxy from `/api` to the backend during local development

### Install

```bash
cd frontend
npm install
```

### Run

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

## How To Run Both

1. Start the backend from `backend/` with `python app.py`.
2. Start the frontend from `frontend/` with `npm run dev`.
3. Open `http://localhost:5173` in the browser.

## Notes

- The AI logic is intentionally a placeholder for now.
- The code structure is minimal, but ready to scale.
- No styling has been added yet.
