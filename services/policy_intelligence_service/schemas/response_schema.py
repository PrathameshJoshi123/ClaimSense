from pydantic import BaseModel
from typing import List
from policy_intelligence_service.schemas.dna_schema import PolicyDNA

class PolicyResponse(BaseModel):
    id: str
    dna: PolicyDNA
