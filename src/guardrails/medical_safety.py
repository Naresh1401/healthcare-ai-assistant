"""
Medical Safety Guardrails.
PII/PHI detection and redaction, medical misinformation detection,
scope limitation, and response validation against medical ontology terms.
"""

import re
from typing import Optional


# Common medical ontology terms for validation
VALID_MEDICAL_TERMS = {
    "conditions": [
        "hypertension", "diabetes", "mellitus", "myocardial", "infarction",
        "heart failure", "pneumonia", "COPD", "asthma", "stroke",
        "arrhythmia", "anemia", "hypothyroidism", "hyperthyroidism",
        "chronic kidney disease", "hepatitis", "cirrhosis", "epilepsy",
        "migraine", "osteoarthritis", "rheumatoid arthritis", "lupus",
        "pulmonary embolism", "deep vein thrombosis", "sepsis",
        "meningitis", "pancreatitis", "appendicitis",
    ],
    "medications": [
        "metformin", "lisinopril", "amlodipine", "metoprolol", "omeprazole",
        "atorvastatin", "losartan", "warfarin", "aspirin", "clopidogrel",
        "insulin", "levothyroxine", "furosemide", "spironolactone",
        "amiodarone", "digoxin", "heparin", "enoxaparin", "prednisone",
        "ibuprofen", "acetaminophen", "gabapentin", "sertraline",
        "fluoxetine", "sumatriptan", "topiramate", "empagliflozin",
        "semaglutide", "dapagliflozin", "sitagliptin", "rosuvastatin",
    ],
    "procedures": [
        "ECG", "echocardiogram", "MRI", "CT scan", "X-ray", "ultrasound",
        "biopsy", "endoscopy", "colonoscopy", "catheterization",
        "angiography", "lumbar puncture", "spirometry", "EEG",
    ],
}

# Phrases that indicate potential scope violations
SCOPE_VIOLATION_PATTERNS = [
    r"you (?:definitely |clearly )?have\b",
    r"your diagnosis is\b",
    r"you should (?:stop|discontinue|start) (?:taking |your )",
    r"you don'?t need (?:to see |a )(?:doctor|physician|specialist)",
    r"no need (?:to |for )(?:worry|concern|see a doctor)",
    r"i (?:can )?(?:diagnose|prescribe|recommend treatment)\b",
    r"this (?:is|confirms) (?:a |your )?(?:definitive )?diagnosis\b",
]

# Common medical misinformation patterns
MISINFORMATION_PATTERNS = [
    r"(?:vaccines? |vaccination )(?:cause|causes|causing) autism",
    r"(?:bleach|chlorine dioxide|MMS) (?:cures?|treats?|heals?)",
    r"homeopathy (?:cures?|treats?|heals?) cancer",
    r"essential oils? (?:cure|treat|heal) (?:cancer|diabetes|covid)",
    r"5G (?:causes?|spreads?) (?:covid|coronavirus|disease)",
    r"(?:ivermectin|hydroxychloroquine) (?:is )?(?:a )?(?:proven )?cure for covid",
]


class MedicalSafetyGuardrails:
    """Medical safety checks for PII/PHI redaction, scope limitation, and validation."""

    # PHI/PII regex patterns
    PHI_PATTERNS = {
        "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "MRN": re.compile(r"\b(?:MRN|Medical Record Number|Med Rec)[:\s#]*\d{4,10}\b", re.IGNORECASE),
        "DOB": re.compile(
            r"\b(?:DOB|Date of Birth|Birth Date)[:\s]*"
            r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{1,2},? \d{4})\b",
            re.IGNORECASE,
        ),
        "PHONE": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "PERSON_NAME": re.compile(
            r"\b(?:Patient|Pt|Name|Dr\.?|Mr\.?|Mrs\.?|Ms\.?)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)\b"
        ),
        "ADDRESS": re.compile(
            r"\b\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+"
            r"(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane|Ct|Court)"
            r"\.?\b",
            re.IGNORECASE,
        ),
        "DATE_SPECIFIC": re.compile(
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)"
            r"\s+\d{1,2},?\s+\d{4}\b",
            re.IGNORECASE,
        ),
    }

    # Redaction replacement map
    REDACTION_MAP = {
        "SSN": "[REDACTED-SSN]",
        "MRN": "[REDACTED-MRN]",
        "DOB": "[REDACTED-DOB]",
        "PHONE": "[REDACTED-PHONE]",
        "EMAIL": "[REDACTED-EMAIL]",
        "PERSON_NAME": "[REDACTED-NAME]",
        "ADDRESS": "[REDACTED-ADDRESS]",
        "DATE_SPECIFIC": "[REDACTED-DATE]",
    }

    def redact_phi(self, text: str) -> dict:
        """
        Detect and redact PHI/PII from text.

        Returns:
            dict with redacted_text and list of detections
        """
        redacted_text = text
        detections = []

        for phi_type, pattern in self.PHI_PATTERNS.items():
            matches = pattern.findall(redacted_text)
            for match in matches:
                match_str = match if isinstance(match, str) else match[0] if match else ""
                if match_str:
                    detections.append({
                        "type": phi_type,
                        "found": True,
                        "count": len(matches),
                    })
            redacted_text = pattern.sub(self.REDACTION_MAP[phi_type], redacted_text)

        # Deduplicate detections
        seen = set()
        unique_detections = []
        for d in detections:
            key = d["type"]
            if key not in seen:
                seen.add(key)
                unique_detections.append(d)

        return {
            "redacted_text": redacted_text,
            "detections": unique_detections,
            "phi_detected": len(unique_detections) > 0,
        }

    def check_scope_violations(self, response: str) -> dict:
        """
        Check if a response exceeds appropriate clinical scope.

        Returns:
            dict with violation status and details
        """
        violations = []
        for pattern in SCOPE_VIOLATION_PATTERNS:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                violations.append({
                    "pattern": pattern,
                    "matches": matches,
                    "severity": "HIGH",
                })

        return {
            "has_violations": len(violations) > 0,
            "violations": violations,
            "recommendation": (
                "Response contains language that may exceed clinical scope. "
                "Ensure all responses include appropriate disclaimers and "
                "recommendations for professional consultation."
                if violations
                else "No scope violations detected."
            ),
        }

    def check_misinformation(self, text: str) -> dict:
        """
        Screen for known medical misinformation patterns.

        Returns:
            dict with misinformation detection results
        """
        flags = []
        for pattern in MISINFORMATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                flags.append({
                    "pattern": pattern,
                    "matches": matches,
                    "severity": "CRITICAL",
                })

        return {
            "has_misinformation": len(flags) > 0,
            "flags": flags,
            "action": (
                "BLOCK — Response contains potential medical misinformation. "
                "Do not present this information to users."
                if flags
                else "No misinformation patterns detected."
            ),
        }

    def validate_medical_terms(self, text: str) -> dict:
        """
        Validate response contains recognized medical terminology.

        Returns:
            dict with validation results
        """
        found_terms = {"conditions": [], "medications": [], "procedures": []}
        text_lower = text.lower()

        for category, terms in VALID_MEDICAL_TERMS.items():
            for term in terms:
                if term.lower() in text_lower:
                    found_terms[category].append(term)

        total_terms = sum(len(v) for v in found_terms.values())

        return {
            "recognized_terms": found_terms,
            "total_recognized": total_terms,
            "validation_status": "VALID" if total_terms > 0 else "REVIEW_NEEDED",
            "note": (
                "Response references recognized medical terminology."
                if total_terms > 0
                else "No recognized medical terms found. Response may need review."
            ),
        }

    def run_all_checks(self, text: str, is_response: bool = True) -> dict:
        """
        Run all safety checks on a piece of text.

        Args:
            text: Text to check
            is_response: True if checking an LLM response, False if checking input

        Returns:
            Comprehensive safety check results
        """
        results = {
            "phi_check": self.redact_phi(text),
            "safe_to_display": True,
            "warnings": [],
        }

        if is_response:
            results["scope_check"] = self.check_scope_violations(text)
            results["misinformation_check"] = self.check_misinformation(text)
            results["terminology_check"] = self.validate_medical_terms(text)

            if results["misinformation_check"]["has_misinformation"]:
                results["safe_to_display"] = False
                results["warnings"].append("Potential medical misinformation detected")

            if results["scope_check"]["has_violations"]:
                results["warnings"].append("Response may exceed clinical scope")

        if results["phi_check"]["phi_detected"]:
            results["warnings"].append("PHI/PII detected and redacted")

        return results


if __name__ == "__main__":
    guardrails = MedicalSafetyGuardrails()

    # Test PHI redaction
    test_text = (
        "Patient: John Smith, DOB: 03/15/1965, SSN: 123-45-6789, "
        "MRN: 00123456. Lives at 123 Oak Street. Contact: john@email.com"
    )
    print("=== PHI Redaction Test ===")
    result = guardrails.redact_phi(test_text)
    print(f"Original: {test_text}")
    print(f"Redacted: {result['redacted_text']}")
    print(f"Detections: {result['detections']}")

    # Test scope validation
    print("\n=== Scope Check Test ===")
    bad_response = "Based on these symptoms, you definitely have diabetes."
    scope_result = guardrails.check_scope_violations(bad_response)
    print(f"Text: {bad_response}")
    print(f"Violations: {scope_result['has_violations']}")

    # Test misinformation detection
    print("\n=== Misinformation Check ===")
    misinfo = "Some people believe vaccines cause autism."
    misinfo_result = guardrails.check_misinformation(misinfo)
    print(f"Text: {misinfo}")
    print(f"Flagged: {misinfo_result['has_misinformation']}")
