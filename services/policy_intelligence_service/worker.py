import asyncio
from services.policy_intelligence_service.services.ocr_engine import process_pdf
from services.policy_intelligence_service.services.llm_parser import PolicyParser
from services.policy_intelligence_service.services.risk_analyzer import analyze_risks
from services.policy_intelligence_service.services.vector_store import index_policy_for_rag
from services.policy_intelligence_service.db.session import get_db

parser = PolicyParser()

def process_policy(file_path: str):
    text = process_pdf(file_path)
    parsed = asyncio.run(parser.parse_text_to_dna(text))
    risks = analyze_risks(parsed)
    print("hi")
    parsed.risks = risks
    print("hello")
    db = get_db()
    print("hey")
    policy_doc = parsed.model_dump()
    result = db.policies.insert_one(policy_doc)
    print("done")
    # New: Index for RAG
    policy_id = parsed.policy_id  # Use parsed policy_id as unique identifier
    index_policy_for_rag(policy_id, text)
    print("RAG indexing completed")
