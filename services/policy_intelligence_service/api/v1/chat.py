from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from langchain_pinecone import PineconeVectorStore as LangchainPinecone
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pinecone import Pinecone
from shared.utils.auth_middleware import get_current_user
from services.policy_intelligence_service.db.session import get_db
from bson import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    policy_id: str = None  # Optional policy_id for specific policy searches

@router.post("/chat")
async def chat_with_policy(request: ChatRequest, current_user: str = Depends(get_current_user)):
    try:
        embeddings = MistralAIEmbeddings(api_key=os.getenv("MISTRAL_API_KEY"))
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("policies")
        vector_store = LangchainPinecone.from_existing_index(
            index_name="policies",   # ✅ string
            embedding=embeddings,
            namespace=current_user
        )
       
        
        if request.policy_id:
            db = get_db()
            policy = db.policies.find_one({"_id": ObjectId(request.policy_id)})
            if not policy:
                raise HTTPException(status_code=404, detail="Policy not found")
            policy_id_uin = policy["policy_metadata"]["policy_id_uin"]
            search_filter = {"policy_id": policy_id_uin}
        else:
            search_filter = {}
        retriever = vector_store.as_retriever(search_kwargs={"filter": search_filter, "k": 5})
        
        # Fix: Use ainvoke instead of aget_relevant_documents
        docs = await retriever.ainvoke(request.query)
        # Debugging logs
        
        llm = ChatMistralAI(api_key=os.getenv("MISTRAL_API_KEY"), model_name="mistral-small-2506")
        
        # Modern LCEL RAG chain
        prompt = ChatPromptTemplate.from_template(
            "Answer the following question based only on the provided context:\n\n{context}\n\nQuestion: {input}"
        )
        chain = (
            {"context": retriever, "input": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        response = await chain.ainvoke(request.query)
        
        return {"response": response}
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Print full error to console for easier debugging
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
