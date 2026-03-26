"""
Clinical Note Structurer.
Converts unstructured clinical notes into SOAP format
(Subjective, Objective, Assessment, Plan) using LLM with medical prompting.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from src.guardrails.medical_safety import MedicalSafetyGuardrails

load_dotenv()


class SubjectiveSection(BaseModel):
    """Subjective section of SOAP note."""
    chief_complaint: str = Field(description="Primary reason for the visit")
    history_of_present_illness: str = Field(description="Detailed narrative of current condition")
    review_of_systems: list[str] = Field(description="Pertinent positive and negative findings")
    past_medical_history: list[str] = Field(description="Relevant past medical history")
    social_history: str = Field(description="Relevant social history (smoking, alcohol, etc.)")
    family_history: str = Field(description="Relevant family medical history")


class ObjectiveSection(BaseModel):
    """Objective section of SOAP note."""
    vital_signs: str = Field(description="Documented vital signs")
    physical_exam: list[str] = Field(description="Physical examination findings")
    lab_results: list[str] = Field(description="Laboratory results if documented")
    imaging: list[str] = Field(description="Imaging results if documented")


class AssessmentSection(BaseModel):
    """Assessment section of SOAP note."""
    primary_diagnosis: str = Field(description="Primary working diagnosis")
    differential_diagnoses: list[str] = Field(description="Differential diagnoses considered")
    clinical_reasoning: str = Field(description="Brief clinical reasoning narrative")


class PlanSection(BaseModel):
    """Plan section of SOAP note."""
    medications: list[str] = Field(description="Medication orders and changes")
    diagnostic_workup: list[str] = Field(description="Ordered labs, imaging, tests")
    procedures: list[str] = Field(description="Procedures planned or performed")
    referrals: list[str] = Field(description="Specialist referrals")
    patient_education: list[str] = Field(description="Education provided to patient")
    follow_up: str = Field(description="Follow-up timing and instructions")


class NoteMetadata(BaseModel):
    """Metadata for the structured note."""
    visit_type: str = Field(description="Type of visit (e.g., new patient, follow-up, urgent)")
    complexity: str = Field(description="Visit complexity: LOW, MODERATE, HIGH, CRITICAL")
    completeness_score: str = Field(description="How complete the original note is: COMPLETE, PARTIAL, MINIMAL")
    missing_elements: list[str] = Field(description="Important clinical elements not documented")


class SOAPNote(BaseModel):
    """Structured SOAP note format."""
    subjective: SubjectiveSection = Field(description="Subjective findings from patient history")
    objective: ObjectiveSection = Field(description="Objective clinical findings")
    assessment: AssessmentSection = Field(description="Clinical assessment and diagnoses")
    plan: PlanSection = Field(description="Treatment and management plan")
    metadata: NoteMetadata = Field(description="Additional note metadata")

SOAP_SYSTEM_PROMPT = """You are a clinical documentation expert specializing in converting unstructured clinical notes into standardized SOAP format (Subjective, Objective, Assessment, Plan).

RULES:
1. Extract and organize information ONLY from the provided clinical notes.
2. Use "Not documented" for any section where information is not available in the notes.
3. Maintain clinical accuracy — do not alter, interpret, or embellish documented findings.
4. Identify missing critical elements that should ideally be documented.
5. Rate the note completeness based on standard documentation requirements.
6. Preserve all clinically relevant details during restructuring.
7. Use standard medical abbreviations where appropriate (BP, HR, RR, SpO2, etc.).
8. Separate pertinent positives from pertinent negatives in review of systems.

UNSTRUCTURED CLINICAL NOTES:
{clinical_notes}

{format_instructions}

⚠️ This structured note is auto-generated and must be reviewed and co-signed by the treating provider.
"""


class ClinicalNoteStructurer:
    """Converts unstructured clinical notes into SOAP format."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4")
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.0)
        self.output_parser = PydanticOutputParser(pydantic_object=SOAPNote)
        self.guardrails = MedicalSafetyGuardrails()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SOAP_SYSTEM_PROMPT),
            ("human", "Convert the clinical notes above into a structured SOAP format."),
        ])

    def structure_note(self, clinical_notes: str, redact_phi: bool = True) -> dict:
        """
        Convert unstructured clinical notes into SOAP format.

        Args:
            clinical_notes: Raw unstructured clinical notes
            redact_phi: Whether to redact PHI before processing

        Returns:
            dict containing structured SOAP note
        """
        processed_notes = clinical_notes
        if redact_phi:
            redaction_result = self.guardrails.redact_phi(clinical_notes)
            processed_notes = redaction_result["redacted_text"]

        chain = self.prompt | self.llm | self.output_parser

        soap_note = chain.invoke({
            "clinical_notes": processed_notes,
            "format_instructions": self.output_parser.get_format_instructions(),
        })

        return soap_note.model_dump()


def structure_clinical_note(clinical_notes: str) -> dict:
    """Convenience function for structuring clinical notes into SOAP format."""
    structurer = ClinicalNoteStructurer()
    return structurer.structure_note(clinical_notes)


if __name__ == "__main__":
    sample_note = """
    Pt is a 45 yo female c/o worsening headaches x 2 weeks. Describes bifrontal
    throbbing pain, 7/10 severity, worse in the morning, associated with nausea
    but no vomiting. No visual changes, no fever, no neck stiffness. Has tried
    OTC ibuprofen 400mg with minimal relief. PMH significant for HTN (on
    losartan 50mg daily), migraine history since age 20. FHx: mother with
    migraines, father with HTN and stroke at age 62.

    Social: non-smoker, occasional alcohol (1-2 drinks/week), works as
    accountant, reports increased work stress recently.

    VS: BP 148/92, HR 78, T 98.6F, RR 16, SpO2 99% RA
    PE: Alert, oriented x3. HEENT: PERRL, no papilledema on fundoscopy.
    Neck supple, no meningeal signs. Neuro: CN II-XII intact, no focal deficits.
    Reflexes 2+ symmetric.

    A: 1) Chronic migraine with increasing frequency — likely tension-type
    component given work stress. 2) Hypertension suboptimally controlled.

    P: 1) Start sumatriptan 50mg PRN for acute migraine episodes
    2) Start topiramate 25mg daily for migraine prophylaxis, titrate to 50mg
    3) Increase losartan to 100mg daily for BP control
    4) MRI brain without contrast to rule out secondary causes
    5) Headache diary for 4 weeks
    6) Stress management counseling referral
    7) F/u in 4 weeks, sooner if headache worsens or new neurological symptoms
    """
    result = structure_clinical_note(sample_note)
    print("=== SOAP NOTE ===")
    print(f"Chief Complaint: {result['subjective']['chief_complaint']}")
    print(f"Primary Dx: {result['assessment']['primary_diagnosis']}")
    print(f"Complexity: {result['metadata']['complexity']}")
    print(f"Missing Elements: {result['metadata']['missing_elements']}")
