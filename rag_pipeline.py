import sys
import chromadb
import os
from dotenv import load_dotenv
from google import genai
from ddgs import DDGS

# THE SILVER BULLET: Force Windows to output pure UTF-8 so symbols (₹, →) never crash the terminal
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(override=True)
client_ai = genai.Client()

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
            queries = ["Reserve Bank of India economy", "Indian stock market", "Global macro economy India impact"]
            for query in queries:
                results = list(ddgs.news(query, region="in-en", max_results=5))
                for r in results:
                    live_data.append(r['title'] + " - " + r['body'])
    except Exception as e:
        print("Failed to gather data:", e)
        return

    print(f"3. Shredding {len(live_data)} reports into Gemini vectors and storing in ChromaDB...")
    for i, doc in enumerate(live_data):
        response = client_ai.models.embed_content(model="gemini-embedding-001", contents=doc)
        emb = response.embeddings[0].values
        collection.upsert(ids=[str(i)], embeddings=[emb], documents=[doc])

    print("4. Vault loaded. Formulating query for the Chief Strategist...\n")
    
    question = "Identify a major recent macroeconomic event, policy shift, or structural change to dive deep into its history, goals, numbers, and reasoning."
    print(f"USER QUERY: {question}\n")

    q_resp = client_ai.models.embed_content(model="gemini-embedding-001", contents=question)
    q_emb = q_resp.embeddings[0].values
    results = collection.query(query_embeddings=[q_emb], n_results=10)
    retrieved_context = "\n\n".join(results['documents'][0])

    # THE FINSHOTS PROMPT OVERRIDE
    system_prompt = """You are a top-tier macroeconomic journalist writing for Finshots.
Your job is to write a highly engaging, continuous, long-form article (MINIMUM 800 WORDS).
Instead of a generic macro overview, you must pick ONE specific macroeconomic event (either a recent event from the provided live intelligence, or an old, highly relevant historical event) and dive extremely deep into it.
Decode exactly how it came into existence, the specific goals it had, the exact numbers that were achieved, and the detailed reasoning behind its performance, numbers, and policies.
CRITICAL RULES:
- ABSOLUTELY NO BULLET POINTS.
- ABSOLUTELY NO LISTS.
- DO NOT USE ASTERISKS.
- Write in flowing, cohesive paragraphs. Tell a story with the data.
- Ensure your writing is highly varied, non-repetitive, and deeply analytical.
- Avoid repeating the same points or phrases. Provide a deep-dive analysis of a single event."""

    user_prompt = f"Write the 800+ word deep-dive Finshots-style Macro Article on a specific event (using the provided context if a recent event stands out, or a relevant historical event). Detail its origins, goals, exact numbers, and policy reasoning:\n\nVAULT CONTEXT:\n{retrieved_context}"

    print("5. Synthesizing Final Forecast...\n")
    response = client_ai.models.generate_content(
        model='gemini-flash-latest',
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
        )
    )

    print("================ CHIEF STRATEGIST OUTPUT ================\n")
    print(response.text)
    print("\n=========================================================")

if __name__ == "__main__":
    run_rag_pipeline()