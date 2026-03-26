import os
import sys
import subprocess
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def execute_engine(script_name):
    print(f"Triggering {script_name}...")
    try:
        # We force UTF-8 encoding so the Rupee symbol (₹) and other special characters don't crash Windows
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="replace", 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"CRITICAL FAILURE IN {script_name}:\n{e.stderr}"

def parse_to_html(raw_text):
    """Converts terminal markdown and sentiment into styled HTML components."""
    # 1. Replace the ugly ======== dividers with sleek corporate section headers
    clean = re.sub(r'={5,}\s*(.*?)\s*={5,}', r'<div class="section-divider">\1</div>', raw_text)
    
    # 2. Convert Markdown bold (**text**) to HTML bold with dark color
    clean = re.sub(r'\*\*(.*?)\*\*', r'<span class="highlight">\1</span>', clean)
    
    # 3. Convert Markdown bullets (* text) into actual HTML list items with custom blue bullets
    clean = re.sub(r'^\s*\*\s+(.*)', r'<div class="custom-bullet">\1</div>', clean, flags=re.MULTILINE)
    
    # 4. Colorize Quant Sentiment (Green/Red/Gray tags)
    clean = clean.replace('NET ACCUMULATION (BULLISH)', '<span class="bullish">NET ACCUMULATION (BULLISH)</span>')
    clean = clean.replace('NET DISTRIBUTION (BEARISH)', '<span class="bearish">NET DISTRIBUTION (BEARISH)</span>')
    clean = clean.replace('NET NEUTRAL (MARKET MAKING)', '<span class="neutral">NET NEUTRAL (MARKET MAKING)</span>')
    
    return clean

def compile_and_send_brief():
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("[ERROR] Credentials missing. Check your .env file.")
        return

    today_date = datetime.now().strftime("%B %d, %Y")
    print(f"Initiating Master Pipeline for {today_date}...\n")
    
    # Run the engines
    raw_macro = execute_engine("rag_pipeline.py")
    raw_liquidity = execute_engine("nse_flow_tracker.py")
    raw_risk = execute_engine("macro_indicators.py")
    
    print("\nAll engines executed. Parsing Markdown to HTML...")

    # Pass the raw text through our new Regex formatting engine
    macro_intel = parse_to_html(raw_macro)
    liquidity_flow = parse_to_html(raw_liquidity)
    portfolio_risk = parse_to_html(raw_risk)

    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; padding: 20px; }}
                .container {{ background-color: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); max-width: 800px; margin: auto; border: 1px solid #e2e8f0; }}
                
                h2 {{ color: #0f172a; border-bottom: 2px solid #2563eb; padding-bottom: 15px; font-size: 24px; margin-bottom: 30px; font-weight: 800; letter-spacing: -0.5px; }}
                h3 {{ color: #1e3a8a; margin-top: 40px; font-size: 15px; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 700; display: flex; align-items: center; }}
                
                /* The main text containers */
                .content-block {{ background-color: #ffffff; color: #475569; padding: 5px 15px 15px 15px; border-radius: 8px; font-size: 14px; white-space: pre-wrap; line-height: 1.6; }}
                
                /* Parsed Elements Styling */
                .section-divider {{ font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; margin: 25px 0 10px 0; border-bottom: 1px dashed #e2e8f0; padding-bottom: 5px; }}
                .highlight {{ color: #0f172a; font-weight: 700; }}
                .custom-bullet {{ margin-left: 15px; margin-bottom: 6px; position: relative; display: block; }}
                .custom-bullet::before {{ content: "■"; color: #3b82f6; font-size: 10px; position: absolute; left: -15px; top: 3px; }}
                
                /* Quant Sentiment Tags */
                .bullish {{ color: #15803d; font-weight: 700; background: #dcfce7; padding: 2px 8px; border-radius: 4px; border: 1px solid #bbf7d0; font-size: 12px; }}
                .bearish {{ color: #b91c1c; font-weight: 700; background: #fee2e2; padding: 2px 8px; border-radius: 4px; border: 1px solid #fecaca; font-size: 12px; }}
                .neutral {{ color: #475569; font-weight: 700; background: #f1f5f9; padding: 2px 8px; border-radius: 4px; border: 1px solid #e2e8f0; font-size: 12px; }}
                
                .footer {{ margin-top: 50px; font-size: 12px; color: #94a3b8; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Quantitative Executive Brief <span style="color: #94a3b8; font-weight: 400; font-size: 18px;">| {today_date}</span></h2>
                
                <h3>1. Global Macro & Systemic Risk</h3>
                <div class="content-block">{macro_intel}</div>
                
                <h3>2. Market Liquidity & Institutional Flow</h3>
                <div class="content-block">{liquidity_flow}</div>
                
                <h3>3. Leading Indicators & Global Correlation</h3>
                <div class="content-block">{portfolio_risk}</div>
                
                <div class="footer">
                    <strong>Autonomous Quantitative Architecture</strong><br>
                    Localized LLM Inference • NSE FII/DII Data Streams
                </div>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"EXECUTIVE BRIEF: Institutional Market Flow ({today_date})"
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("\n[SUCCESS] Executive Brief successfully delivered to inbox.")
    except Exception as e:
        print(f"\n[ERROR] Failed to send email: {e}")

if __name__ == "__main__":
    compile_and_send_brief()