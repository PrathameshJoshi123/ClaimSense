import json
import logging
import re
from langchain_mistralai import ChatMistralAI
from services.policy_intelligence_service.core.constants import INSURANCE_TERMS
from services.policy_intelligence_service.core.config import API_KEY
from services.policy_intelligence_service.schemas.dna_schema import PolicyDNA

def analyze_risks(parsed_data: PolicyDNA) -> list:
    risks = []
    # Basic check for hidden clauses
    content = parsed_data.model_dump_json().lower()
    if "hidden_clause" in content or "fine_print" in content:
        risks.append("Potential hidden clause detected")
    
    # Use LLM for advanced risk analysis
    llm = ChatMistralAI(api_key=API_KEY, model="mistral-medium-latest")
    prompt = f"Analyze the following insurance policy data for risks, traps, and hidden clauses. Return a valid JSON array of strings listing identified risks, with no extra text or markdown: {parsed_data.model_dump_json()}"
    logging.debug(f"Risk analysis prompt: {prompt}")
    response = llm.invoke(prompt)
    logging.debug(f"LLM risk response: {response.content}")
    # Strip markdown code block if present
    json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        json_str = response.content.strip()
    logging.debug(f"Extracted risk JSON: {json_str}")
    try:
        llm_risks = json.loads(json_str)
        if isinstance(llm_risks, list):
            risks.extend(llm_risks)
        elif isinstance(llm_risks, dict) and "risks" in llm_risks:
            risks.extend(llm_risks["risks"])
    except json.JSONDecodeError as e:
        logging.error(f"Risk JSON parsing failed: {e}")
        risks.append(f"LLM Analysis: {response.content}")
    
    return risks
