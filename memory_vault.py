import chromadb
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)
client_ai = genai.Client()

def test_memory_vault():
    print("1. Initializing Local Vector Database (ChromaDB)...")
    # This creates a hidden folder called 'db_storage' on your PC to save the data permanently
    client = chromadb.PersistentClient(path="./db_storage")
    
    try:
        client.delete_collection("institutional_research")
    except:
        pass
        
    # Create a collection (think of this as a specific filing cabinet)
    collection = client.get_or_create_collection(name="institutional_research")
    
    print("2. Injecting test data into the vault using Nomic Embeddings...\n")
    
    # We are loading 3 completely different pieces of data into the database
    documents = [
        "The NSE Bulk Deal data shows FIIs sold 4,000 Crores of IT sector stocks today.",
        "CRISIL downgraded the corporate debt rating of three major Indian textile manufacturers due to margin pressure.",
        "Goldman Sachs predicts the RBI will hold interest rates steady until Q4 due to persistent food inflation."
    ]
    
    # We generate the mathematical embeddings for each document using Gemini
    for i, doc in enumerate(documents):
        response = client_ai.models.embed_content(model="text-embedding-004", contents=doc)
        embedding = response.embeddings[0].values
        
        # Store it in the database
        collection.upsert(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[doc]
        )
        
    print("3. Data stored safely on disk.")
    print("4. Testing Retrieval: Asking the vault a specific question...\n")
    
    # Now, we ask a question, and the database must find the most relevant document
    question = "What is happening with textile companies?"
    print(f"QUESTION: {question}")
    
    # Convert the question into an embedding to search the database
    q_resp = client_ai.models.embed_content(model="text-embedding-004", contents=question)
    q_embedding = q_resp.embeddings[0].values
    
    # Retrieve the top 1 most relevant result
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=1
    )
    
    print(f"\nVAULT RETRIEVED: {results['documents'][0][0]}")

if __name__ == "__main__":
    test_memory_vault()