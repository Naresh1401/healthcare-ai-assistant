"""
Drug Interaction Checker agent using LangChain.
Takes a list of medications, checks for interactions via RAG knowledge base,
and returns structured output with severity, mechanism, and clinical significance.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from src.knowledge.medical_data_loader import get_vector_store

load_dotenv()


class DrugInteraction(BaseModel):
    """Structured output for a single drug interaction."""
    drug_pair: str = Field(description="The two drugs involved, e.g. 'Warfarin + Aspirin'")
    severity: str = Field(description="Severity level: MAJOR, MODERATE, or MINOR")
    mechanism: str = Field(description="Pharmacological mechanism of the interaction")
    clinical_significance: str = Field(description="Clinical impact and risk description")
    management: str = Field(description="Recommended management strategy")


class DrugInteractionReport(BaseModel):
    """Complete drug interaction check report."""
    medications_checked: list[str] = Field(description="List of medications analyzed")
    interactions_found: list[DrugInteraction] = Field(description="List of identified interactions")
    total_interactions: int = Field(description="Total number of interactions found")
    risk_summary: str = Field(description="Overall risk summary for the medication combination")
    recommendations: list[str] = Field(description="General recommendations for the prescriber")


DRUG_INTERACTION_PROMPT = """You are a clinical pharmacology expert assistant specializing in drug interaction analysis. Your role is to identify potential drug-drug interactions from the provided medication list using the medical knowledge base.

RULES:
1. Only report interactions that are supported by the retrieved medical knowledge context.
2. Classify severity accurately as MAJOR, MODERATE, or MINOR.
3. Explain the pharmacological mechanism clearly.
4. Provide actionable management recommendations.
5. If no interactions are found in the knowledge base, state that clearly but recommend comprehensive pharmacy review.
6. Never claim completeness — always recommend professional pharmacist review.

MEDICAL KNOWLEDGE CONTEXT:
{context}

MEDICATIONS TO CHECK:
{medications}

{format_instructions}

⚠️ DISCLAIMER: This is an educational tool only. Always verify drug interactions with a licensed pharmacist and up-to-date clinical references (e.g., Lexicomp, Micromedex).
"""


class DrugInteractionChecker:
    """Agent that checks for drug interactions using RAG knowledge base."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4")
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.0)
        self.vector_store = get_vector_store()
        self.output_parser = PydanticOutputParser(pydantic_object=DrugInteractionReport)

        self.prompt = ChatPromptTemplate.from_template(DRUG_INTERACTION_PROMPT)

    def _retrieve_interaction_context(self, medications: list[str]) -> str:
        """Retrieve relevant drug interaction information from the knowledge base."""
        queries = []
        # Search for each pair combination
        for i, drug_a in enumerate(medications):
            for drug_b in medications[i + 1:]:
                queries.append(f"drug interaction {drug_a} {drug_b}")
            queries.append(f"{drug_a} interactions side effects contraindications")

        all_docs = []
        seen_content = set()
        for query in queries:
            docs = self.vector_store.similarity_search(query, k=3)
            for doc in docs:
                content_hash = hash(doc.page_content[:100])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)

        formatted = []
        for i, doc in enumerate(all_docs[:10], 1):  # Limit to top 10 unique chunks
            source = doc.metadata.get("source", "Unknown")
            formatted.append(f"[Source {i}: {source}]\n{doc.page_content}")

        return "\n\n---\n\n".join(formatted)

    def check_interactions(self, medications: list[str]) -> DrugInteractionReport:
        """
        Check for drug interactions among a list of medications.

        Args:
            medications: List of medication names

        Returns:
            DrugInteractionReport with structured interaction data
        """
        if len(medications) < 2:
            return DrugInteractionReport(
                medications_checked=medications,
                interactions_found=[],
                total_interactions=0,
                risk_summary="At least two medications are required to check for interactions.",
                recommendations=["Provide two or more medications for interaction analysis."],
            )

        # Retrieve relevant context
        context = self._retrieve_interaction_context(medications)

        # Build prompt
        formatted_meds = ", ".join(medications)
        chain = self.prompt | self.llm | self.output_parser

        result = chain.invoke({
            "context": context,
            "medications": formatted_meds,
            "format_instructions": self.output_parser.get_format_instructions(),
        })

        return result


def check_drug_interactions(medications: list[str]) -> dict:
    """Convenience function for checking drug interactions."""
    checker = DrugInteractionChecker()
    report = checker.check_interactions(medications)
    return report.model_dump()


if __name__ == "__main__":
    meds = ["warfarin", "aspirin", "omeprazole", "lisinopril"]
    result = check_drug_interactions(meds)
    print(f"Medications: {result['medications_checked']}")
    print(f"Interactions found: {result['total_interactions']}")
    print(f"Risk summary: {result['risk_summary']}")
    for interaction in result["interactions_found"]:
        print(f"\n  {interaction['drug_pair']} [{interaction['severity']}]")
        print(f"  Mechanism: {interaction['mechanism']}")
        print(f"  Management: {interaction['management']}")
