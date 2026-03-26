from curl_cffi import requests
import pandas as pd
import time

def get_nse_session():
    print("1. Forging secure session with NSE servers (TLS Spoofing Active)...")
    # The 'impersonate="chrome"' flag mathematically mimics a real browser's network handshake
    session = requests.Session(impersonate="chrome")
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    session.headers.update(headers)
    
    # Hit homepage to harvest the required cookies
    session.get("https://www.nseindia.com", timeout=15)
    
    print("   [Stealth Delay: Simulating human navigation...]")
    time.sleep(2)
    return session

def analyze_option_chain(session):
    print("\n2. Ripping NIFTY Option Chain (Derivatives Data)...")
    session.headers.update({"Referer": "https://www.nseindia.com/option-chain"})
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    
    response = session.get(url, timeout=15)
    
    if response.status_code != 200:
        print(f"Hard Blocked. Status Code: {response.status_code}")
        return
        
    try:
        data = response.json()
        
        if 'filtered' not in data:
            print("WAF INTERCEPT: The server returned a restricted JSON payload.")
            return
            
        tot_ce_oi = data['filtered']['CE']['totOI']
        tot_pe_oi = data['filtered']['PE']['totOI']
        
        pcr = tot_pe_oi / tot_ce_oi if tot_ce_oi else 0
        
        print("================ DERIVATIVES SENTIMENT ================")
        print(f"Total Call OI (Resistance): {tot_ce_oi:,}")
        print(f"Total Put OI  (Support):    {tot_pe_oi:,}")
        print(f"NIFTY Put-Call Ratio (PCR): {pcr:.2f}")
        
        if pcr > 1:
            print("ANALYSIS: PCR > 1. Institutions are heavily writing Puts. Bullish undertone.")
        elif pcr < 0.7:
            print("ANALYSIS: PCR < 0.7. Institutions are aggressively writing Calls. High bearish resistance.")
        else:
            print("ANALYSIS: PCR is neutral. Market makers are hedging both sides.")
        print("=======================================================")
        
    except Exception as e:
        print(f"Failed to parse Option Chain: {e}")

def analyze_bulk_deals(session):
    print("\n3. Scanning for Institutional Bulk Deals (Cash Market)...")
    session.headers.update({"Referer": "https://www.nseindia.com/market-data/bulk-deals"})
    url = "https://www.nseindia.com/api/snapshot-capital-market-largedeal"
    
    time.sleep(2)
    response = session.get(url, timeout=15)
    
    if response.status_code != 200:
        print(f"Bulk Deals Hard Blocked. Status Code: {response.status_code}")
        return
        
    try:
        # If the text is completely blank, we got shadow blocked again
        if not response.text.strip():
            print("WAF INTERCEPT: Server returned an empty response.")
            return
            
        data = response.json()
        
        if 'BULK_DEALS_DATA' not in data:
            print("WAF INTERCEPT: The server returned an altered payload.")
            return
            
        bulk_deals = data['BULK_DEALS_DATA']
        if not bulk_deals:
            print("No bulk deals reported yet today.")
            return
            
        df = pd.DataFrame(bulk_deals)
        
        if 'symbol' in df.columns:
            clean_df = df[['symbol', 'clientName', 'buySell', 'qty', 'watp']]
            print("================ TOP INSTITUTIONAL BLOCK TRADES ================\n")
            print(clean_df.head(10).to_string(index=False))
            print("\n==================================================================")
        else:
            print("WAF INTERCEPT: Bulk deal payload structure altered by server.")
            
    except Exception as e:
        print(f"Failed to parse Bulk Deal JSON: {e}")

if __name__ == "__main__":
    try:
        master_session = get_nse_session()
        analyze_option_chain(master_session)
        analyze_bulk_deals(master_session)
    except Exception as e:
        print(f"Sniper failure: {e}")