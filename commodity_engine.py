import sys
import yfinance as yf
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from google import genai
import math
import time

# Force UTF-8 so Windows never crashes
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(override=True)
client = genai.Client()

def run_commodity_analysis():
    print("1. Scraping Institutional Commodity Data...")
    
    # 15 Key Commodities
    commodity_tickers = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Copper": "HG=F",
        "Platinum": "PL=F",
        "Palladium": "PA=F",
        "WTI Crude": "CL=F",
        "Brent Crude": "BZ=F",
        "Natural Gas": "NG=F",
        "Wheat": "ZW=F",
        "Corn": "ZC=F",
        "Soybeans": "ZS=F",
        "Sugar": "SB=F",
        "Cotton": "CT=F",
        "Coffee": "KC=F",
        "Cocoa": "CC=F"
    }

    commodity_latest = {}
    metals_energy_data = {}
    agri_data = {}

    try:
        # Batch download drastically reduces YFinance rate limit issues
        tickers_list = list(commodity_tickers.values())
        raw_data = yf.download(tickers_list, period="6mo", progress=False)
        close_prices = raw_data['Close'].dropna(how='all')
    except Exception as e:
        print(f"Error fetching data: {e}")
        close_prices = None

    if close_prices is not None and not close_prices.empty:
        close_prices = close_prices.sort_index()
        for name, ticker in commodity_tickers.items():
            if ticker in close_prices.columns:
                series = close_prices[ticker].dropna()
                if not series.empty:
                    latest = series.iloc[-1]
                    
                    # Compute Returns
                    start_px = series.iloc[0]
                    ret_6m = ((latest / start_px) - 1) * 100
                    
                    if len(series) > 21:
                        px_1m = series.iloc[-21]
                        ret_1m = ((latest / px_1m) - 1) * 100
                    else:
                        ret_1m = 0.0
                    
                    commodity_latest[name] = f"${latest:.2f} (1M: {ret_1m:+.1f}%, 6M: {ret_6m:+.1f}%)"

                    # Charting basis
                    if name in ["Gold", "Copper", "WTI Crude"]:
                        metals_energy_data[name] = (series / series.iloc[0]) * 100
                    elif name in ["Wheat", "Corn", "Soybeans"]:
                        agri_data[name] = (series / series.iloc[0]) * 100
                else:
                    commodity_latest[name] = "N/A"
            else:
                commodity_latest[name] = "N/A"
    else:
        for name in commodity_tickers.keys():
            commodity_latest[name] = "N/A"

    # --- CHART 1: METALS & ENERGY RELATIVE PERFORMANCE ---
    plt.figure(figsize=(7, 4))
    colors = {"Gold": "#fbbf24", "Copper": "#d97706", "WTI Crude": "#0f172a"}
    for name, series in metals_energy_data.items():
        plt.plot(series.index, series, label=name, color=colors[name], linewidth=2)
    plt.title('Metals vs Energy (6-Month Relative Performance)', fontsize=12, fontweight='bold', color='#0f172a')
    plt.ylabel('Normalized (Base = 100)', fontsize=10, color='#334155')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(frameon=False, loc="best")
    plt.gca().set_facecolor('#f8fafc')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig('metals_energy.png', dpi=150, bbox_inches='tight')
    plt.close()

    # --- CHART 2: AGRICULTURAL RELATIVE PERFORMANCE ---
    plt.figure(figsize=(7, 4))
    agri_colors = {"Wheat": "#eab308", "Corn": "#16a34a", "Soybeans": "#84cc16"}
    for name, series in agri_data.items():
        plt.plot(series.index, series, label=name, color=agri_colors[name], linewidth=2)
    plt.title('Agricultural Commodities (6-Month Relative Performance)', fontsize=12, fontweight='bold', color='#0f172a')
    plt.ylabel('Normalized (Base = 100)', fontsize=10, color='#334155')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(frameon=False, loc="best")
    plt.gca().set_facecolor('#f8fafc')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig('agriculture.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("2. Raw commodities secured. Waking up Quantitative Commodity Agent...")

    prompt_data = f"""
    LIVE COMMODITY DATA (Latest Prices with 1M and 6M Returns):
    Precious Metals: Gold={commodity_latest.get('Gold')}, Silver={commodity_latest.get('Silver')}, Platinum={commodity_latest.get('Platinum')}, Palladium={commodity_latest.get('Palladium')}
    Base Metals: Copper={commodity_latest.get('Copper')}
    Energy: WTI Crude={commodity_latest.get('WTI Crude')}, Brent Crude={commodity_latest.get('Brent Crude')}, Natural Gas={commodity_latest.get('Natural Gas')}
    Agriculture (Grains): Wheat={commodity_latest.get('Wheat')}, Corn={commodity_latest.get('Corn')}, Soybeans={commodity_latest.get('Soybeans')}
    Agriculture (Softs): Sugar={commodity_latest.get('Sugar')}, Cotton={commodity_latest.get('Cotton')}, Coffee={commodity_latest.get('Coffee')}, Cocoa={commodity_latest.get('Cocoa')}
    """

    system_prompt = """You are a highly sophisticated, ruthless Quantitative Commodity Analyst.
    Analyze the provided quantitative commodity data aggressively across 15 key global markets. Write exactly four extremely detailed, thorough, highly analytical paragraphs:
    Paragraph 1: Assess Precious & Base Metals - Use the 1M & 6M return percentages supplied to identify structural trend shifts, inflation signals, and macro money flow into safe havens. Provide deep insight.
    Paragraph 2: Assess the Energy Complex - Dig deeply into the pricing shifts over the last month vs 6 months to extract insights on global supply/demand imbalances, geopolitical risk limits, and global growth.
    Paragraph 3: Assess the Grains - Build a macro narrative analyzing yield curves, export dynamics, or geopolitical shocks impacting food security. Be highly specific and informative.
    Paragraph 4: Assess the Soft Commodities - Synthesize specific structural deficits, climate dynamics, or cyclical spikes affecting the softs market. Extrapolate long-term effects.
    CRITICAL: YOU MUST BE EXTREMELY INFORMATIVE! NO BULLET POINTS. NO LISTS. NO ASTERISKS. Write flowing, professional, in-depth paragraphs."""

    user_prompt = f"{prompt_data}\n\nProvide the 4-paragraph commodity macro insight."

    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                )
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[RETRY {attempt+1}/{max_retries}] Gemini API overloaded (503). Waiting 5 seconds before retrying...")
                time.sleep(5)
            else:
                raise e

    print("================ COMMODITY MACRO OUTPUT ================\n")
    paras = [p.strip() for p in response.text.split('\n\n') if p.strip()]
    
    if len(paras) >= 4:
        print("[IMG: metals_energy.png]")
        print(paras[0] + "\n")
        print(paras[1] + "\n")
        print("[IMG: agriculture.png]")
        print(paras[2] + "\n")
        print("\n\n".join(paras[3:]) + "\n")
    else:
        # Fallback if the agent didn't follow paragraph count
        print("[IMG: metals_energy.png]")
        print("[IMG: agriculture.png]")
        print("\n\n".join(paras))
    print("\n=========================================================")

if __name__ == "__main__":
    run_commodity_analysis()
