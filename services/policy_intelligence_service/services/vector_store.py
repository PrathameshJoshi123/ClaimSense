from dotenv import load_dotenv
import os
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_pinecone import Pinecone as LangchainPinecone
from pinecone import Pinecone, ServerlessSpec

INDEX_NAME = "policies"
EMBED_DIM = 1024  # Mistral embedding dimension

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Ensure index exists
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIM,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

def index_policy_for_rag(policy_id: str, raw_text: str, user_id: str):
    try:
        print(f"Indexing policy {policy_id} for user {user_id}")

        # 1. Split text
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = splitter.split_text(raw_text)

        # 2. Metadata
        metadatas = [
            {
                "policy_id": policy_id,
                "user_id": user_id,
                "chunk": i
            }
            for i in range(len(chunks))
        ]

        # 3. Embeddings
        embeddings = MistralAIEmbeddings(
            api_key=os.getenv("MISTRAL_API_KEY")
        )

        # 4. Vector store (namespace = user)
        vector_store = LangchainPinecone(
            index_name=INDEX_NAME,
            embedding=embeddings,
            namespace=user_id  # tenant isolation
        )

        # 5. Upload vectors
        vector_store.add_texts(
            texts=chunks,
            metadatas=metadatas
        )

        print(f"Indexed {len(chunks)} chunks into Pinecone cloud")
        return vector_store

    except Exception as e:
        print(f"Error indexing policy {policy_id}: {e}")
        raise
