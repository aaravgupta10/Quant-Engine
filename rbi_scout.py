from duckduckgo_search import DDGS

def fetch_rbi_intelligence():
    print("Deploying DuckDuckGo Syndicate Bypass...\n")
    
    try:
        # We initialize the search client
        with DDGS() as ddgs:
            # We specifically target Indian regional news (in-en) about the RBI
            results = list(ddgs.news(
                keywords="Reserve Bank of India macro economy", 
                region="in-en", 
                max_results=3
            ))
            
            if not results:
                print("No intelligence found.")
                return

            for i, r in enumerate(results, 1):
                print(f"[{i}] SOURCE: {r['source']}")
                print(f"TITLE: {r['title']}")
                print(f"DATE: {r['date']}")
                # This 'body' field contains the actual meat of the article, pre-extracted
                print(f"INTELLIGENCE:\n{r['body']}\n")
                print("-" * 70 + "\n")
                
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    fetch_rbi_intelligence()