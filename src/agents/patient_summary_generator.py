"""
Patient Summary Generator.
Takes raw clinical notes and generates structured patient summaries
with ICD-10 code suggestions, follow-up items, using LangChain output parsing.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from src.guardrails.medical_safety import MedicalSafetyGuardrails

load_dotenv()


class PatientDemographics(BaseModel):
    """Extracted patient demographics."""
    age: str = Field(description="Patient age or age range")
    sex: str = Field(description="Patient sex/gender")
    relevant_history: str = Field(description="Relevant past medical/social history")


class ICD10Suggestion(BaseModel):
    """Suggested ICD-10 code."""
    code: str = Field(description="ICD-10 code (e.g., E11.9)")
    description: str = Field(description="Code description")
    confidence: str = Field(description="Confidence level: HIGH, MEDIUM, or LOW")


class PatientSummary(BaseModel):
    """Complete structured patient summary."""
    demographics: PatientDemographics = Field(description="Patient demographic information")
    chief_complaint: str = Field(description="Primary reason for visit")
    history_of_present_illness: str = Field(description="Detailed HPI narrative")
    past_medical_history: list[str] = Field(description="List of past medical conditions")
    current_medications: list[str] = Field(description="List of current medications with doses")
    allergies: list[str] = Field(description="Known allergies and reactions")
    assessment: str = Field(description="Clinical assessment and working diagnosis")
    plan: list[str] = Field(description="Treatment plan items")
    icd10_suggestions: list[ICD10Suggestion] = Field(description="Suggested ICD-10 codes")
    follow_up_actions: list[str] = Field(description="Required follow-up action items")
    critical_alerts: list[str] = Field(description="Any critical findings or alerts")


SUMMARY_SYSTEM_PROMPT = """You are a clinical documentation specialist. Your role is to analyze raw clinical notes and extract structured patient summary information.

RULES:
1. Extract only information explicitly stated in or clearly implied by the clinical notes.
2. If information is not available, use "Not documented" or empty list as appropriate.
3. Suggest ICD-10 codes based on documented conditions with confidence levels.
4. Identify follow-up action items from the clinical notes.
5. Flag any critical findings or safety concerns.
6. Do NOT fabricate or assume clinical information not present in the notes.
7. All patient-identifiable information should be noted but will be handled by the guardrails layer.

CLINICAL NOTES:
{clinical_notes}

{format_instructions}

⚠️ This is an automated summary for clinical documentation assistance only. All outputs must be reviewed and verified by a licensed healthcare provider.
"""


class PatientSummaryGenerator:
    """Generates structured patient summaries from clinical notes."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4")
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.0)
        self.output_parser = PydanticOutputParser(pydantic_object=PatientSummary)
        self.guardrails = MedicalSafetyGuardrails()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SUMMARY_SYSTEM_PROMPT),
            ("human", "Generate a structured patient summary from the clinical notes above."),
        ])

    def generate_summary(self, clinical_notes: str, redact_phi: bool = True) -> dict:
        """
        Generate a structured patient summary from clinical notes.

        Args:
            clinical_notes: Raw clinical notes text
            redact_phi: Whether to redact PHI from the input before processing

        Returns:
            dict containing the structured patient summary
        """
        # Apply PHI redaction if enabled
        processed_notes = clinical_notes
        phi_detections = []
        if redact_phi:
            redaction_result = self.guardrails.redact_phi(clinical_notes)
            processed_notes = redaction_result["redacted_text"]
            phi_detections = redaction_result["detections"]

        # Generate structured summary
        chain = self.prompt | self.llm | self.output_parser

        summary = chain.invoke({
            "clinical_notes": processed_notes,
            "format_instructions": self.output_parser.get_format_instructions(),
        })

        result = summary.model_dump()
        result["phi_redactions_applied"] = len(phi_detections)
        result["processing_notes"] = (
            "PHI elements were detected and redacted before processing."
            if phi_detections
            else "No PHI elements detected in input."
        )

        return result


def generate_patient_summary(clinical_notes: str) -> dict:
    """Convenience function for generating patient summaries."""
    generator = PatientSummaryGenerator()
    return generator.generate_summary(clinical_notes)


if __name__ == "__main__":
    sample_notes = """
    Patient is a 58-year-old male presenting with complaints of increased thirst
    and frequent urination for the past 3 weeks. Has a history of hypertension
    managed with lisinopril 20mg daily and amlodipine 5mg daily. Reports family
    history of diabetes (mother and brother). BMI 32.4. BP today 142/88.
    Fasting glucose 186 mg/dL. HbA1c 8.2%.

    Assessment: New diagnosis of Type 2 Diabetes Mellitus with suboptimal
    blood pressure control despite current regimen.

    Plan:
    - Start metformin 500mg BID, titrate to 1000mg BID over 4 weeks
    - Increase amlodipine to 10mg daily
    - Order lipid panel, renal function, urine microalbumin
    - Diabetic education referral
    - Nutrition counseling for diabetic diet
    - Follow-up in 4 weeks with repeat HbA1c in 3 months
    - Ophthalmology referral for baseline diabetic eye exam

    Allergies: Sulfa drugs (rash), Penicillin (anaphylaxis)
    """
    result = generate_patient_summary(sample_notes)
    print(f"Chief Complaint: {result['chief_complaint']}")
    print(f"Assessment: {result['assessment']}")
    print(f"ICD-10 Suggestions: {len(result['icd10_suggestions'])}")
    for code in result["icd10_suggestions"]:
        print(f"  {code['code']}: {code['description']} ({code['confidence']})")
    print(f"Follow-up Actions: {len(result['follow_up_actions'])}")
    for action in result["follow_up_actions"]:
        print(f"  - {action}")
