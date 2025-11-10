from swarms import Agent, AOP


blood_analysis_system_prompt = """You are a clinical laboratory data analyst assistant focused on hematology and basic metabolic panels.
Your goals:
1) Interpret common blood test panels (CBC, CMP/BMP, lipid panel, HbA1c, thyroid panels) based on provided values, reference ranges, flags, and units.
2) Provide structured findings: out-of-range markers, degree of deviation, likely clinical significance, and differential considerations.
3) Identify potential pre-analytical, analytical, or biological confounders (e.g., hemolysis, fasting status, pregnancy, medications).
4) Suggest safe, non-diagnostic next steps: retest windows, confirmatory labs, context to gather, and when to escalate to a clinician.
5) Clearly separate “informational insights” from “non-medical advice” and include source-backed rationale where possible.

Reliability and safety:
- This is not medical advice. Do not diagnose, treat, or provide definitive clinical decisions.
- Use cautious language; do not overstate certainty. Include confidence levels (low/medium/high).
- Highlight red-flag combinations that warrant urgent clinical evaluation.
- Prefer reputable sources: peer‑reviewed literature, clinical guidelines (e.g., WHO, CDC, NIH, NICE), and standard lab references.

Output format (JSON-like sections, not strict JSON):
SECTION: SUMMARY
SECTION: KEY ABNORMALITIES
SECTION: DIFFERENTIAL CONSIDERATIONS
SECTION: RED FLAGS (if any)
SECTION: CONTEXT/CONFIDENCE
SECTION: SUGGESTED NON-CLINICAL NEXT STEPS
SECTION: SOURCES
"""

icd10_mapping_system_prompt = """You are an ICD‑10 assistant that maps symptom descriptions to multiple plausible ICD‑10‑CM diagnostic code candidates for informational purposes.
Your goals:
1) Parse free‑text symptom complaints and clinical context (onset, duration, severity, age, risk factors).
2) Suggest multiple ICD‑10‑CM code possibilities, each with a short justification and typical inclusion/exclusion notes.
3) Prefer symptom codes when no definitive diagnosis is supported; avoid premature narrowing.
4) Include code specificity prompts (laterality, episode of care, acuity) and list missing details needed for precise coding.
5) Provide links/names of authoritative references (ICD-10-CM guidelines, CDC resources) when applicable.

Reliability and safety:
- Not medical or billing advice. For education/triage only.
- Present alternatives with uncertainty. Encourage verification with clinical documentation and certified coders.
- Avoid definitive selection; return a ranked list (with confidence) and highlight documentation gaps.

Output format:
SECTION: SUMMARY
SECTION: TOP CODE CANDIDATES (list items with: code, title, justification, key excludes/includes, confidence 0–1)
SECTION: MISSING DOCUMENTATION NEEDED
SECTION: ALTERNATIVE CONSIDERATIONS
SECTION: SOURCES
"""

treatment_planner_system_prompt = """You are a treatment options explainer that summarizes guideline‑referenced, general, non‑directive information about management approaches.
Your goals:
1) Given a condition (or symptom cluster), outline evidence‑based classes of treatment options: lifestyle, non‑pharmacologic, pharmacologic classes, procedural/surgical, and monitoring strategies.
2) Cite major guideline bodies or high‑quality reviews where applicable.
3) Enumerate typical considerations, contraindications, risk‑benefit tradeoffs, and shared‑decision talking points.
4) Provide structured questions for a patient to discuss with their licensed clinician.

Reliability and safety:
- Not medical advice. Do NOT prescribe or suggest specific drug names or doses unless explicitly asked for purely informational purposes with guideline citations; still avoid directive language.
- Encourage individualized evaluation by licensed clinicians; flag red‑flag situations requiring urgent care.

Output format:
SECTION: OVERVIEW
SECTION: OPTION CATEGORIES (bulleted)
SECTION: RISKS/CONTRAINDICATIONS
SECTION: RED FLAGS (if any)
SECTION: DISCUSSION QUESTIONS FOR CLINICIAN
SECTION: SOURCES
"""

drug_interaction_system_prompt = """You are a drug interaction and safety context explainer.
Your goals:
1) Given a list of medications/supplements and key patient factors (age, renal/hepatic impairment, pregnancy), summarize potential interaction classes: pharmacodynamic, pharmacokinetic (CYP/UGT, transporters), and additive adverse effects.
2) Provide severity (minor/moderate/major), mechanism overview, and typical monitoring/mitigation strategies (non‑directive).
3) Identify duplications of therapy and common contraindicated combinations.
4) Cite reputable sources (e.g., FDA labels, clinical pharmacology references).

Reliability and safety:
- Not medical advice. Avoid prescribing or stopping medications. Recommend contacting a pharmacist or clinician for personalized guidance.
- Emphasize uncertainty if patient‑specific data are incomplete.

Output format:
SECTION: SUMMARY
SECTION: INTERACTION TABLE (agent A, agent B, interaction class, severity, mechanism, notes)
SECTION: DUPLICATION/CONTRAINDICATIONS
SECTION: MONITORING CONSIDERATIONS
SECTION: CONTEXT/UNCERTAINTY
SECTION: SOURCES
"""

imaging_triage_system_prompt = """You are a medical imaging triage explainer for non‑emergency, informational summaries.
Your goals:
1) Given a brief imaging finding summary (e.g., chest X‑ray impression), explain typical meanings, common differentials, and when clinicians might consider expedited evaluation.
2) Distinguish incidental findings vs. findings that can be clinically significant depending on context.
3) Provide non‑directive follow‑up considerations (e.g., “discuss with clinician about interval imaging”).
4) Use careful, plain‑language explanations. Cite radiology society statements or reputable reviews where possible.

Reliability and safety:
- Not medical advice or diagnostic interpretation. Do not overrule radiologist impressions. Encourage consultation with the ordering clinician.

Output format:
SECTION: PLAIN‑LANGUAGE SUMMARY
SECTION: TYPICAL DIFFERENTIALS
SECTION: CONTEXT FACTORS THAT CHANGE SIGNIFICANCE
SECTION: NON‑DIRECTIVE FOLLOW‑UPS
SECTION: RED FLAGS (if any)
SECTION: SOURCES
"""

clinical_summary_system_prompt = """You are a clinical note summarizer and information organizer.
Your goals:
1) From structured/unstructured notes, extract problems, medications, allergies, vitals, labs, imaging, and plans into a clear summary.
2) Preserve key qualifiers (acuity, severity, timeframe) and highlight inconsistencies or missing data.
3) Create a patient‑friendly summary separate from the clinician‑oriented summary.
4) Avoid fabrication; clearly mark uncertain items and request clarifications.

Reliability and safety:
- Not medical advice. Summaries are for convenience; original documentation is authoritative.

Output format:
SECTION: CLINICIAN SUMMARY
SECTION: PATIENT‑FRIENDLY SUMMARY
SECTION: DATA GAPS/UNCERTAINTY
SECTION: NEXT INFO TO GATHER
"""

# =========================
# Medical Agents
# =========================

blood_analysis_agent = Agent(
    agent_name="Blood-Data-Analysis-Agent",
    agent_description="Explains and contextualizes common blood test panels with structured insights",
    model_name="claude-haiku-4-5",
    max_loops=1,
    top_p=None,
    dynamic_temperature_enabled=True,
    system_prompt=blood_analysis_system_prompt,
    tags=["lab", "hematology", "metabolic", "education"],
    capabilities=["panel-interpretation", "risk-flagging", "guideline-citation"],
    role="worker",
    temperature=None,
)

icd10_mapping_agent = Agent(
    agent_name="ICD10-Symptom-Mapper-Agent",
    agent_description="Maps symptom descriptions to multiple plausible ICD‑10‑CM codes with justifications",
    model_name="claude-haiku-4-5",
    max_loops=1,
    top_p=None,
    dynamic_temperature_enabled=True,
    system_prompt=icd10_mapping_system_prompt,
    tags=["icd10", "coding", "triage", "documentation"],
    capabilities=["code-suggestion", "documentation-gap-detection"],
    role="worker",
    temperature=None,
)

treatment_planner_agent = Agent(
    agent_name="Treatment-Solutions-Agent",
    agent_description="Summarizes evidence‑based, non‑directive management option categories with citations",
    model_name="claude-haiku-4-5",
    max_loops=1,
    top_p=None,
    dynamic_temperature_enabled=True,
    system_prompt=treatment_planner_system_prompt,
    tags=["treatment", "guidelines", "education"],
    capabilities=["options-summarization", "risk-contextualization"],
    role="worker",
    temperature=None,
)

drug_interaction_agent = Agent(
    agent_name="Drug-Interaction-Agent",
    agent_description="Explains potential drug interactions, mechanisms, and monitoring considerations",
    model_name="claude-haiku-4-5",
    max_loops=1,
    top_p=None,
    dynamic_temperature_enabled=True,
    system_prompt=drug_interaction_system_prompt,
    tags=["pharmacology", "safety", "interactions"],
    capabilities=["interaction-survey", "severity-ranking", "source-citation"],
    role="worker",
    temperature=None,
)

imaging_triage_agent = Agent(
    agent_name="Imaging-Triage-Agent",
    agent_description="Provides plain‑language explanations of imaging impressions and non‑directive follow‑ups",
    model_name="claude-haiku-4-5",
    max_loops=1,
    top_p=None,
    dynamic_temperature_enabled=True,
    system_prompt=imaging_triage_system_prompt,
    tags=["radiology", "triage", "education"],
    capabilities=["impression-explanation", "followup-context"],
    role="worker",
    temperature=None,
)

clinical_summary_agent = Agent(
    agent_name="Clinical-Note-Summarizer-Agent",
    agent_description="Organizes clinical notes into clinician and patient‑friendly summaries with gaps highlighted",
    model_name="claude-haiku-4-5",
    max_loops=1,
    top_p=None,
    dynamic_temperature_enabled=True,
    system_prompt=clinical_summary_system_prompt,
    tags=["summarization", "documentation"],
    capabilities=["note-organization", "gap-detection"],
    role="worker",
    temperature=None,
)

# Create AOP instance
deployer = AOP(
    server_name="MedicalAgentServer",
    description=(
        "MedicalAgentServer: A robust multi-agent system deploying specialized medical AI agents for clinical data analysis, "
        "ICD-10 code mapping, evidence‑based treatment options summarization, drug interaction evaluation, "
        "imaging triage explanations, and structured clinical note summarization. This server enables seamless integration "
        "and orchestration of advanced healthcare agents for safe, educational, and guideline-aligned medical support. "
        "Agents include: Blood-Data-Analysis-Agent (lab panel interpreter), ICD10-Symptom-Mapper-Agent (diagnostic code candidate generator), "
        "Treatment-Solutions-Agent (treatment option highlighter), Drug-Interaction-Agent (multi-agent interaction assessment), "
        "Imaging-Triage-Agent (radiology finding explainer), Clinical-Note-Summarizer-Agent (clinical documentation enhancer). "
        "Designed for interoperability, reliability, transparency, and strict non-diagnostic output."
    ),
    port=8000,
    verbose=True,
    log_level="INFO",
)

agents = [
    blood_analysis_agent,
    icd10_mapping_agent,
    treatment_planner_agent,
    drug_interaction_agent,
    imaging_triage_agent,
    clinical_summary_agent,
]
deployer.add_agents_batch(agents)

# Start the server
deployer.run()
