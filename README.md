# 🏥 Healthcare Intake Agent

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-✓-blue.svg)](https://www.docker.com/)
[![Groq](https://img.shields.io/badge/Groq-API-purple.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered healthcare intake system that uses Groq's fast inference API for preliminary symptom analysis, structured patient data collection, and medical history documentation.

## ✨ Features

- 🏥 **Clinical Intake Agent** - Professional, empathetic conversation flow with structured questioning
- 🔍 **RAG Pipeline** - Retrieval-augmented generation using medical guidelines
- 🛡️ **Safety Guardrails** - Emergency detection, no diagnosis/prescription rules
- 📊 **Structured Data** - Automatic extraction of symptoms, conditions, allergies, medications
- 🚀 **Fast Inference** - Powered by Groq's llama-3.3-70b-versatile model
- 🐳 **Dockerized** - Complete containerization for easy deployment
- 🎨 **Streamlit UI** - Beautiful chat interface with real-time patient summary
- 💾 **FAISS Vector DB** - Lightweight, efficient similarity search for medical guidelines

## 🏗️ Architecture
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                                    DOCKER COMPOSE                                         ║
║                                                                                           ║
║  ┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐║
║  │      STREAMLIT UI       │    │      FASTAPI APP       │    │       FAISS DB         │║
║  │       Port: 8501        │    │       Port: 8000        │    │     Memory Store       │║
║  ├─────────────────────────┤    ├─────────────────────────┤    ├─────────────────────────┤║
║  │  ┌───────────────────┐  │    │  ┌───────────────────┐  │    │  ┌───────────────────┐  │║
║  │  │   Chat Interface  │  │    │  │   Intake Agent   │  │    │  │     Medical       │  │║
║  │  │   User Input      │──┼───▶│  │   Process Message│──┼───▶│  │   Guidelines     │  │║
║  │  └───────────────────┘  │    │  └───────────────────┘  │    │  └───────────────────┘  │║
║  │                         │    │                         │    │                         │║
║  │  ┌───────────────────┐  │    │  ┌───────────────────┐  │    │  ┌───────────────────┐  │║
║  │  │  Patient Summary  │  │    │  │  Safety Rules    │  │    │  │    Embeddings     │  │║
║  │  │  Real-time Updates│◀─┼───▶│  │  Data Extraction │◀─┼───▶│  │   Similarity     │  │║
║  │  └───────────────────┘  │    │  └───────────────────┘  │    │  │     Search       │  │║
║  └─────────────────────────┘    └─────────────────────────┘    │  └───────────────────┘  │║
║                                          │                     └─────────────────────────┘║
║                                          │                                │               ║
║                                          │                           ┌────▼────┐          ║
║                                          │                           │ Medical │          ║
║                                          │                           │Guidelines│          ║
║                                          │                           └─────────┘          ║
║                                          │                                                ║
║                                   ┌──────▼──────┐                                         ║
║                                   │   GROQ API  │                                         ║
║                                   │  External   │                                         ║
║                                   │ llama-3.3   │                                         ║
║                                   └─────────────┘                                         ║
║                                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝

                                    DATA FLOW
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. User Input → Streamlit UI → FastAPI Backend                                         │
│ 2. Backend → FAISS (Retrieve relevant medical guidelines)                              │
│ 3. Backend → Groq API (Generate clinical response with context)                        │
│ 4. Response → Data Extraction → Update patient record                                  │
│ 5. Updated summary → Streamlit UI sidebar (Real-time refresh)                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Data Flow:

User input → Streamlit UI → FastAPI Backend

Backend → FAISS (retrieve medical guidelines)

Backend → Groq API (generate clinical response)

Response → Data extraction → Store patient info

Updated summary → Streamlit UI sidebar



## 📋 Prerequisites

- **Docker** and **Docker Compose** (version 2.0+)
- **Groq API Key** (get from [console.groq.com](https://console.groq.com))
- 4GB+ RAM (for FAISS embeddings)
- 2GB+ free disk space

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/rayaproluaditya/healthcare-intake-agent.git
cd healthcare-intake-agent

2. Set Up Environment Variables
Create a .env file with your Groq API key:
cp .env.example .env

edit :
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.3-70b-versatile
FAISS_PERSIST_DIR=./data/faiss_db
TEMPERATURE=0.3
MAX_TOKENS=1000
LOG_LEVEL=INFO

3. Run with Docker Compose
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d

4. Access the Application
Service	URL	Description
Streamlit UI	http://localhost:8501	Main chat interface
Backend API	http://localhost:8000	FastAPI endpoints
API Docs	http://localhost:8000/docs	Swagger documentation
ChromaDB UI	http://localhost:8001	Vector DB interface

5. Test the API
# Health check
curl http://localhost:8000/health

# Send a message
curl -X POST http://localhost:8000/api/v1/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'

# Get patient summary
curl http://localhost:8000/api/v1/summary

Example Conversation
User: I have a headache for the past 3 days

Agent: Thank you for sharing that. I understand headaches can be uncomfortable. 
To better understand, could you tell me:
1. Where exactly do you feel the pain?
2. Is it throbbing, sharp, or pressure-like?
3. On a scale of 1-10, how severe is it?
4. Have you noticed any other symptoms like nausea or sensitivity to light?

User: It's throbbing on the left side, about 7 out of 10. I also feel nauseous.

Agent: Thank you for those details. The throbbing quality and location are helpful.
1. Have you experienced headaches like this before?
2. Does anything make it better or worse?
3. Do you have any medical conditions or take any medications?

User: I have high blood pressure and take lisinopril.

Agent: Thank you for sharing your medical history. This information will help your 
healthcare provider. Do you have any allergies to medications?

User: I'm allergic to penicillin.

Agent: Thank you for mentioning that. I've recorded your information:
- Headache (3 days, left side, 7/10, throbbing)
- Nausea
- Hypertension (lisinopril)
- Penicillin allergy

Your healthcare provider will have this information ready for review.



Project Structure

healthcare-intake-agent/
├── app/                          # Backend application
│   ├── __init__.py
│   ├── main.py                   # FastAPI entry point
│   ├── config.py                 # Configuration
│   ├── models/                   # Data models
│   │   ├── patient_data.py       # Patient intake schema
│   │   └── conversation.py       # Conversation models
│   ├── agents/                   # Core agent logic
│   │   ├── intake_agent.py       # Main intake agent
│   │   └── safety_guardrails.py  # Safety rules
│   ├── vector_db/                # Vector database
│   │   ├── faiss_client.py       # FAISS wrapper
│   │   └── document_processor.py # Medical guidelines
│   ├── fine_tuning/              # Clinical tone fine-tuning
│   │   └── fine_tune_clinical.py
│   └── api/                      # API endpoints
│       ├── routes.py             # Route definitions
│       └── schemas.py            # Request/response models
├── data/                         # Data storage
│   ├── medical_guidelines/       # Medical knowledge base
│   │   ├── cdc_symptoms.txt
│   │   ├── diagnostic_protocols.txt
│   │   ├── treatment_guidelines.txt
│   │   └── emergency_protocols.txt
│   └── faiss_db/                 # FAISS index storage
├── streamlit_app.py              # Frontend UI
├── requirements.txt              # Backend dependencies
├── requirements_frontend.txt     # Frontend dependencies
├── Dockerfile                    # Backend container
├── Dockerfile.streamlit          # Frontend container
├── docker-compose.yml            # Orchestration
├── .env.example                  # Environment template
└── README.md                     # This file



Design Choices
LLM Selection: Groq (llama-3.3-70b-versatile)
Why Groq?

Speed: 10x faster inference compared to traditional APIs (sub-second responses)

Cost: More cost-effective for production deployment

Quality: Llama-3.3-70B provides excellent clinical reasoning

Scale: Handles high-throughput medical intake scenarios

Trade-offs:

❌ No traditional fine-tuning (uses few-shot learning instead)

❌ Limited to available Groq models

✅ Excellent for real-time conversational intake

Vector Database: FAISS
Why FAISS?

Lightweight: No SQLite dependencies, runs in memory

Fast: Optimized similarity search for embeddings

No SQLite issues: Works perfectly on Apple Silicon and Linux

Simple: Easy to deploy and maintain

Trade-offs:

❌ No built-in persistence (we implement our own)

❌ No automatic updates (requires manual index management)

✅ Perfect for medical guidelines (lightweight document set)

Agent Framework: Custom with Groq API
Why Custom Framework?

Control: Full control over prompts and responses

Flexibility: Easy to modify clinical tone

Lightweight: No heavy dependencies (LangChain, etc.)

Direct: Direct Groq API calls for reliability

Trade-offs:

❌ More code to maintain

❌ Need to handle edge cases manually

✅ Better performance and debugging

Frontend: Streamlit
Why Streamlit?

Rapid Development: Built entire UI in < 200 lines

Real-time Updates: Automatic sidebar refresh

Chat Components: Built-in chat message support

Easy Deployment: Single file, Docker-friendly

Trade-offs:

❌ Less customizable than React

❌ Limited advanced UI features

✅ Perfect for medical intake interface

Fine-tuning: Few-shot Learning
Why Few-shot Learning?

No Training: Works immediately with Groq

Controlled: Easy to adjust clinical tone

Transparent: Prompts are human-readable

Iterative: Quick to improve with examples

Trade-offs:

❌ Less sophisticated than full fine-tuning

❌ Prompt engineering required

✅ Immediate results, no training costs




Development Commands
Run Locally (Without Docker)

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_frontend.txt

# Run backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run frontend (new terminal)
streamlit run streamlit_app.py



Docker Commands
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart services
docker-compose restart


Testing
# Run backend tests
pytest tests/test_api.py -v

# Test Groq connection
python scripts/test_groq.py

# Run fine-tuning
python scripts/run_fine_tuning.py

# Evaluate clinical tone
python scripts/evaluate_clinical_tone.py

Sample Output
Patient Summary JSON


{
  "patient_data": {
    "chief_complaint": "Headache",
    "symptoms": [
      {
        "name": "Headache",
        "duration": "3 days",
        "severity": "moderate",
        "location": "left side",
        "description": "throbbing"
      },
      {
        "name": "Nausea",
        "severity": "mild"
      }
    ],
    "preexisting_conditions": ["Hypertension"],
    "medications": ["Lisinopril"],
    "allergies": ["Penicillin"]
  },
  "completion_percentage": 66.67,
  "recommendation": "Ready for provider review"
}


