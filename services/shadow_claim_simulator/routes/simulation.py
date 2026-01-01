from fastapi import APIRouter, HTTPException, Depends
from services.shadow_claim_simulator.schemas.models import PayoutSimulationRequest, PayoutSimulationResponse
from services.shadow_claim_simulator.services.financial_logic import simulate_payout
from shared.utils.auth_middleware import get_current_user
from services.shadow_claim_simulator.db.session import get_policies_collection
from bson import ObjectId
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")

router = APIRouter()

@router.post("/simulate-payout")
def simulate_payout_endpoint(request: PayoutSimulationRequest, user_id: str = Depends(get_current_user)):
    try:
        policies_col = get_policies_collection()
        policy = policies_col.find_one({"user_id": ObjectId(user_id)})
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found for user.")
        policy_dna = policy
        if policy_dna.get("sum_insured", 0) == 0:
            raise HTTPException(status_code=400, detail="Sum Insured is 0, cannot simulate payout.")
        
        # Extract request fields
        hospital_bill = [item.dict() for item in request.hospital_bill]  # Convert to dict list
        stay_context = request.stay_context.dict()
        
        result = simulate_payout(policy_dna, hospital_bill, stay_context)
        
        # Use LLM to format the response in human language for a naive user
        llm = ChatMistralAI(api_key=API_KEY, model="mistral-small-2506")
        prompt = f"""
        Explain this insurance payout simulation result to a naive user in simple, easy-to-understand language. Avoid jargon or explain it simply.

        Here is the hospital bill: {hospital_bill}

        Here is the simulation result: {result.model_dump()}

        Formulate a friendly, clear explanation of what the payout is, why deductions happened, and any advice.

        Just provide the explanation text without extra gibberish.
        """
        messages = [{"role": "user", "content": prompt}]
        llm_response = llm.invoke(messages)
        formatted_response = llm_response.content.strip()
        
        return {"formatted_explanation": formatted_response}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
