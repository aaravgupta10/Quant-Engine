import sys
import chromadb
import ollama
from ddgs import DDGS

# THE SILVER BULLET: Force Windows to output pure UTF-8 so symbols (₹, →) never crash the terminal
sys.stdout.reconfigure(encoding='utf-8')

def run_rag_pipeline():
    print("1. Initializing the Daily Memory Vault...")
    client = chromadb.PersistentClient(path="./db_storage")
    
    try:
        client.delete_collection("daily_macro")
    except:
        pass
    collection = client.create_collection(name="daily_macro")

    print("2. Agent 3 (Global/Macro Scout) is scraping live intelligence...")
    live_data = []
    try:
        with DDGS() as ddgs:
            # FIXED API CALL: Removed "keywords=" as DDGS changed their positional arguments
            results = list(ddgs.news("Reserve Bank of India economy", region="in-en", max_results=5))
            for r in results:
                live_data.append(r['title'] + " - " + r['body'])
    except Exception as e:
        print("Failed to gather data:", e)
        return

    print(f"3. Shredding {len(live_data)} reports into Nomic vectors and storing in ChromaDB...")
    for i, doc in enumerate(live_data):
        emb = ollama.embeddings(model="nomic-embed-text", prompt=doc)["embedding"]
        collection.upsert(ids=[str(i)], embeddings=[emb], documents=[doc])

    print("4. Vault loaded. Formulating query for the Chief Strategist...\n")
    
    question = "Synthesize the top 3 macroeconomic headlines from today and analyze their impact on the Indian economy."
    print(f"USER QUERY: {question}\n")

    q_emb = ollama.embeddings(model="nomic-embed-text", prompt=question)["embedding"]
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    retrieved_context = "\n\n".join(results['documents'][0])

    # THE FINSHOTS PROMPT OVERRIDE
    system_prompt = """You are a top-tier macroeconomic journalist writing for Finshots. 
Your job is to read the provided live intelligence and write a highly engaging, continuous, long-form article (MINIMUM 400 WORDS). 
Focus on synthesizing the top 3 macroeconomic headlines and explaining exactly how they impact the Indian economy, inflation, and retail investors.
CRITICAL RULES:
- ABSOLUTELY NO BULLET POINTS.
- ABSOLUTELY NO LISTS.
- DO NOT USE ASTERISKS.
- Write in flowing, cohesive paragraphs. Tell a story with the data."""

    user_prompt = f"Write the 400+ word Finshots-style Macro Article based on this data:\n\nVAULT CONTEXT:\n{retrieved_context}"

    print("5. Synthesizing Final Forecast...\n")
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ])

    print("================ CHIEF STRATEGIST OUTPUT ================\n")
    print(response['message']['content'])
    print("\n=========================================================")

if __name__ == "__main__":
    run_rag_pipeline()