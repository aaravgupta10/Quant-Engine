import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import pandas as pd
import ollama

def extract_and_analyze_flow():
    print("1. Harvesting NSE session cookies...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        session.get("https://www.nseindia.com", timeout=10)
        
        print("2. Extracting raw FII/DII matrix...")
        api_url = "https://www.nseindia.com/api/fiidiiTradeReact"
        response = session.get(api_url, timeout=10)
        
        if response.status_code != 200:
            print(f"Blocked. Status Code: {response.status_code}")
            return
            
        df = pd.DataFrame(response.json())
        clean_df = df[['category', 'date', 'buyValue', 'sellValue', 'netValue']]
        
        # Calculate the total net liquidity injected or drained from the market today
        fii_net = float(clean_df[clean_df['category'] == 'FII/FPI']['netValue'].iloc[0])
        dii_net = float(clean_df[clean_df['category'] == 'DII']['netValue'].iloc[0])
        total_liquidity = fii_net + dii_net
        
        data_string = clean_df.to_string(index=False)
        
        print("3. Data secured. Waking up Quant Agent for structural analysis...\n")
        
        # THE QUANT PROMPT
        system_prompt = """
        You are a quantitative risk analyst for an Indian Equities fund. 
        Analyze the provided daily FII (Foreign) and DII (Domestic) cash market data.
        
        Do not give generic advice. Focus your analysis on:
        1. The power dynamic between FIIs and DIIs today.
        2. The net liquidity impact on the market.
        3. The immediate risk to high-beta vs low-beta portfolio holdings based on this specific flow.
        4. How this flow impacts max drawdown probability in the short term.
        
        Output your analysis in a brutal, direct, and highly technical tone. Use bullet points.
        """
        
        user_prompt = f"Today's Net Market Liquidity: {total_liquidity} Crores\n\nRaw Flow Matrix:\n{data_string}"

        response = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ])

        print("================ QUANTITATIVE LIQUIDITY ANALYSIS ================\n")
        print(response['message']['content'])
        print("\n=================================================================")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    extract_and_analyze_flow()