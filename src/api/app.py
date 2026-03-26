"""
FastAPI backend for the Clinical Decision Support System.
Provides endpoints for RAG queries, drug interactions, patient summaries, and SOAP notes.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agents.clinical_rag import ClinicalRAGPipeline
from src.agents.drug_interaction_checker import DrugInteractionChecker
from src.agents.patient_summary_generator import PatientSummaryGenerator
from src.agents.clinical_note_structurer import ClinicalNoteStructurer
from src.guardrails.medical_safety import MedicalSafetyGuardrails

load_dotenv()

# --- Singletons initialized at startup ---
agents: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents on startup."""
    agents["rag"] = ClinicalRAGPipeline()
    agents["drug_checker"] = DrugInteractionChecker()
    agents["summary_gen"] = PatientSummaryGenerator()
    agents["note_structurer"] = ClinicalNoteStructurer()
    agents["guardrails"] = MedicalSafetyGuardrails()
    yield
    agents.clear()


app = FastAPI(
    title="AI-Powered Clinical Decision Support System",
    description=(
        "LLM-powered clinical assistant with medical knowledge RAG, "
        "drug interaction checking, patient summary generation, "
        "and clinical note structuring."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# --- Request/Response Models ---

class ClinicalQueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000, description="Clinical knowledge question")


class ClinicalQueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    confidence: str
    num_sources: int


class DrugInteractionRequest(BaseModel):
    medications: list[str] = Field(
        ..., min_length=2, max_length=20,
        description="List of medication names to check for interactions",
    )


class PatientNotesRequest(BaseModel):
    clinical_notes: str = Field(..., min_length=10, max_length=10000, description="Raw clinical notes text")
    redact_phi: bool = Field(default=True, description="Whether to redact PHI before processing")


class HealthResponse(BaseModel):
    status: str
    version: str
    agents_loaded: list[str]


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_loaded=list(agents.keys()),
    )


@app.post("/query", response_model=ClinicalQueryResponse, tags=["Clinical RAG"])
async def clinical_query(request: ClinicalQueryRequest):
    """
    Query the clinical knowledge base using RAG.
    Returns an evidence-based answer with source citations and confidence score.
    """
    try:
        # Run input through guardrails
        guardrails: MedicalSafetyGuardrails = agents["guardrails"]
        input_check = guardrails.redact_phi(request.question)

        result = agents["rag"].query(input_check["redacted_text"])
        return ClinicalQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/drug-interactions", tags=["Drug Interactions"])
async def check_drug_interactions(request: DrugInteractionRequest):
    """
    Check for drug-drug interactions among a list of medications.
    Returns severity levels, mechanisms, and management recommendations.
    """
    try:
        report = agents["drug_checker"].check_interactions(request.medications)
        return report.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drug interaction check failed: {str(e)}")


@app.post("/summarize-notes", tags=["Patient Summary"])
async def summarize_notes(request: PatientNotesRequest):
    """
    Generate a structured patient summary from raw clinical notes.
    Includes ICD-10 suggestions and follow-up action items.
    """
    try:
        result = agents["summary_gen"].generate_summary(
            request.clinical_notes, redact_phi=request.redact_phi
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@app.post("/structure-notes", tags=["SOAP Notes"])
async def structure_notes(request: PatientNotesRequest):
    """
    Convert unstructured clinical notes into SOAP format.
    (Subjective, Objective, Assessment, Plan)
    """
    try:
        result = agents["note_structurer"].structure_note(
            request.clinical_notes, redact_phi=request.redact_phi
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Note structuring failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)
