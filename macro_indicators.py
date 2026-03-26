import yfinance as yf
import ollama
import time

def fetch_macro_data():
    print("1. Locking onto global leading macroeconomic indicators...")
    
    # Standard tickers for global systemic risk tracking
    tickers = {
        "US 10-Year Treasury Yield": "^TNX", 
        "Brent Crude Oil": "BZ=F", 
        "USD/INR Exchange Rate": "INR=X", 
        "Nifty 50 Index": "^NSEI"
    }
    live_data = ""
    
    for name, ticker in tickers.items():
        try:
            asset = yf.Ticker(ticker)
            data = asset.history(period="5d")
            if not data.empty:
                last_close = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                pct_change = ((last_close - prev_close) / prev_close) * 100
                live_data += f"{name}: {last_close:.2f} ({pct_change:+.2f}%)\n"
        except Exception as e:
            live_data += f"{name}: Data pull failed.\n"
            
    print("2. Raw macro indicators secured. Waking up Chief Economist Agent...")
    
    system_prompt = """You are a Chief Economist. You are provided with real-time data for leading global macroeconomic indicators.
    Write a sharp, ruthless analysis of how these specific numbers (Yields, Oil, Currency) are currently interacting and what they signal for the Indian economy today.
    Discuss potential impacts on imported inflation, foreign capital flow, and currency defense strategies. 
    Keep it strictly professional. No fluff. Just pure macro correlation."""
    
    user_prompt = f"LIVE MACRO DATA:\n{live_data}\n\nProvide the systemic correlation analysis based ONLY on these numbers."
    
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ])
    
    print("================ MACRO CORRELATION ENGINE ================\n")
    print(f"**LIVE METRICS:**\n{live_data}\n")
    print(response['message']['content'])
    print("\n==========================================================")

if __name__ == "__main__":
    fetch_macro_data()