<div align="center">
  <!-- Replace the placeholder with a real logo if you have one -->
  <h1>🤖 AI Career Mentor Agent</h1>
  <p>
    <em>A Full-Stack AI-Powered Application to Guide and Accelerate Your Career Journey</em>
  </p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![React](https://img.shields.io/badge/React-18.0-blue.svg)](https://reactjs.org/)
  [![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)](https://flask.palletsprojects.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)
</div>

<br />

## 🌟 Overview

The **AI Career Mentor Agent** is a full-stack platform designed to analyze user profiles (education, skills, and interests) and generate intelligent, actionable career roadmaps. Leveraging advanced Large Language Models (LLMs), the platform identifies optimal career paths, highlights strengths and missing skills, and constructs a step-by-step roadmap for success.

## ✨ Features

- **Personalized Career Pathways:** Intelligent matching of your background to ideal tech and business roles.
- **Multi-Provider AI Abstraction:** Seamlessly switch between AI engines (Mock, OpenAI, Azure OpenAI, FoundryIQ).
- **Actionable Roadmaps:** Month-by-month actionable steps to bridge the gap to your dream job.
- **Skill Gap Analysis:** Objective identification of strengths and areas for improvement.
- **Modern Tech Stack:** Built with a blazing-fast React/Vite frontend and a lightweight, scalable Python Flask backend.

## 🏗️ Architecture

```text
AI-Career-Mentor-Agent/
├── backend/          # Python Flask API & AI Engine
│   ├── app.py        # API Entrypoint
│   └── services/     # Pluggable Career Mentor Services
└── frontend/         # React + Vite Application
    ├── src/          # UI Components & Views
    └── index.html
```

### AI Service Abstraction Layer

The backend uses a flexible strategy pattern to interact with different LLM providers, making it future-proof and easy to extend. By simply updating the `CAREER_MENTOR_PROVIDER` environment variable, you can switch the intelligence engine without altering the core logic.

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

- Node.js (v18+)
- Python (3.10+)

### 1. Clone the Repository

```bash
git clone https://github.com/Dali15/ai-career-mentor-agent.git
cd ai-career-mentor-agent
```

### 2. Backend Setup (Flask API)

Navigate to the backend directory, set up your virtual environment, and start the server:

```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```
*The API will be available at `http://localhost:5000`.*

### 3. Frontend Setup (React + Vite)

Open a new terminal window, navigate to the frontend directory, and start the development server:

```bash
cd frontend
npm install
npm run dev
```
*The application will be available at `http://localhost:5173`.*

## 📖 API Documentation

### `POST /api/career`

Analyzes user profile data and returns a structured career roadmap.

**Request Body:**
```json
{
  "user_data": {
    "education": "BSc Computer Science",
    "skills": "Python, React, SQL",
    "interests": "building web apps, data engineering"
  }
}
```

**Response:**
```json
{
  "career_path": "Data Engineer / Full Stack Developer",
  "reasoning": [
    "Your background in CS provides a strong foundation.",
    "Python and SQL are essential for Data Engineering."
  ],
  "strengths": ["Python", "SQL", "Software Architecture"],
  "missing_skills": ["Cloud Platforms (AWS/GCP)", "Docker", "CI/CD"],
  "roadmap": {
    "month_1": ["Master Docker basics", "Build a microservice"],
    "month_2": ["Learn AWS core services", "Deploy your app"],
    "month_3": ["Implement CI/CD pipelines", "Start applying"]
  },
  "final_advice": "Focus on bridging the deployment and cloud gap."
}
```

## 🛠️ Configuration

Configure the active AI provider by setting environment variables in the `backend/.env` file:

```env
# Available options: mock, openai, azure_openai, foundry_iq
CAREER_MENTOR_PROVIDER=mock

# Provide the corresponding API keys for active providers
OPENAI_API_KEY=your_key_here
```

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
