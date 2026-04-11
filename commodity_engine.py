import sys
import yfinance as yf
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from google import genai
import math

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

    for name, ticker in commodity_tickers.items():
        try:
            data = yf.Ticker(ticker).history(period="6mo")
            if not data.empty:
                commodity_latest[name] = data['Close'].iloc[-1]
                if name in ["Gold", "Copper", "WTI Crude"]:
                    # Normalize for comparative trend line (Base 100)
                    metals_energy_data[name] = (data['Close'] / data['Close'].iloc[0]) * 100
                elif name in ["Wheat", "Corn", "Soybeans"]:
                    agri_data[name] = (data['Close'] / data['Close'].iloc[0]) * 100
            else:
                commodity_latest[name] = "N/A"
        except:
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
    LIVE COMMODITY DATA (Latest Prices):
    Precious Metals: Gold={commodity_latest.get('Gold')}, Silver={commodity_latest.get('Silver')}, Platinum={commodity_latest.get('Platinum')}, Palladium={commodity_latest.get('Palladium')}
    Base Metals: Copper={commodity_latest.get('Copper')}
    Energy: WTI Crude={commodity_latest.get('WTI Crude')}, Brent Crude={commodity_latest.get('Brent Crude')}, Natural Gas={commodity_latest.get('Natural Gas')}
    Agriculture (Grains): Wheat={commodity_latest.get('Wheat')}, Corn={commodity_latest.get('Corn')}, Soybeans={commodity_latest.get('Soybeans')}
    Agriculture (Softs): Sugar={commodity_latest.get('Sugar')}, Cotton={commodity_latest.get('Cotton')}, Coffee={commodity_latest.get('Coffee')}, Cocoa={commodity_latest.get('Cocoa')}
    """

    system_prompt = """You are a ruthless Quantitative Commodity Analyst.
    Analyze the provided commodity data across 15 key global markets. Write exactly four short, highly analytical paragraphs:
    Paragraph 1: Assess Precious & Base Metals (Gold, Silver, Platinum, Palladium, Copper) - What does it signal for inflation, safe-haven demand, and industrial output?
    Paragraph 2: Assess the Energy Complex (Crude types, Natural Gas) - What does the pricing indicate for global supply/demand imbalances or geopolitical risk?
    Paragraph 3: Assess the Grains (Wheat, Corn, Soybeans) - What is the macro narrative surrounding food security, yield pressures, or weather impacts?
    Paragraph 4: Assess the Soft Commodities (Sugar, Cotton, Coffee, Cocoa) - Synthesize specific structural deficits, climate dynamics, or cyclical spikes affecting the softs market.
    CRITICAL: NO BULLET POINTS. NO LISTS. NO ASTERISKS. Write flowing, professional paragraphs."""

    user_prompt = f"{prompt_data}\n\nProvide the 4-paragraph commodity macro insight."

    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
        )
    )

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
