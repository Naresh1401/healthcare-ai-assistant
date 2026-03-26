"""
Streamlit Dashboard for the Clinical Decision Support System.
Provides interactive interfaces for clinical Q&A, drug interactions,
patient summaries, and clinical note structuring.
"""

import streamlit as st
import requests
import json

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Clinical Decision Support System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar ---
st.sidebar.title("🏥 Clinical Decision Support")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Clinical Knowledge Q&A",
        "Drug Interaction Checker",
        "Patient Summary Generator",
        "Clinical Note Structurer",
    ],
)

st.sidebar.markdown("---")
st.sidebar.warning(
    "⚠️ **Disclaimer**: This tool is for educational and demonstration "
    "purposes only. It does NOT provide real medical advice. Always consult "
    "qualified healthcare professionals."
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Author:** Naresh Sampangi")


def api_request(endpoint: str, payload: dict) -> dict | None:
    """Make a POST request to the API backend."""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API server. Make sure it's running on port 8000.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None


# =============================================================================
# Page: Clinical Knowledge Q&A
# =============================================================================
if page == "Clinical Knowledge Q&A":
    st.title("🔍 Clinical Knowledge Q&A")
    st.markdown(
        "Ask clinical questions and receive evidence-based answers with source "
        "citations and confidence scoring from the medical knowledge base."
    )

    # Sample questions
    with st.expander("📋 Sample Questions"):
        st.markdown("""
        - What is the first-line treatment for type 2 diabetes?
        - What are the drug interactions with warfarin?
        - How is hypertension classified by blood pressure levels?
        - What is the MONA protocol for acute coronary syndrome?
        - What are the symptoms of bacterial meningitis?
        """)

    question = st.text_area("Enter your clinical question:", height=100, placeholder="e.g., What is the recommended treatment for Stage 2 hypertension?")

    if st.button("🔎 Search Knowledge Base", type="primary"):
        if question.strip():
            with st.spinner("Querying medical knowledge base..."):
                result = api_request("/query", {"question": question})

            if result:
                # Confidence badge
                confidence = result.get("confidence", "unknown")
                confidence_colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}
                badge = confidence_colors.get(confidence, "⚪")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader("Answer")
                with col2:
                    st.metric("Confidence", f"{badge} {confidence.upper()}")
                    st.metric("Sources", result.get("num_sources", 0))

                st.markdown(result.get("answer", "No answer returned."))

                # Source documents
                st.subheader("📚 Source Documents")
                sources = result.get("sources", [])
                for i, source in enumerate(sources, 1):
                    with st.expander(f"Source {i}: {source.get('source', 'Unknown')} — Relevance: {source.get('relevance_score', 'N/A')}"):
                        st.markdown(f"**Category:** {source.get('category', 'N/A')}")
                        st.markdown(f"**Relevance Score:** {source.get('relevance_score', 'N/A')}")
                        st.text(source.get("excerpt", "No excerpt available."))
        else:
            st.warning("Please enter a question.")


# =============================================================================
# Page: Drug Interaction Checker
# =============================================================================
elif page == "Drug Interaction Checker":
    st.title("💊 Drug Interaction Checker")
    st.markdown(
        "Enter a list of medications to check for potential drug-drug interactions. "
        "The system analyzes interactions using the medical knowledge base."
    )

    with st.expander("📋 Sample Medication Lists"):
        st.markdown("""
        - warfarin, aspirin, omeprazole
        - lisinopril, spironolactone, ibuprofen
        - metformin, amlodipine, simvastatin
        - amiodarone, digoxin, metoprolol
        """)

    medications_input = st.text_input(
        "Enter medications (comma-separated):",
        placeholder="e.g., warfarin, aspirin, omeprazole, lisinopril",
    )

    if st.button("🔍 Check Interactions", type="primary"):
        medications = [m.strip() for m in medications_input.split(",") if m.strip()]

        if len(medications) < 2:
            st.warning("Please enter at least 2 medications separated by commas.")
        else:
            with st.spinner("Analyzing drug interactions..."):
                result = api_request("/drug-interactions", {"medications": medications})

            if result:
                st.subheader("Results")

                col1, col2, col3 = st.columns(3)
                col1.metric("Medications Checked", len(result.get("medications_checked", [])))
                col2.metric("Interactions Found", result.get("total_interactions", 0))

                # Count by severity
                interactions = result.get("interactions_found", [])
                major = sum(1 for i in interactions if i.get("severity") == "MAJOR")
                col3.metric("Major Interactions", major)

                # Risk summary
                st.info(f"**Risk Summary:** {result.get('risk_summary', 'N/A')}")

                # Interactions detail
                if interactions:
                    st.subheader("Interaction Details")
                    for interaction in interactions:
                        severity = interaction.get("severity", "UNKNOWN")
                        severity_icon = {"MAJOR": "🔴", "MODERATE": "🟡", "MINOR": "🟢"}.get(severity, "⚪")

                        with st.expander(f"{severity_icon} {interaction.get('drug_pair', 'Unknown')} [{severity}]"):
                            st.markdown(f"**Mechanism:** {interaction.get('mechanism', 'N/A')}")
                            st.markdown(f"**Clinical Significance:** {interaction.get('clinical_significance', 'N/A')}")
                            st.markdown(f"**Management:** {interaction.get('management', 'N/A')}")
                else:
                    st.success("No interactions found in the knowledge base. Always verify with a pharmacist.")

                # Recommendations
                recommendations = result.get("recommendations", [])
                if recommendations:
                    st.subheader("Recommendations")
                    for rec in recommendations:
                        st.markdown(f"- {rec}")


# =============================================================================
# Page: Patient Summary Generator
# =============================================================================
elif page == "Patient Summary Generator":
    st.title("📋 Patient Summary Generator")
    st.markdown(
        "Paste raw clinical notes to generate a structured patient summary "
        "with ICD-10 code suggestions and follow-up action items."
    )

    with st.expander("📋 Sample Clinical Notes"):
        st.code("""Patient is a 58-year-old male presenting with complaints of increased thirst
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
- Follow-up in 4 weeks with repeat HbA1c in 3 months

Allergies: Sulfa drugs (rash), Penicillin (anaphylaxis)""", language="text")

    clinical_notes = st.text_area(
        "Paste clinical notes here:",
        height=250,
        placeholder="Enter raw clinical notes...",
    )

    redact_phi = st.checkbox("Redact PHI/PII before processing", value=True)

    if st.button("📄 Generate Summary", type="primary"):
        if clinical_notes.strip():
            with st.spinner("Generating patient summary..."):
                result = api_request("/summarize-notes", {
                    "clinical_notes": clinical_notes,
                    "redact_phi": redact_phi,
                })

            if result:
                st.subheader("Structured Patient Summary")

                # Demographics
                demo = result.get("demographics", {})
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**Age:** {demo.get('age', 'N/A')}")
                col2.markdown(f"**Sex:** {demo.get('sex', 'N/A')}")
                col3.markdown(f"**PHI Redactions:** {result.get('phi_redactions_applied', 0)}")

                st.markdown(f"**Chief Complaint:** {result.get('chief_complaint', 'N/A')}")
                st.markdown(f"**HPI:** {result.get('history_of_present_illness', 'N/A')}")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Past Medical History:**")
                    for item in result.get("past_medical_history", []):
                        st.markdown(f"- {item}")
                    st.markdown("**Allergies:**")
                    for item in result.get("allergies", []):
                        st.markdown(f"- {item}")
                with col2:
                    st.markdown("**Current Medications:**")
                    for item in result.get("current_medications", []):
                        st.markdown(f"- {item}")

                st.markdown(f"**Assessment:** {result.get('assessment', 'N/A')}")

                st.markdown("**Plan:**")
                for item in result.get("plan", []):
                    st.markdown(f"- {item}")

                # ICD-10 suggestions
                icd_codes = result.get("icd10_suggestions", [])
                if icd_codes:
                    st.subheader("ICD-10 Code Suggestions")
                    for code in icd_codes:
                        confidence_icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(code.get("confidence", ""), "⚪")
                        st.markdown(f"{confidence_icon} **{code.get('code', '')}** — {code.get('description', '')} ({code.get('confidence', '')})")

                # Follow-up actions
                follow_ups = result.get("follow_up_actions", [])
                if follow_ups:
                    st.subheader("Follow-up Actions")
                    for action in follow_ups:
                        st.markdown(f"☐ {action}")

                # Critical alerts
                alerts = result.get("critical_alerts", [])
                if alerts:
                    st.subheader("⚠️ Critical Alerts")
                    for alert in alerts:
                        st.error(alert)
        else:
            st.warning("Please enter clinical notes.")


# =============================================================================
# Page: Clinical Note Structurer
# =============================================================================
elif page == "Clinical Note Structurer":
    st.title("📝 Clinical Note Structurer (SOAP Format)")
    st.markdown(
        "Convert unstructured clinical notes into standardized SOAP format "
        "(Subjective, Objective, Assessment, Plan)."
    )

    with st.expander("📋 Sample Unstructured Note"):
        st.code("""Pt is a 45 yo female c/o worsening headaches x 2 weeks. Describes bifrontal
throbbing pain, 7/10 severity, worse in the morning, associated with nausea
but no vomiting. No visual changes, no fever, no neck stiffness. Has tried
OTC ibuprofen 400mg with minimal relief. PMH significant for HTN (on
losartan 50mg daily), migraine history since age 20.

VS: BP 148/92, HR 78, T 98.6F, RR 16, SpO2 99% RA
PE: Alert, oriented x3. HEENT: PERRL, no papilledema. Neck supple.
Neuro: CN II-XII intact, no focal deficits.

A: Chronic migraine with increasing frequency. HTN suboptimally controlled.
P: Start sumatriptan 50mg PRN, topiramate 25mg daily for prophylaxis.
Increase losartan to 100mg. MRI brain w/o contrast. F/u in 4 weeks.""", language="text")

    clinical_notes = st.text_area(
        "Paste unstructured clinical notes here:",
        height=250,
        placeholder="Enter clinical notes to convert to SOAP format...",
        key="soap_notes",
    )

    redact_phi_soap = st.checkbox("Redact PHI/PII before processing", value=True, key="soap_redact")

    if st.button("📝 Convert to SOAP", type="primary"):
        if clinical_notes.strip():
            with st.spinner("Structuring clinical note into SOAP format..."):
                result = api_request("/structure-notes", {
                    "clinical_notes": clinical_notes,
                    "redact_phi": redact_phi_soap,
                })

            if result:
                # Metadata
                metadata = result.get("metadata", {})
                col1, col2, col3 = st.columns(3)
                col1.metric("Visit Type", metadata.get("visit_type", "N/A"))
                col2.metric("Complexity", metadata.get("complexity", "N/A"))
                col3.metric("Completeness", metadata.get("completeness_score", "N/A"))

                # SOAP sections
                st.subheader("S — Subjective")
                subj = result.get("subjective", {})
                st.markdown(f"**Chief Complaint:** {subj.get('chief_complaint', 'N/A')}")
                st.markdown(f"**HPI:** {subj.get('history_of_present_illness', 'N/A')}")
                if subj.get("review_of_systems"):
                    st.markdown("**Review of Systems:**")
                    for ros in subj["review_of_systems"]:
                        st.markdown(f"- {ros}")
                st.markdown(f"**Social History:** {subj.get('social_history', 'N/A')}")
                st.markdown(f"**Family History:** {subj.get('family_history', 'N/A')}")

                st.subheader("O — Objective")
                obj = result.get("objective", {})
                st.markdown(f"**Vital Signs:** {obj.get('vital_signs', 'N/A')}")
                if obj.get("physical_exam"):
                    st.markdown("**Physical Exam:**")
                    for finding in obj["physical_exam"]:
                        st.markdown(f"- {finding}")
                if obj.get("lab_results"):
                    st.markdown("**Lab Results:**")
                    for lab in obj["lab_results"]:
                        st.markdown(f"- {lab}")

                st.subheader("A — Assessment")
                assess = result.get("assessment", {})
                st.markdown(f"**Primary Diagnosis:** {assess.get('primary_diagnosis', 'N/A')}")
                if assess.get("differential_diagnoses"):
                    st.markdown("**Differentials:**")
                    for dx in assess["differential_diagnoses"]:
                        st.markdown(f"- {dx}")
                st.markdown(f"**Clinical Reasoning:** {assess.get('clinical_reasoning', 'N/A')}")

                st.subheader("P — Plan")
                plan = result.get("plan", {})
                if plan.get("medications"):
                    st.markdown("**Medications:**")
                    for med in plan["medications"]:
                        st.markdown(f"- {med}")
                if plan.get("diagnostic_workup"):
                    st.markdown("**Diagnostic Workup:**")
                    for dx in plan["diagnostic_workup"]:
                        st.markdown(f"- {dx}")
                if plan.get("referrals"):
                    st.markdown("**Referrals:**")
                    for ref in plan["referrals"]:
                        st.markdown(f"- {ref}")
                if plan.get("patient_education"):
                    st.markdown("**Patient Education:**")
                    for edu in plan["patient_education"]:
                        st.markdown(f"- {edu}")
                st.markdown(f"**Follow-up:** {plan.get('follow_up', 'N/A')}")

                # Missing elements
                missing = metadata.get("missing_elements", [])
                if missing:
                    st.subheader("⚠️ Missing Documentation Elements")
                    for element in missing:
                        st.warning(f"Missing: {element}")
        else:
            st.warning("Please enter clinical notes.")
