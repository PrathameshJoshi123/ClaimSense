from fastapi import APIRouter, HTTPException, Depends
from services.policy_intelligence_service.db.session import get_db
from services.policy_intelligence_service.schemas.dna_schema import PolicyDNA
from services.policy_intelligence_service.services.risk_analyzer import analyze_risks
from shared.utils.auth_middleware import get_current_user
from bson import ObjectId

router = APIRouter()


@router.get("/policies/{policy_id}")
async def get_policy(policy_id: str, current_user: str = Depends(get_current_user)):
    db = get_db()
    policy = db.policies.find_one({"_id": ObjectId(policy_id), "user_id": ObjectId(current_user)})
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    policy["_id"] = str(policy["_id"])
    policy["user_id"] = str(policy["user_id"])
    return policy


@router.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str, current_user: str = Depends(get_current_user)):
    db = get_db()
    result = db.policies.delete_one({"_id": ObjectId(policy_id), "user_id": ObjectId(current_user)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted"}

@router.get("/policies")
async def get_policies(current_user: str = Depends(get_current_user)):
    db = get_db()
    policies = list(db.policies.find({"user_id": ObjectId(current_user)}))
    for policy in policies:
        policy["_id"] = str(policy["_id"])
        policy["user_id"] = str(policy["user_id"])
    return policies
