# 🎓 Campus Duvidha Solver (v2.0)

> **Advanced AI-Powered Multi-Agent Complaint Management System for Elite Educational Institutions.**

Built with a decoupled **React (Vite)** frontend and a **Flask (Python)** backend, this platform provides a professional-grade solution for managing student grievances using a production-ready AI pipeline of 5 specialized agents.

---

## ✨ Primary Evolution (v2.0)

This project has evolved from a Streamlit prototype to a full-stack **Single Page Application (SPA)** with a focus on premium aesthetics, real-time feedback, and secure authorization.

- 💎 **Premium UI/UX**: Custom glassmorphism design system built from scratch with Vanilla CSS.
- ⚡ **Decoupled Architecture**: High-performance React frontend communicating with a RESTful Flask API.
- 🔐 **Secure Access**: Student authentication restricted to college emails and PIN-gated Admin Dashboards.
- 🤖 **AI Traceability**: Real-time visualization of multi-agent execution steps, including latency and raw logic.

---

## 🤖 Multi-Agent Pipeline Architecture

Every complaint is processed by a high-coordinated **Orchestrator** that chains 5 specialized agents:

1.  **Classifier Agent**: Groups the issue into standardized categories (Academic, Hostel, IT, etc.).
2.  **Priority Agent**: Assesses urgency based on safety risks and institutional impact.
3.  **Summarizer Agent**: Translates student descriptions (including Hinglish/slang) into formal summaries.
4.  **Router Agent**: Maps the issue to the exact department responsible for resolution.
5.  **Sentiment Agent**: Detects emotional distress or anger to flag urgent cases for immediate attention.

---

## 📁 Project Structure

```
campus-duvidha-solver/
├── server.py                   # Main Flask API & Static File Server
├── config.py                   # Centralized Environment Configuration
├── requirements.txt            # Python Dependencies
├── .env                        # Environment Variables (OPENAI_API_KEY, etc.)
│
├── frontend/                   # React (Vite) Frontend Application
│   ├── src/
│   │   ├── components/         # Modular Dashboard & Auth Components
│   │   ├── utils/              # API Clients & Shared Logic
│   │   ├── App.jsx             # SPA Routing & Authentication
│   │   └── index.css           # Custom Glassmorphism Design System
│   └── dist/                   # Production build (served by Flask)
│
├── database/
│   ├── db.py                   # SQLite Connection & Schema
│   └── models.py               # Optimized CRUD Operations
│
├── agents/                     # Independent AI Agent Logic
│   ├── orchestrator.py         # Master Pipeline Hub
│   ├── classifier_agent.py     # Agent 1
│   ├── ...                     # Agents 2-5
│   └── fallback.py             # Keyword Heuristic Fallback
│
└── utils/                      # Helper modules (Mail, Notify, Helpers)
```

---

## 🚀 Setup & Installation

### 1. Backend Setup (Flask)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Environment
# Add your OPENAI_API_KEY to .env
# Set ADMIN_PIN (Default: Admin@123)
```

### 2. Frontend Setup (React)

```bash
cd frontend
npm install

# Run Development Server
npm run dev

# Build for Production
npm run build
```

### 3. Running the Integrated App

Once the frontend is built, you can run the entire application via the Flask server:

```bash
python server.py
# Open http://localhost:5000 in your browser
```

---

## 💎 Features at a Glance

### 📝 Student Ecosystem
- **Personalized Portal**: Secure login for `@iiitranchi.ac.in` students.
- **AI-Guided Submission**: Real-time feedback during the AI triage process.
- **My Complaints**: Track historical data and current status of all your grievances.
- **Public Tracker**: Instant lookup of any case via unique Tracking ID.

### 🛡️ Admin Command Center
- **Smart Filtering**: Search and filter thousands of tickets by category, priority, or status.
- **Discussion Threads**: Direct communication channel between admins and students.
- **Agent Traceability**: Inspect the raw outputs and performance of every AI agent per ticket.
- **Analytics Engine**: Real-time Plotly charts for platform workload and department performance.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React 18, Vite, Lucide Icons, Vanilla CSS |
| **Backend** | Python 3.x, Flask, Gunicorn |
| **AI Layer** | OpenAI GPT-4o-mini (Multi-Agent Chaining) |
| **Storage** | SQLite (with optimized relational schema) |
| **Styling** | Custom Glassmorphism Design System |

---

## 📊 Analytics Deep-Dive

The platform includes a specialized analytics dashboard that monitors:
- **Department Workload**: Real-time resolution rates per administrative unit.
- **Issue Distribution**: Categorical breakdown of campus-wide problems.
- **Operational Efficiency**: Average resolution times and AI agent latency.

---

## 📄 License
This project is licensed under the MIT License. Built for professional complaint resolution and high-performance AI integration.
