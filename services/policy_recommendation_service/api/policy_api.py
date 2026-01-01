from fastapi import APIRouter
from services.policy_recommendation_service.schemas.policy_request import PolicyRequest, PolicyResponse
from services.policy_recommendation_service.models.llm_service import get_policy_recommendations

router = APIRouter()

@router.post("/recommend-policies", response_model=PolicyResponse)
async def recommend_policies(request: PolicyRequest):
    result = get_policy_recommendations(request)
    return PolicyResponse(content=result)
