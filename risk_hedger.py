from curl_cffi import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)
client = genai.Client()

def get_nse_session():
    print("1. Forging secure session with NSE servers...")
    session = requests.Session(impersonate="chrome")
    session.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    session.get("https://www.nseindia.com", timeout=15)
    time.sleep(2)
    return session

def execute_hedge_analysis(session):
    print("2. Extracting Live Institutional Block Trades...\n")
    session.headers.update({"Referer": "https://www.nseindia.com/market-data/bulk-deals"})
    url = "https://www.nseindia.com/api/snapshot-capital-market-largedeal"
    
    time.sleep(2)
    response = session.get(url, timeout=15)
    
    if response.status_code != 200 or not response.text.strip():
        print(f"[TRAP 1 HIT] Firewall block. Status: {response.status_code}")
        return

    data = response.json()
    if 'BULK_DEALS_DATA' not in data:
        print("[TRAP 1 HIT] NSE altered the JSON payload. Missing BULK_DEALS_DATA.")
        return

    df = pd.DataFrame(data['BULK_DEALS_DATA'])
    if df.empty:
        print("No bulk deals have occurred yet today.")
        return
        
    # ---------------------------------------------------------
    # DYNAMIC PORTFOLIO SIMULATION
    # We grab the top 3 live symbols being traded right now to guarantee a hit
    # ---------------------------------------------------------
    live_symbols = df['symbol'].unique()[:3]
    print(f"3. Locking onto Active Portfolio Assets: {list(live_symbols)}")
    
    portfolio_metrics = {}
    for i, sym in enumerate(live_symbols):
        # We assign varying simulated risk metrics to test the AI's logic
        portfolio_metrics[sym] = {
            'Beta': 1.4 - (i * 0.3), 
            'Sharpe': 0.8 + (i * 0.4), 
            'Max_Drawdown': f"{25 - (i * 5)}%"
        }
    
    target_portfolio = list(portfolio_metrics.keys())
    portfolio_hits = df[df['symbol'].isin(target_portfolio)].copy()
    
    if portfolio_hits.empty:
        print("\n[TRAP 2 HIT] No institutional action detected. Portfolio metrics stable.")
        return
        
    print("4. Python Quantitative Engine computing Net Institutional Flow...")
    
    # PYTHON DOES THE MATH: Calculate actual Net Flow to filter out intraday jobbing
    portfolio_hits['math_qty'] = portfolio_hits.apply(lambda row: int(row['qty']) if row['buySell'] == 'BUY' else -int(row['qty']), axis=1)
    
    net_flow = portfolio_hits.groupby('symbol')['math_qty'].sum().reset_index()
    net_flow.columns = ['Symbol', 'Net_Institutional_Flow']
    
    final_analysis_data = ""
    for index, row in net_flow.iterrows():
        sym = row['Symbol']
        flow = row['Net_Institutional_Flow']
        metrics = portfolio_metrics[sym]
        
        flow_direction = "NET ACCUMULATION (BULLISH)" if flow > 0 else "NET DISTRIBUTION (BEARISH)" if flow < 0 else "NET NEUTRAL (MARKET MAKING)"
        
        final_analysis_data += f"""
        Asset: {sym}
        Live Institutional Flow: {flow:,} shares ({flow_direction})
        Current Portfolio Beta: {metrics['Beta']:.2f}
        Current Sharpe Ratio: {metrics['Sharpe']:.2f}
        Historical Max Drawdown: {metrics['Max_Drawdown']}
        --------------------------------------------------
        """
        
    print("\n[ALGORITHMIC MATH COMPLETED - DATA HANDOFF TO CHIEF STRATEGIST]")
    print(final_analysis_data)
    
    system_prompt = """
    You are the Chief Quantitative Strategist. 
    You are presented with pre-calculated net institutional flow and the user's exact portfolio risk metrics (Beta, Sharpe, Max Drawdown).
    
    Do not recalculate the math. Your job is to generate a brief, ruthless hedging directive based on the data provided.
    For each asset, output a 1-sentence risk diagnosis, and a 1-sentence action (e.g., "Hedge Beta exposure", "Hold for accumulation").
    Keep it strictly professional.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"Generate hedging directives based on this flow:\n{final_analysis_data}",
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
        )
    )

    print("================ EXECUTIVE HEDGING DIRECTIVE ================\n")
    print(response.text)
    print("\n=============================================================")

if __name__ == "__main__":
    try:
        master_session = get_nse_session()
        execute_hedge_analysis(master_session)
    except Exception as e:
        print(f"System failure: {e}")