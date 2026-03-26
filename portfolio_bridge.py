from curl_cffi import requests
import pandas as pd
import time
import ollama

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

def analyze_portfolio_risk(session):
    print("2. Extracting Live Institutional Block Trades...\n")
    session.headers.update({"Referer": "https://www.nseindia.com/market-data/bulk-deals"})
    url = "https://www.nseindia.com/api/snapshot-capital-market-largedeal"
    
    time.sleep(2)
    response = session.get(url, timeout=15)
    
    if response.status_code != 200 or not response.text.strip():
        print("Firewall block or empty response.")
        return

    data = response.json()
    if 'BULK_DEALS_DATA' not in data or not data['BULK_DEALS_DATA']:
        print("No data available.")
        return

    df = pd.DataFrame(data['BULK_DEALS_DATA'])
    clean_df = df[['symbol', 'clientName', 'buySell', 'qty', 'watp']]
    
    # ---------------------------------------------------------
    # THE PORTFOLIO MATRIX
    # We define the specific assets we are tracking for risk.
    # (Using a few from today's scrape as examples to guarantee a hit)
    # ---------------------------------------------------------
    target_portfolio = ['ASTEC', 'AGIIL', 'RELIANCE', 'HDFCBANK', 'DHRUV']
    
    print(f"3. Cross-referencing institutional flow against portfolio: {target_portfolio}")
    
    # Filter the bulk deals to ONLY show action on our specific holdings
    portfolio_hits = clean_df[clean_df['symbol'].isin(target_portfolio)]
    
    if portfolio_hits.empty:
        print("\nNo institutional action detected on portfolio holdings today. Risk metrics stable.")
        return
        
    print("\n[ALERT] Institutional flow detected in portfolio holdings:")
    flow_data = portfolio_hits.to_string(index=False)
    print(flow_data)
    
    print("\n4. Waking up Quant Agent for Risk Recalculation...\n")
    
    system_prompt = """
    You are the Chief Risk Officer for a quantitative fund. 
    You are presented with live institutional block trades that directly impact the user's current portfolio.
    
    Based ONLY on this flow data, calculate the qualitative impact on the portfolio's risk metrics. 
    Format your response ruthlessly:
    1. Assess the immediate impact on Portfolio Beta (Are institutions injecting volatility?).
    2. Assess the directional impact on the Sharpe Ratio based on the buy/sell pressure.
    3. Evaluate the shift in Max Drawdown probability for the affected assets.
    
    Do not use generic warnings. Be specific to the client names and assets provided.
    """
    
    user_prompt = f"LIVE PORTFOLIO HITS:\n{flow_data}"

    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ])

    print("================ LOCALIZED RISK ASSESSMENT ================\n")
    print(response['message']['content'])
    print("\n===========================================================")

if __name__ == "__main__":
    try:
        master_session = get_nse_session()
        analyze_portfolio_risk(master_session)
    except Exception as e:
        print(f"Bridge failure: {e}")