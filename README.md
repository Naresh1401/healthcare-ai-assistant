# 🏥 AI-Powered Clinical Decision Support System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange.svg)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An LLM-powered clinical decision support assistant featuring medical knowledge retrieval-augmented generation (RAG), drug interaction checking, patient summary generation, and clinical note structuring — all with medical guardrails and HIPAA-aware PII/PHI handling.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit Dashboard                        │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ Clinical  │ │    Drug      │ │  Patient   │ │  Clinical   │  │
│  │ Q&A + RAG │ │ Interaction  │ │  Summary   │ │    SOAP     │  │
│  │           │ │   Checker    │ │ Generator  │ │  Structurer │  │
│  └─────┬─────┘ └──────┬───────┘ └─────┬──────┘ └──────┬──────┘  │
│        │               │               │               │        │
└────────┼───────────────┼───────────────┼───────────────┼────────┘
         │               │               │               │
┌────────▼───────────────▼───────────────▼───────────────▼────────┐
│                        FastAPI Backend                           │
│  /query    /drug-interactions   /summarize-notes  /structure-notes│
└────────┬───────────────┬───────────────┬───────────────┬────────┘
         │               │               │               │
┌────────▼───────────────▼───────────────▼───────────────▼────────┐
│                    Medical Safety Guardrails                     │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────────┐  │
│  │ PII/PHI     │ │ Scope        │ │ Medical Ontology         │  │
│  │ Redaction   │ │ Limitation   │ │ Validation               │  │
│  └─────────────┘ └──────────────┘ └──────────────────────────┘  │
└────────┬───────────────────────────────────────────────┬────────┘
         │                                               │
┌────────▼──────────────────┐  ┌─────────────────────────▼────────┐
│   LangChain Agent Layer   │  │     ChromaDB Vector Store        │
│  ┌──────────────────────┐ │  │  ┌────────────────────────────┐  │
│  │ OpenAI LLM (GPT-4)   │ │  │  │ Medical Guidelines         │  │
│  │ Structured Output    │ │  │  │ Drug Interactions           │  │
│  │ Prompt Templates     │ │  │  │ Symptom-Disease Mappings    │  │
│  └──────────────────────┘ │  │  │ Clinical Protocols          │  │
└───────────────────────────┘  │  └────────────────────────────┘  │
                               └──────────────────────────────────┘
```

---

## Features

- **Clinical Knowledge Q&A (RAG)** — Query medical knowledge base with source citations and confidence scoring
- **Drug Interaction Checker** — Analyze medication lists for interactions with severity levels and clinical significance
- **Patient Summary Generator** — Transform free-text clinical notes into structured summaries with ICD-10 suggestions
- **Clinical Note Structurer** — Convert unstructured notes into SOAP format (Subjective, Objective, Assessment, Plan)
- **Medical Safety Guardrails** — PII/PHI redaction, scope limitation, medical ontology validation
- **HIPAA-Aware PII Handling** — Automatic detection and redaction of protected health information

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/naresh-sampangi/healthcare-ai-assistant.git
cd healthcare-ai-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Load Medical Knowledge Base

```bash
python -m src.knowledge.sample_guidelines
python -m src.knowledge.medical_data_loader
```

### 4. Run the Application

```bash
# API Server
make api

# Streamlit Dashboard
make dashboard
```

---

## Project Structure

```
healthcare-ai-assistant/
├── src/
│   ├── knowledge/          # Medical knowledge ingestion & RAG data
│   │   ├── medical_data_loader.py
│   │   └── sample_guidelines.py
│   ├── agents/             # LangChain-powered clinical agents
│   │   ├── clinical_rag.py
│   │   ├── drug_interaction_checker.py
│   │   ├── patient_summary_generator.py
│   │   └── clinical_note_structurer.py
│   ├── guardrails/         # Medical safety & compliance
│   │   └── medical_safety.py
│   ├── api/                # FastAPI backend
│   │   └── app.py
│   └── dashboard/          # Streamlit frontend
│       └── app.py
├── data/knowledge/         # Synthetic medical knowledge files
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## API Endpoints

| Method | Endpoint              | Description                          |
|--------|-----------------------|--------------------------------------|
| POST   | `/query`              | Clinical knowledge query via RAG     |
| POST   | `/drug-interactions`  | Check drug interaction risks         |
| POST   | `/summarize-notes`    | Generate structured patient summary  |
| POST   | `/structure-notes`    | Convert notes to SOAP format         |
| GET    | `/health`             | Health check                         |

---

## Tech Stack

- **LLM**: OpenAI GPT-4 via LangChain
- **Vector Store**: ChromaDB with OpenAI embeddings
- **Framework**: LangChain for orchestration, structured output parsing
- **API**: FastAPI with Pydantic validation
- **Frontend**: Streamlit interactive dashboard
- **Containerization**: Docker & Docker Compose

---

## ⚠️ Disclaimer

> **This project is for educational and demonstration purposes only.**
>
> This system does **NOT** provide real medical advice, diagnosis, or treatment recommendations.
> All medical knowledge used is synthetic sample data created for demonstration.
> **Always consult qualified healthcare professionals for medical decisions.**
>
> The developers assume no liability for any use of this software in clinical settings.
> This tool is not FDA-approved, not clinically validated, and should never be used as a
> substitute for professional medical judgment.

---

## Author

**Naresh Sampangi**

---

## License

MIT License — see [LICENSE](LICENSE) for details.
