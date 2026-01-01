from fastapi import APIRouter, HTTPException
from schemas.models import ProcedureMatchRequest, ProcedureMatchResponse
from services.procedure_matcher import match_procedure

router = APIRouter()

@router.post("/match-procedure", response_model=ProcedureMatchResponse)
def match_procedure_endpoint(request: ProcedureMatchRequest):
    try:
        results = match_procedure(request.query)
        return ProcedureMatchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
