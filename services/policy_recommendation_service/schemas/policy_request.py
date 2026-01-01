from pydantic import BaseModel
from typing import List, Optional

class PolicyRequest(BaseModel):
    ages: List[int]  # Age(s) of insured members
    individual_or_family: str  # "individual" or "family floater"
    city: str  # City of residence
    pre_existing_diseases: Optional[List[str]] = None  # Any pre-existing diseases
    desired_sum_insured: float  # Desired sum insured
    budget: float  # Monthly or annual budget
    preference: str  # e.g., "low premium", "maximum coverage", "no co-pay", "corporate hospital network"

class PolicyRecommendation(BaseModel):
    policy_name: str
    provider: str
    cost: float
    coverage: str
    reasoning: str

class PolicyResponse(BaseModel):
    content: str  # Raw recommendation text from LLM
