import chromadb
import ollama
from duckduckgo_search import DDGS

def run_rag_pipeline():
    print("1. Initializing the Daily Memory Vault...")
    client = chromadb.PersistentClient(path="./db_storage")
    
    # We create a fresh collection for today's data (deleting the old one if it exists to avoid clutter)
    try:
        client.delete_collection("daily_macro")
    except:
        pass
    collection = client.create_collection(name="daily_macro")

    print("2. Agent 3 (Global/Macro Scout) is scraping live intelligence...")
    live_data = []
    try:
        with DDGS() as ddgs:
            # Pulling 5 live macro reports
            results = list(ddgs.news(keywords="Reserve Bank of India economy", region="in-en", max_results=5))
            for r in results:
                # Combining title and body into one solid intelligence block
                live_data.append(r['title'] + " - " + r['body'])
    except Exception as e:
        print("Failed to gather data:", e)
        return

    print(f"3. Shredding {len(live_data)} reports into Nomic vectors and storing in ChromaDB...")
    for i, doc in enumerate(live_data):
        emb = ollama.embeddings(model="nomic-embed-text", prompt=doc)["embedding"]
        collection.upsert(ids=[str(i)], embeddings=[emb], documents=[doc])

    print("4. Vault loaded. Formulating query for the Chief Strategist...\n")
    
    # The Question you want to ask your portfolio manager
    question = "What are the biggest immediate risks to the Indian economy mentioned in today's reports?"
    print(f"USER QUERY: {question}\n")

    # STEP A: Convert the question to math
    q_emb = ollama.embeddings(model="nomic-embed-text", prompt=question)["embedding"]
    
    # STEP B: Retrieve only the top 2 most mathematically relevant reports from the vault
    results = collection.query(query_embeddings=[q_emb], n_results=2)
    retrieved_context = "\n\n".join(results['documents'][0])

    # STEP C: Feed the retrieved data and the strict rules to Llama 3.1
    system_prompt = f"""
    You are a ruthless institutional macro strategist for an Indian Equities Portfolio.
    Answer the user's question using ONLY the provided intelligence context below. 
    If the answer is not in the context, output exactly: "Insufficient data to form a thesis."
    Do not hallucinate or use outside knowledge. Format with bullet points for specific risks.
    
    VAULT CONTEXT:
    {retrieved_context}
    """

    print("5. Synthesizing Final Forecast...\n")
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': question}
    ])

    print("================ CHIEF STRATEGIST OUTPUT ================\n")
    print(response['message']['content'])
    print("\n=========================================================")

if __name__ == "__main__":
    run_rag_pipeline()