import sys
import yfinance as yf
import matplotlib.pyplot as plt
import ollama
import math

# Force UTF-8 so Windows never crashes
sys.stdout.reconfigure(encoding='utf-8')

def run_technical_analysis():
    print("1. Scraping Yield Curve, India VIX, and Moving Averages...")
    
    # --- 1. THE YIELD CURVE ---
    yield_tickers = {"3-Month": "^IRX", "5-Year": "^FVX", "10-Year": "^TNX", "30-Year": "^TYX"}
    yields = {}
    for name, ticker in yield_tickers.items():
        try:
            data = yf.Ticker(ticker).history(period="1d")
            yields[name] = data['Close'].iloc[-1] if not data.empty else 0.0
        except:
            yields[name] = 0.0

    # Draw the chart and save it as an image
    plt.figure(figsize=(7, 4))
    plt.plot(list(yields.keys()), list(yields.values()), marker='o', color='#dc2626', linewidth=2.5, markersize=8)
    plt.title('Live US Treasury Yield Curve', fontsize=12, fontweight='bold', color='#0f172a')
    plt.ylabel('Yield (%)', fontsize=10, color='#334155')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gca().set_facecolor('#f8fafc')
    plt.tight_layout()
    plt.savefig('yield_curve.png', dpi=150, bbox_inches='tight')
    plt.close()

    # --- 1.5 RECESSION GAUGE ---
    spread = yields.get('10-Year', 0.0) - yields.get('3-Month', 0.0)
    x = -0.596 - 0.710 * spread
    recession_prob = (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0 * 100

    plt.figure(figsize=(6, 1.5))
    color = '#ef4444' if recession_prob > 50 else ('#f97316' if recession_prob > 30 else '#22c55e')
    plt.barh([0], [recession_prob], color=color, height=0.4)
    plt.barh([0], [100 - recession_prob], left=[recession_prob], color='#e2e8f0', height=0.4)
    plt.xlim(0, 100)
    plt.yticks([])
    plt.xlabel('Recession Probability (%)', fontsize=10, fontweight='bold', color='#334155')
    plt.title(f'10Y-3M Spread: {spread:.2f}% | Prob: {recession_prob:.1f}%', fontsize=10, color='#0f172a', fontweight='bold')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().set_facecolor('#f8fafc')
    plt.tight_layout()
    plt.savefig('recession_gauge.png', dpi=150, bbox_inches='tight')
    plt.close()

    # --- 2. INDIA VIX ---
    try:
        vix_data = yf.Ticker("^INDIAVIX").history(period="6mo")
        if not vix_data.empty:
            vix_val = vix_data['Close'].iloc[-1]
            plt.figure(figsize=(7, 4))
            plt.plot(vix_data.index, vix_data['Close'], color='#ea580c', linewidth=1.5)
            plt.title('India VIX (6-Month Trend)', fontsize=12, fontweight='bold', color='#0f172a')
            plt.ylabel('VIX Level', fontsize=10, color='#334155')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.gca().set_facecolor('#f8fafc')
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            plt.savefig('india_vix.png', dpi=150, bbox_inches='tight')
            plt.close()
        else:
            vix_val = "N/A"
    except:
        vix_val = "N/A"

    # --- 2.5 HIGH YIELD CREDIT SPREAD PROXY ---
    try:
        # We use IEF (Treasury) / HYG (High Yield) as a proxy for credit spread stress
        # When stress is high, High Yield crashes and Treasuries rally, sending this ratio UP.
        hyg_data = yf.Ticker("HYG").history(period="6mo")['Close']
        ief_data = yf.Ticker("IEF").history(period="6mo")['Close']
        if not hyg_data.empty and not ief_data.empty:
            spread_proxy = ief_data / hyg_data
            latest_spread = spread_proxy.iloc[-1]
            plt.figure(figsize=(7, 4))
            plt.plot(spread_proxy.index, spread_proxy, color='#8b5cf6', linewidth=1.5)
            plt.title('High Yield Credit Stress Proxy (IEF/HYG, 6-Month)', fontsize=12, fontweight='bold', color='#0f172a')
            plt.ylabel('Stress Ratio', fontsize=10, color='#334155')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.gca().set_facecolor('#f8fafc')
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            plt.savefig('hyg_spread.png', dpi=150, bbox_inches='tight')
            plt.close()
        else:
            latest_spread = "N/A"
    except:
        latest_spread = "N/A"

    # --- 2.8 INTERBANK RATE (Risk-Free Proxy) ---
    try:
        irx_data = yf.Ticker("^IRX").history(period="6mo")
        if not irx_data.empty:
            irx_val = irx_data['Close'].iloc[-1]
            plt.figure(figsize=(7, 4))
            plt.plot(irx_data.index, irx_data['Close'], color='#0284c7', linewidth=1.5)
            plt.title('Interbank/Risk-Free Rate (^IRX, 6-Month)', fontsize=12, fontweight='bold', color='#0f172a')
            plt.ylabel('Yield (%)', fontsize=10, color='#334155')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.gca().set_facecolor('#f8fafc')
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            plt.savefig('interbank_rate.png', dpi=150, bbox_inches='tight')
            plt.close()
        else:
            irx_val = "N/A"
    except:
        irx_val = "N/A"

    # --- 3. TECHNICAL ANCHORS (Nifty 50) ---
    try:
        nifty = yf.Ticker("^NSEI").history(period="200d")
        current_price = nifty['Close'].iloc[-1]
        sma_50 = nifty['Close'].tail(50).mean()
        sma_200 = nifty['Close'].mean()
    except:
        current_price = sma_50 = sma_200 = 0.0

    print("2. Raw technicals secured. Waking up Quantitative Technical Agent...")

    prompt_data = f"""
    LIVE TECHNICAL DATA:
    1. US Yield Curve: 3-Month={yields.get('3-Month'):.2f}%, 5-Year={yields.get('5-Year'):.2f}%, 10-Year={yields.get('10-Year'):.2f}%, 30-Year={yields.get('30-Year'):.2f}%
    2. Recession Gauge: 10Y-3M Spread={spread:.2f}%, Implied Probability={recession_prob:.1f}%
    3. India VIX (Fear Gauge): {vix_val if isinstance(vix_val, str) else f"{vix_val:.2f}"}
    4. Nifty 50 Anchors: Current Price={current_price:.2f}, 50-Day SMA={sma_50:.2f}, 200-Day SMA={sma_200:.2f}
    5. High Yield Credit Stress Proxy (IEF/HYG Ratio): {latest_spread if isinstance(latest_spread, str) else f"{latest_spread:.4f}"}
    6. Interbank/Risk-Free Rate (^IRX): {irx_val if isinstance(irx_val, str) else f"{irx_val:.2f}%"}
    """

    system_prompt = """You are a ruthless Quantitative Technical Analyst.
    Analyze the provided technical data. Write exactly six short, highly analytical paragraphs:
    Paragraph 1: Assess the shape of the US Yield Curve (Is it inverted? Normal? What does it signal for global liquidity?).
    Paragraph 2: Assess the Recession Probability gauge based on the 10Y-3M spread.
    Paragraph 3: Assess the India VIX (Is fear high or low? Are markets complacent or panicked?).
    Paragraph 4: Assess the Nifty 50 against its 50-Day and 200-Day Moving Averages (Is it overextended, breaking down, or in a secular bull trend?).
    Paragraph 5: Assess the High Yield Credit Stress Proxy (Are credit spreads widening, signaling stress, or tightening, signaling risk-on?).
    Paragraph 6: Assess the Interbank/Risk-Free Rate (Is the short-term rate elevated? What does this mean for borrowing costs and liquidity?).
    CRITICAL: NO BULLET POINTS. NO LISTS. NO ASTERISKS. Write flowing, professional paragraphs."""

    user_prompt = f"{prompt_data}\n\nProvide the 6-paragraph technical insight."

    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ])

    print("================ TECHNICAL ANCHOR OUTPUT ================\n")
    paras = [p.strip() for p in response['message']['content'].split('\n\n') if p.strip()]
    
    if len(paras) >= 6:
        print("[IMG: yield_curve.png]")
        print(paras[0] + "\n")
        print("[IMG: recession_gauge.png]")
        print(paras[1] + "\n")
        print("[IMG: india_vix.png]")
        print(paras[2] + "\n")
        print(paras[3] + "\n") # Nifty 50 (no image)
        print("[IMG: hyg_spread.png]")
        print(paras[4] + "\n")
        print("[IMG: interbank_rate.png]")
        print("\n\n".join(paras[5:]) + "\n")
    else:
        # Fallback if the agent didn't follow paragraph count
        print("[IMG: yield_curve.png]")
        print("[IMG: recession_gauge.png]")
        print("[IMG: india_vix.png]")
        print("[IMG: hyg_spread.png]")
        print("[IMG: interbank_rate.png]")
        print("\n\n".join(paras))
    print("\n=========================================================")

if __name__ == "__main__":
    run_technical_analysis()