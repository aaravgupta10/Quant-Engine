import chromadb
import ollama
from ddgs import DDGS

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
    
    # The new focus for the macro blog
    question = "Synthesize the top 3 macroeconomic headlines from today and analyze their impact on the Indian economy."
    print(f"USER QUERY: {question}\n")

    # STEP A: Convert the question to math
    q_emb = ollama.embeddings(model="nomic-embed-text", prompt=question)["embedding"]
    
    # STEP B: Retrieve the top 3 most relevant reports from the vault
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    retrieved_context = "\n\n".join(results['documents'][0])

    # STEP C: Feed the retrieved data and the strict new analyst rules to Llama 3.1
    system_prompt = """You are a Senior Macroeconomic Equity Analyst at a Tier-1 quantitative fund. 
Your job is to read the provided live intelligence and write a highly detailed, professional blog-style brief (minimum 400 words). 
Focus strictly on synthesizing the top 3 leading macroeconomic indicators or systemic themes found in the data. 
Do not give me a list of bullet points. Write cohesive, analytical paragraphs. Break down exactly how these specific themes will impact the broader Indian equity markets, corporate operating leverage, and systemic risk over the next quarter. 
Use a sophisticated, institutional tone."""

    user_prompt = f"Analyze this live intelligence and write the 400+ word Macro Equity Analyst Blog:\n\nVAULT CONTEXT:\n{retrieved_context}"

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