import json
import logging
import re
from langchain_mistralai import ChatMistralAI
from services.policy_intelligence_service.schemas.dna_schema import PolicyDNA
from services.policy_intelligence_service.core.config import API_KEY

class PolicyParser:
    def __init__(self):
        self.system_prompt = """
        1. SEARCH & INTERPRETATION LOGIC (MANDATORY)
        1.1 Room Rent & Proportionate Deduction

        Search sections titled or containing:

        “In-patient Hospitalization”

        “Eligibility”

        “Accommodation”

        “Room Rent”

        Identify:

        Room category limits (category / percentage / flat / no limit)

        Clauses stating “Associated Medical Expenses,” “Proportionate Deduction,” or similar

        If higher room selection leads to pro-rata reduction in doctor, surgery, or hospital charges, set:

        "proportionate_deduction": true

        1.2 Co-payment (Strict Extraction)

        Extract only mandatory co-payments

        Ignore:

        Voluntary deductibles

        Optional co-pay discounts

        Identify if co-pay is:

        Entry-age based (e.g., above 60 years)

        Zone / location based

        If not mandatory, return 0 and mark flags as false

        1.3 Waiting Periods (Months Only)

        Explicitly identify:

        Initial Waiting Period

        Specific / Named Illness Waiting Period

        Pre-Existing Disease (PED) Waiting Period

        If not mentioned → return null

        2. UNDERWRITING RISK AUDIT (ANTI-CUSTOMER PATTERNS)

        Analyze wording for hidden or restrictive clauses, including but not limited to:

        2.1 Sub-limits

        Disease-wise or procedure-wise caps such as:

        Cataract

        Joint Replacement

        Hernia

        ENT / Tonsils

        Flag low flat caps vs Sum Insured linkage

        2.2 Modern Treatments

        Identify coverage of:

        Robotic surgery

        Stem cell therapy

        Oral chemotherapy

        Immunotherapy

        Distinguish clearly between:

        Covered up to Sum Insured

        Covered with sub-limit

        Explicitly excluded

        Not mentioned

        2.3 Restoration / Reinstatement Rules

        Check if restoration:

        Applies only after full exhaustion

        Is allowed for related illnesses

        Is restricted to unrelated illnesses only (hidden negative)

        Document these precisely.

        3. SCORING FRAMEWORK (0–100)
        Base Score: 50
        Deductions (apply cumulatively)

        Room rent cap: –20

        Proportionate deduction: –10

        Mandatory co-pay: –15

        Low disease sub-limits: –10

        PED waiting period ≥ 36 months: –10

        Additions

        No room rent limit: +20

        Restoration usable for related illnesses: +10

        Consumables covered: +10

        📌 Rules

        Clamp final score between 0 and 100

        If data is missing, do not penalize or reward

        4. CONFLICT RESOLUTION RULES (CRITICAL)

        If multiple documents exist:

        Policy Wording overrides Prospectus

        Endorsements override both

        If clauses conflict:

        Use the most restrictive interpretation

        Document the conflict in hidden_clauses

        5. SUMMARY STYLE RULES

        Explain like a helpful, informed peer

        Assume the reader is a first-time insurance buyer

        Avoid insurance jargon such as:

        “Incurred”

        “Inception”

        “Indemnity”

        Limit to 3–4 sentences

        OUTPUT FORMAT (STRICT JSON — NO EXTRA TEXT)
        {
          "policy_metadata": {
            "policy_id_uin": "string",
            "insurer": "string",
            "policy_name": "string",
            "overall_security_score": number
          },
          "room_rent_limit": {
            "limit_type": "CATEGORY|PERCENTAGE|FLAT|NO_LIMIT|NOT_MENTIONED",
            "value": "string",
            "proportionate_deduction": boolean,
            "excludes_icu_and_pharmacy": boolean
          },
          "co_pay": {
            "percentage": number,
            "is_entry_age_based": boolean,
            "threshold_age": number,
            "is_zone_based": boolean
          },
          "waiting_periods_months": {
            "initial": number,
            "specific_illnesses": number,
            "pre_existing_diseases": number
          },
          "modern_treatments": {
            "treatment_name": {
              "covered": boolean,
              "limit": "Up to Sum Insured | Flat Amount | Not mentioned | Excluded"
            }
          },
          "risk_analysis": {
            "hidden_clauses": ["Exact restrictive wording or explanation"],
            "negative_features": ["Explicit caps, co-pays, or exclusions"],
            "positive_features": ["High-value or consumer-friendly benefits"]
          },
          "notice_period": {
            "planned_hours": number,
            "emergency_hours": number
          },
          "non_payable_items": ["Only items explicitly listed in the document"],
          "plain_english_summary": "10 - 15 sentence consumer-friendly explanation"
        }
        """

    async def parse_text_to_dna(self, raw_text: str) -> PolicyDNA:
        logging.debug(f"Parsing text: {raw_text[:200]}...")  # Log first 200 chars of input
        llm = ChatMistralAI(api_key=API_KEY, model="mistral-large-latest")
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": raw_text}
        ]
        response = await llm.ainvoke(messages)
        print(f"LLM response: {response}")
        logging.debug(f"LLM response: {response.content}")
        # Strip markdown code block if present
        json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            json_str = response.content.strip()
        logging.debug(f"Extracted JSON: {json_str}")
        # Clean the JSON string by removing control characters
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        try:
            return PolicyDNA.model_validate_json(json_str)
        except Exception as e:
            logging.error(f"JSON parsing failed: {e}")
            # Fallback if JSON parsing fails
            return PolicyDNA(
                policy_metadata={
                    "policy_id_uin": "unknown",
                    "insurer": "unknown",
                    "policy_name": "unknown",
                    "overall_security_score": 50
                },
                room_rent_limit={
                    "limit_type": "NO_LIMIT",
                    "value": "unknown",
                    "proportionate_deduction": False,
                    "excludes_icu_and_pharmacy": False
                },
                co_pay={
                    "percentage": 0.0,
                    "is_entry_age_based": False,
                    "threshold_age": None,
                    "is_zone_based": False
                },
                waiting_periods_months={
                    "initial": None,
                    "specific_illnesses": None,
                    "pre_existing_diseases": None
                },
                modern_treatments={},
                risk_analysis={
                    "hidden_clauses": [],
                    "negative_features": [],
                    "positive_features": []
                },
                notice_period={
                    "planned_hours": 0,
                    "emergency_hours": 0
                },
                non_payable_items=[],
                plain_english_summary="Unable to generate summary due to parsing error."
            )
