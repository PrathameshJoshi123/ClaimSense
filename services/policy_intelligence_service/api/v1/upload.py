from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
import shutil
import os
import tempfile
from services.policy_intelligence_service.services.ocr_engine import process_pdf
from services.policy_intelligence_service.services.llm_parser import PolicyParser
from services.policy_intelligence_service.services.risk_analyzer import analyze_risks
from services.policy_intelligence_service.db.session import get_db, get_users_collection
from shared.utils.auth_middleware import get_current_user
from bson import ObjectId
from services.policy_intelligence_service.worker import process_policy  # Add import
from services.policy_intelligence_service.services.vector_store import index_policy_for_rag  # Add import for vector indexing

router = APIRouter()
parser = PolicyParser()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), sum_insured: float = Form(...), current_user: str = Depends(get_current_user)):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Sequential processing
    text = process_pdf(file_path)
    parsed = await parser.parse_text_to_dna(text)
    risks = analyze_risks(parsed)
    parsed.risk_analysis.negative_features = risks
    db = get_db()
    policy_doc = parsed.model_dump()
    policy_doc["sum_insured"] = sum_insured
    try:
        policy_doc["user_id"] = ObjectId(current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user ID: {str(e)}")
    result = db.policies.insert_one(policy_doc)
    # Index the policy text in Pinecone for RAG, using policy_id as reference
    try:
        index_policy_for_rag(parsed.policy_metadata.policy_id_uin, text, current_user)
    except Exception as e:
        print(f"Error indexing policy for RAG: {str(e)}")
    os.remove(file_path)
    return {"message": "PDF processed and saved", "id": str(result.inserted_id)}
