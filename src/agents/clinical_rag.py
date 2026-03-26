"""
Clinical RAG pipeline using LangChain.
Retrieves relevant medical context from ChromaDB, enforces medical disclaimers,
cites sources, and provides confidence scoring.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from src.knowledge.medical_data_loader import get_vector_store

load_dotenv()

CLINICAL_SYSTEM_PROMPT = """You are a clinical decision support assistant designed to help healthcare professionals access medical knowledge. You must follow these rules strictly:

RULES:
1. Always provide evidence-based responses grounded in the retrieved medical context.
2. Cite your sources explicitly by referencing the source document names.
3. Include appropriate medical disclaimers in every response.
4. Never provide a definitive diagnosis — always frame as differential considerations.
5. Recommend professional consultation for any clinical decision-making.
6. If the retrieved context does not contain sufficient information, clearly state the limitation.
7. Use precise medical terminology with explanations when appropriate.
8. Flag any information that may be time-sensitive or subject to guideline updates.

RESPONSE FORMAT:
- Begin with a concise answer to the query
- Provide supporting evidence from the knowledge base
- List source citations
- End with a standard medical disclaimer

DISCLAIMER (include at end of every response):
"⚠️ This information is for educational purposes only and does not constitute medical advice. Always consult qualified healthcare professionals for clinical decisions."

CONTEXT FROM MEDICAL KNOWLEDGE BASE:
{context}
"""

CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.5,
    "low": 0.0,
}


class ClinicalRAGPipeline:
    """RAG pipeline for clinical knowledge queries."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4")
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.1)
        self.vector_store = get_vector_store()
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CLINICAL_SYSTEM_PROMPT),
            ("human", "{question}"),
        ])
        self.chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    @staticmethod
    def _format_docs(docs) -> str:
        """Format retrieved documents with source attribution."""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            category = doc.metadata.get("category", "General")
            formatted.append(
                f"[Source {i}: {source} | Category: {category}]\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(formatted)

    def query(self, question: str) -> dict:
        """
        Query the clinical knowledge base.

        Returns:
            dict with keys: answer, sources, confidence, num_sources
        """
        # Retrieve documents with scores for confidence assessment
        docs_with_scores = self.vector_store.similarity_search_with_score(question, k=5)

        # Calculate confidence based on similarity scores
        confidence = self._calculate_confidence(docs_with_scores)

        # Extract source information
        sources = []
        for doc, score in docs_with_scores:
            sources.append({
                "source": doc.metadata.get("source", "Unknown"),
                "category": doc.metadata.get("category", "General"),
                "relevance_score": round(1 - score, 3),  # ChromaDB returns distance
                "excerpt": doc.page_content[:200] + "...",
            })

        # Generate answer
        answer = self.chain.invoke(question)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "num_sources": len(sources),
        }

    def _calculate_confidence(self, docs_with_scores: list) -> str:
        """Calculate confidence level based on retrieval similarity scores."""
        if not docs_with_scores:
            return "low"

        # ChromaDB returns L2 distance; lower is better
        avg_distance = sum(score for _, score in docs_with_scores) / len(docs_with_scores)
        best_distance = min(score for _, score in docs_with_scores)

        # Convert distance to similarity-like score (inverse)
        best_similarity = max(0, 1 - best_distance)

        if best_similarity >= CONFIDENCE_THRESHOLDS["high"]:
            return "high"
        elif best_similarity >= CONFIDENCE_THRESHOLDS["medium"]:
            return "medium"
        return "low"


def query_clinical_knowledge(question: str) -> dict:
    """Convenience function for querying clinical knowledge."""
    pipeline = ClinicalRAGPipeline()
    return pipeline.query(question)


if __name__ == "__main__":
    result = query_clinical_knowledge("What is the first-line treatment for type 2 diabetes?")
    print(f"Confidence: {result['confidence']}")
    print(f"Sources: {result['num_sources']}")
    print(f"\n{result['answer']}")
