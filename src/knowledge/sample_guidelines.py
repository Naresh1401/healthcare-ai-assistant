"""
Generate synthetic medical guideline text files for RAG ingestion.
Creates sample clinical guidelines for diabetes, hypertension, and cardiac care.
"""

import os

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge")

DIABETES_GUIDELINES = """CLINICAL GUIDELINE: Type 2 Diabetes Management
Source: Synthetic Clinical Guidelines Database v2.0
Category: Endocrinology / Metabolic Disorders

1. DIAGNOSIS CRITERIA
- Fasting plasma glucose (FPG) >= 126 mg/dL on two separate occasions
- HbA1c >= 6.5% confirmed on repeat testing
- 2-hour plasma glucose >= 200 mg/dL during oral glucose tolerance test (OGTT)
- Random plasma glucose >= 200 mg/dL with classic hyperglycemic symptoms

2. FIRST-LINE TREATMENT
- Metformin 500mg twice daily, titrate to 1000mg twice daily over 4 weeks
- Lifestyle modifications: dietary counseling, 150 min/week moderate exercise
- Target HbA1c < 7.0% for most adults; individualize for elderly (< 8.0%)
- Monitor renal function (eGFR) before initiation; contraindicated if eGFR < 30

3. SECOND-LINE AGENTS (if HbA1c not at goal after 3 months)
- SGLT2 inhibitors (empagliflozin, dapagliflozin): preferred if cardiovascular or renal comorbidity
- GLP-1 receptor agonists (semaglutide, liraglutide): preferred if obesity or cardiovascular risk
- DPP-4 inhibitors (sitagliptin, linagliptin): consider if cost is a concern
- Sulfonylureas (glimepiride, glipizide): effective but risk of hypoglycemia and weight gain

4. INSULIN THERAPY
- Consider if HbA1c > 10% or symptomatic hyperglycemia at diagnosis
- Basal insulin (glargine, detemir): start 10 units or 0.2 units/kg at bedtime
- Titrate by 2 units every 3 days to achieve fasting glucose 80-130 mg/dL
- Add prandial insulin if postprandial glucose > 180 mg/dL despite basal optimization

5. MONITORING
- HbA1c every 3 months until stable, then every 6 months
- Annual eye exam, foot exam, renal function panel
- Lipid profile annually; target LDL < 100 mg/dL (< 70 if high CV risk)
- Blood pressure target < 130/80 mmHg

6. DRUG INTERACTIONS - DIABETES MEDICATIONS
- Metformin + contrast dye: hold metformin 48 hours before/after iodinated contrast
- Sulfonylureas + fluconazole: increased hypoglycemia risk (CYP2C9 inhibition)
- SGLT2 inhibitors + loop diuretics: risk of volume depletion and hypotension
- GLP-1 agonists + warfarin: may alter warfarin absorption; monitor INR closely

7. COMPLICATIONS SCREENING
- Diabetic nephropathy: annual urine albumin-to-creatinine ratio
- Diabetic neuropathy: annual monofilament testing
- Cardiovascular risk: calculate 10-year ASCVD risk score
- Mental health: screen for diabetes distress and depression annually
"""

HYPERTENSION_GUIDELINES = """CLINICAL GUIDELINE: Hypertension Management
Source: Synthetic Clinical Guidelines Database v2.0
Category: Cardiovascular / Internal Medicine

1. CLASSIFICATION
- Normal: systolic < 120 AND diastolic < 80 mmHg
- Elevated: systolic 120-129 AND diastolic < 80 mmHg
- Stage 1 HTN: systolic 130-139 OR diastolic 80-89 mmHg
- Stage 2 HTN: systolic >= 140 OR diastolic >= 90 mmHg
- Hypertensive crisis: systolic > 180 AND/OR diastolic > 120 mmHg

2. INITIAL EVALUATION
- Confirm with ambulatory or home BP monitoring (2 readings on 2 separate occasions)
- Assess for secondary causes: renal artery stenosis, pheochromocytoma, Cushing syndrome
- Basic labs: BMP, CBC, lipid panel, TSH, urinalysis, ECG
- Calculate 10-year ASCVD risk for treatment threshold decisions

3. NON-PHARMACOLOGICAL INTERVENTIONS
- DASH diet: rich in fruits, vegetables, whole grains; limit sodium to < 2300 mg/day
- Regular aerobic exercise: 90-150 min/week moderate intensity
- Weight management: target BMI 18.5-24.9
- Limit alcohol: <= 2 drinks/day men, <= 1 drink/day women
- Stress management and adequate sleep (7-9 hours)

4. FIRST-LINE PHARMACOTHERAPY
- ACE inhibitors (lisinopril 10mg daily, enalapril 5mg BID): preferred for diabetes, CKD, HF
- ARBs (losartan 50mg daily, valsartan 80mg daily): alternative if ACE intolerant (cough)
- Calcium channel blockers (amlodipine 5mg daily): preferred for elderly, Black patients
- Thiazide diuretics (hydrochlorothiazide 25mg daily, chlorthalidone 12.5mg daily)

5. COMBINATION THERAPY
- ACE/ARB + CCB: effective combination, well-tolerated
- ACE/ARB + thiazide: synergistic, monitor potassium
- DO NOT combine ACE + ARB: increased adverse events without benefit
- Triple therapy if needed: ACE/ARB + CCB + thiazide

6. DRUG INTERACTIONS - ANTIHYPERTENSIVES
- ACE inhibitors + potassium-sparing diuretics: hyperkalemia risk
- ACE inhibitors + NSAIDs: reduced antihypertensive effect, nephrotoxicity
- ACE inhibitors + lithium: increased lithium levels, toxicity risk
- Beta-blockers + verapamil/diltiazem: severe bradycardia, heart block
- Thiazides + digoxin: hypokalemia increases digoxin toxicity risk
- Amlodipine + simvastatin > 20mg: increased statin myopathy risk

7. SPECIAL POPULATIONS
- Pregnancy: labetalol, nifedipine, methyldopa; AVOID ACE/ARBs (teratogenic)
- CKD: ACE/ARB preferred; monitor creatinine and potassium
- Heart failure: ACE/ARB + beta-blocker + diuretic
- Elderly (>65): start low, go slow; target < 130/80 if tolerated

8. MONITORING
- Follow-up in 4 weeks after initiation or dose change
- Home BP monitoring encouraged (morning and evening readings)
- Annual labs: BMP, lipid panel; more frequent if on diuretics/ACE/ARBs
- Reassess cardiovascular risk annually
"""

CARDIAC_CARE_GUIDELINES = """CLINICAL GUIDELINE: Acute Coronary Syndrome & Cardiac Care
Source: Synthetic Clinical Guidelines Database v2.0
Category: Cardiology / Emergency Medicine

1. ACUTE CORONARY SYNDROME (ACS) CLASSIFICATION
- STEMI: ST elevation >= 1mm in 2 contiguous leads; emergent PCI within 90 minutes
- NSTEMI: troponin elevation without ST elevation; risk stratify with TIMI/GRACE score
- Unstable Angina: clinical presentation without troponin elevation

2. INITIAL MANAGEMENT (MONA Protocol)
- Morphine 2-4mg IV for pain unresponsive to nitroglycerin (use with caution)
- Oxygen: only if SpO2 < 94% (routine supplementation not recommended)
- Nitroglycerin 0.4mg SL every 5 min x 3; AVOID if systolic BP < 90 or recent PDE5 inhibitor
- Aspirin 325mg chewed immediately (non-enteric coated)

3. ANTIPLATELET & ANTICOAGULATION
- Dual antiplatelet therapy (DAPT): aspirin + P2Y12 inhibitor
- Ticagrelor 180mg loading, then 90mg BID (preferred for most ACS)
- Clopidogrel 600mg loading, then 75mg daily (if ticagrelor contraindicated)
- Heparin: UFH 60 units/kg bolus (max 4000 units), then 12 units/kg/hr

4. SECONDARY PREVENTION
- High-intensity statin: atorvastatin 80mg or rosuvastatin 20mg daily
- Beta-blocker: metoprolol succinate 25-200mg daily (start within 24 hours if stable)
- ACE inhibitor: start within 24 hours if anterior MI, HF, or EF < 40%
- Cardiac rehabilitation referral
- Smoking cessation counseling

5. HEART FAILURE MANAGEMENT
- HFrEF (EF <= 40%): quadruple therapy
  a. ACE/ARB/ARNI (sacubitril-valsartan preferred)
  b. Beta-blocker (carvedilol, metoprolol succinate, bisoprolol)
  c. Mineralocorticoid antagonist (spironolactone 25mg daily)
  d. SGLT2 inhibitor (dapagliflozin or empagliflozin)
- Diuretics for volume management (furosemide, bumetanide)
- Digoxin if symptoms persist despite optimal therapy

6. DRUG INTERACTIONS - CARDIAC MEDICATIONS
- Warfarin + amiodarone: increased INR, reduce warfarin dose by 30-50%
- Digoxin + amiodarone: increased digoxin levels, reduce dose by 50%
- Statins + macrolide antibiotics (clarithromycin): increased myopathy/rhabdomyolysis risk
- Clopidogrel + omeprazole: reduced clopidogrel efficacy (CYP2C19 inhibition)
- Beta-blockers + clonidine: rebound hypertension if clonidine withdrawn
- Spironolactone + ACE inhibitors: hyperkalemia risk, monitor potassium closely
- Nitroglycerin + sildenafil/tadalafil: severe hypotension, CONTRAINDICATED

7. MONITORING
- Troponin: serial measurements at 0, 3, and 6 hours post-presentation
- ECG: repeat at 15-30 min intervals during acute phase
- Echocardiogram within 24-48 hours of admission
- BNP/NT-proBNP for heart failure assessment
- INR monitoring if on warfarin (target 2.0-3.0)

8. DISCHARGE PLANNING
- Medication reconciliation and patient education
- Follow-up cardiology appointment within 1-2 weeks
- Cardiac rehabilitation enrollment
- Lifestyle modification counseling (diet, exercise, smoking, stress)
- Emergency action plan for recurrent symptoms
"""

DRUG_INTERACTIONS_DB = """DRUG INTERACTION DATABASE
Source: Synthetic Drug Interaction Reference v2.0

INTERACTION: Warfarin + Aspirin
Severity: MAJOR
Mechanism: Additive anticoagulant and antiplatelet effects
Clinical Significance: Significantly increased risk of bleeding, including GI hemorrhage and intracranial bleeding. Monitor INR closely. Use combination only when benefit clearly outweighs risk (e.g., mechanical heart valve with recent ACS).
Management: Consider PPI prophylaxis. Monitor for signs of bleeding. Maintain INR at lower end of therapeutic range.

INTERACTION: Metformin + Iodinated Contrast Dye
Severity: MAJOR
Mechanism: Risk of contrast-induced nephropathy leading to metformin accumulation and lactic acidosis
Clinical Significance: Lactic acidosis can be fatal. Hold metformin for 48 hours before and after contrast administration.
Management: Check renal function (eGFR) before and 48 hours after contrast. Resume metformin only if renal function is stable.

INTERACTION: Lisinopril + Spironolactone
Severity: MAJOR
Mechanism: Both agents decrease potassium excretion leading to hyperkalemia
Clinical Significance: Life-threatening hyperkalemia possible, especially in renal impairment. Risk further increased with concurrent NSAID use.
Management: Monitor potassium within 1 week of initiation and periodically. Avoid if eGFR < 30. Dietary potassium counseling.

INTERACTION: Simvastatin + Amlodipine
Severity: MODERATE
Mechanism: Amlodipine inhibits CYP3A4, increasing simvastatin plasma levels
Clinical Significance: Increased risk of statin-related myopathy and rhabdomyolysis.
Management: Limit simvastatin to 20mg daily when combined with amlodipine. Consider switching to rosuvastatin or pravastatin.

INTERACTION: Clopidogrel + Omeprazole
Severity: MODERATE
Mechanism: Omeprazole inhibits CYP2C19, reducing conversion of clopidogrel to active metabolite
Clinical Significance: Reduced antiplatelet effect, potentially increasing risk of cardiovascular events.
Management: Use pantoprazole instead (minimal CYP2C19 interaction). Avoid omeprazole and esomeprazole.

INTERACTION: Metoprolol + Fluoxetine
Severity: MODERATE
Mechanism: Fluoxetine inhibits CYP2D6, increasing metoprolol plasma levels
Clinical Significance: Enhanced beta-blockade leading to bradycardia, hypotension, and fatigue.
Management: Monitor heart rate and blood pressure. Consider dose reduction of metoprolol or switch to atenolol (not CYP2D6 metabolized).

INTERACTION: Amiodarone + Digoxin
Severity: MAJOR
Mechanism: Amiodarone inhibits P-glycoprotein and renal clearance of digoxin
Clinical Significance: Digoxin levels can increase by 70-100%, leading to toxicity (nausea, visual disturbances, arrhythmias).
Management: Reduce digoxin dose by 50% when starting amiodarone. Monitor digoxin levels weekly for 4-6 weeks.

INTERACTION: Ciprofloxacin + Theophylline
Severity: MAJOR
Mechanism: Ciprofloxacin inhibits CYP1A2, decreasing theophylline metabolism
Clinical Significance: Theophylline toxicity (seizures, arrhythmias, nausea) can occur within 1-2 days.
Management: Reduce theophylline dose by 30-50%. Monitor theophylline levels. Consider alternative antibiotic.

INTERACTION: SSRIs + Tramadol
Severity: MAJOR
Mechanism: Both agents increase serotonin levels; additive serotonergic effect
Clinical Significance: Risk of serotonin syndrome (agitation, hyperthermia, clonus, diaphoresis). Can be life-threatening.
Management: Avoid combination if possible. If necessary, use lowest effective doses and monitor for serotonin syndrome symptoms.

INTERACTION: ACE Inhibitors + NSAIDs
Severity: MODERATE
Mechanism: NSAIDs reduce prostaglandin-mediated renal blood flow, counteracting ACE inhibitor effects
Clinical Significance: Reduced antihypertensive efficacy. Increased risk of acute kidney injury, especially with dehydration.
Management: Use lowest NSAID dose for shortest duration. Monitor blood pressure and renal function. Consider acetaminophen as alternative analgesic.
"""

SYMPTOM_DISEASE_MAPPINGS = """SYMPTOM-DISEASE MAPPING REFERENCE
Source: Synthetic Clinical Decision Support v2.0

SYMPTOM CLUSTER: Chest Pain + Diaphoresis + Dyspnea
Primary Differentials:
1. Acute Myocardial Infarction (STEMI/NSTEMI) - Likelihood: HIGH
   Key Features: substernal pressure, radiation to jaw/left arm, onset with exertion
   Urgent Workup: ECG within 10 min, troponin, CBC, BMP, coagulation studies
2. Pulmonary Embolism - Likelihood: MODERATE
   Key Features: pleuritic chest pain, tachycardia, recent immobilization, unilateral leg swelling
   Workup: D-dimer, CT pulmonary angiography, Wells score
3. Aortic Dissection - Likelihood: LOW-MODERATE
   Key Features: tearing/ripping chest pain radiating to back, BP differential between arms
   Workup: CT angiography of chest/abdomen/pelvis, emergent surgical consult

SYMPTOM CLUSTER: Polyuria + Polydipsia + Weight Loss
Primary Differentials:
1. Type 1 Diabetes Mellitus - Likelihood: HIGH (younger patients)
   Key Features: acute onset, ketosis, autoimmune markers
   Workup: fasting glucose, HbA1c, C-peptide, GAD antibodies, urinalysis for ketones
2. Type 2 Diabetes Mellitus - Likelihood: HIGH (older/obese patients)
   Key Features: gradual onset, family history, metabolic syndrome features
   Workup: fasting glucose, HbA1c, lipid panel, renal function
3. Diabetes Insipidus - Likelihood: LOW
   Key Features: large volumes of dilute urine, normal or high glucose
   Workup: serum and urine osmolality, water deprivation test

SYMPTOM CLUSTER: Headache + Fever + Neck Stiffness
Primary Differentials:
1. Bacterial Meningitis - Likelihood: HIGH (medical emergency)
   Key Features: rapid onset, photophobia, altered mental status, petechial rash
   Workup: blood cultures, lumbar puncture (CSF analysis), empiric antibiotics BEFORE LP if delayed
2. Viral Meningitis - Likelihood: MODERATE
   Key Features: less severe, gradual onset, seasonal (enterovirus in summer/fall)
   Workup: CSF lymphocytic pleocytosis, viral PCR panel
3. Subarachnoid Hemorrhage - Likelihood: MODERATE
   Key Features: thunderclap headache, worst headache of life, sudden onset
   Workup: non-contrast CT head, LP for xanthochromia if CT negative

SYMPTOM CLUSTER: Fatigue + Weight Gain + Cold Intolerance
Primary Differentials:
1. Hypothyroidism - Likelihood: HIGH
   Key Features: constipation, dry skin, bradycardia, delayed reflexes
   Workup: TSH (elevated), free T4 (low), anti-TPO antibodies
2. Depression - Likelihood: MODERATE
   Key Features: anhedonia, sleep changes, concentration difficulties
   Workup: PHQ-9 screening, clinical interview, rule out organic causes
3. Iron Deficiency Anemia - Likelihood: MODERATE
   Key Features: pallor, dyspnea on exertion, pica, koilonychia
   Workup: CBC, iron studies (ferritin, TIBC, serum iron), reticulocyte count

SYMPTOM CLUSTER: Joint Pain + Morning Stiffness + Fatigue
Primary Differentials:
1. Rheumatoid Arthritis - Likelihood: HIGH
   Key Features: symmetric small joint involvement (MCP, PIP), stiffness > 30 min
   Workup: RF, anti-CCP, ESR, CRP, X-rays of hands/feet
2. Systemic Lupus Erythematosus - Likelihood: MODERATE
   Key Features: malar rash, photosensitivity, oral ulcers, multi-organ involvement
   Workup: ANA, anti-dsDNA, complement levels (C3/C4), CBC, urinalysis
3. Osteoarthritis - Likelihood: MODERATE
   Key Features: large joint involvement, weight-bearing joints, stiffness < 30 min
   Workup: X-rays (joint space narrowing, osteophytes), clinical diagnosis
"""


def generate_sample_files():
    """Generate all synthetic medical knowledge files."""
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

    files = {
        "diabetes_management_guidelines.txt": DIABETES_GUIDELINES,
        "hypertension_management_guidelines.txt": HYPERTENSION_GUIDELINES,
        "cardiac_care_guidelines.txt": CARDIAC_CARE_GUIDELINES,
        "drug_interactions_database.txt": DRUG_INTERACTIONS_DB,
        "symptom_disease_mappings.txt": SYMPTOM_DISEASE_MAPPINGS,
    }

    for filename, content in files.items():
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        with open(filepath, "w") as f:
            f.write(content.strip())
        print(f"Created: {filepath}")

    print(f"\nGenerated {len(files)} medical knowledge files in {KNOWLEDGE_DIR}")


if __name__ == "__main__":
    generate_sample_files()
