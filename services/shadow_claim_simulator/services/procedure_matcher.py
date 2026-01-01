from dotenv import load_dotenv
import os
load_dotenv()

from langchain_mistralai import MistralAIEmbeddings
import numpy as np

# Mock ROHINI Procedure Codes
mock_procedures = [
    {"name": "Cholecystectomy", "base_cost": 50000, "standard_room_rate": 2000},
    {"name": "Appendectomy", "base_cost": 30000, "standard_room_rate": 1500},
    {"name": "Cataract Surgery", "base_cost": 25000, "standard_room_rate": 1000},
    {"name": "Hernia Repair", "base_cost": 40000, "standard_room_rate": 1800},
    {"name": "Knee Replacement", "base_cost": 150000, "standard_room_rate": 3000},
    {"name": "Gallbladder Stone Surgery", "base_cost": 45000, "standard_room_rate": 1900},
    {"name": "Thyroidectomy", "base_cost": 35000, "standard_room_rate": 1600},
    {"name": "Cesarean Section", "base_cost": 60000, "standard_room_rate": 2500},
    {"name": "Colonoscopy", "base_cost": 20000, "standard_room_rate": 1200},
    {"name": "Angioplasty", "base_cost": 200000, "standard_room_rate": 4000},
]

embeddings = MistralAIEmbeddings(api_key=os.getenv("API_KEY"))
procedure_embeddings = np.array(embeddings.embed_documents([p["name"] for p in mock_procedures]))

def match_procedure(query: str):
    query_embedding = np.array(embeddings.embed_query(query))
    # Compute cosine similarities
    similarities = np.dot(procedure_embeddings, query_embedding) / (np.linalg.norm(procedure_embeddings, axis=1) * np.linalg.norm(query_embedding))
    top_indices = np.argsort(similarities)[::-1][:3]
    results = [
        {
            "procedure": mock_procedures[i]["name"],
            "base_cost": mock_procedures[i]["base_cost"],
            "standard_room_rate": mock_procedures[i]["standard_room_rate"],
            "similarity_score": float(similarities[i])
        }
        for i in top_indices
    ]
    return results
