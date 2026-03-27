import os
import sys
import subprocess
import smtplib
import re
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def execute_engine(script_name):
    """Executes a child script and captures output using UTF-8 to prevent Windows crashes."""
    print(f"Triggering {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"CRITICAL FAILURE IN {script_name}:\n{e.stderr}"

def parse_to_html(raw_text):
    """Refines raw terminal output into institutional-grade HTML."""
    # 1. Strip ugly terminal dividers
    clean = re.sub(r'={5,}\s*(.*?)\s*={5,}', r'<div class="section-divider">\1</div>', raw_text)
    
    # 2. Convert Markdown bold to high-contrast spans
    clean = re.sub(r'\*\*(.*?)\*\*', r'<span class="highlight">\1</span>', clean)
    
    # 3. Convert Markdown bullets to styled square markers
    clean = re.sub(r'^\s*\*\s+(.*)', r'<div class="custom-bullet">\1</div>', clean, flags=re.MULTILINE)
    
    # 4. Inject dynamic sentiment badges
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
    
    # --- PHASE 1: EXECUTION ---
    raw_macro = execute_engine("rag_pipeline.py")
    raw_liquidity = execute_engine("nse_flow_tracker.py")
    raw_indicators = execute_engine("macro_indicators.py")
    raw_technical = execute_engine("technical_engine.py") # New Section 4 Script
    
    print("\nAll engines executed. Finalizing Multimodal Assembly...")

    # --- PHASE 2: PARSING ---
    macro_intel = parse_to_html(raw_macro)
    liquidity_flow = parse_to_html(raw_liquidity)
    macro_indicators = parse_to_html(raw_indicators)
    technical_insights = parse_to_html(raw_technical)

    # --- PHASE 3: IMAGE ENCODING ---
    img_tag = '<img src="cid:yield_curve_img" style="max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px; display: block; margin-top: 20px;">' if os.path.exists("yield_curve.png") else ''
    recession_tag = '<img src="cid:recession_gauge_img" style="max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px; display: block; margin-top: 20px;">' if os.path.exists("recession_gauge.png") else ''
    vix_tag = '<img src="cid:india_vix_img" style="max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px; display: block; margin-top: 20px;">' if os.path.exists("india_vix.png") else ''
    hyg_tag = '<img src="cid:hyg_spread_img" style="max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px; display: block; margin-top: 20px;">' if os.path.exists("hyg_spread.png") else ''
    interbank_tag = '<img src="cid:interbank_rate_img" style="max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px; display: block; margin-top: 20px;">' if os.path.exists("interbank_rate.png") else ''

    # Injecting interleaved images
    technical_insights = technical_insights.replace("[IMG: yield_curve.png]", img_tag)
    technical_insights = technical_insights.replace("[IMG: recession_gauge.png]", recession_tag)
    technical_insights = technical_insights.replace("[IMG: india_vix.png]", vix_tag)
    technical_insights = technical_insights.replace("[IMG: hyg_spread.png]", hyg_tag)
    technical_insights = technical_insights.replace("[IMG: interbank_rate.png]", interbank_tag)

    # --- PHASE 4: HTML CONSTRUCTION ---
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; padding: 20px; }}
                .container {{ background-color: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); max-width: 800px; margin: auto; border: 1px solid #e2e8f0; }}
                h2 {{ color: #0f172a; border-bottom: 2px solid #2563eb; padding-bottom: 15px; font-size: 24px; margin-bottom: 30px; font-weight: 800; letter-spacing: -0.5px; }}
                h3 {{ color: #1e3a8a; margin-top: 40px; font-size: 15px; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 700; }}
                .content-block {{ color: #475569; padding: 5px 15px; border-radius: 8px; font-size: 14px; white-space: pre-wrap; line-height: 1.6; }}
                .section-divider {{ font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; margin: 25px 0 10px 0; border-bottom: 1px dashed #e2e8f0; padding-bottom: 5px; }}
                .highlight {{ color: #0f172a; font-weight: 700; }}
                .custom-bullet {{ margin-left: 15px; margin-bottom: 6px; position: relative; display: block; }}
                .custom-bullet::before {{ content: "■"; color: #3b82f6; font-size: 10px; position: absolute; left: -15px; top: 3px; }}
                .bullish {{ color: #15803d; font-weight: 700; background: #dcfce7; padding: 2px 8px; border-radius: 4px; border: 1px solid #bbf7d0; font-size: 11px; }}
                .bearish {{ color: #b91c1c; font-weight: 700; background: #fee2e2; padding: 2px 8px; border-radius: 4px; border: 1px solid #fecaca; font-size: 11px; }}
                .neutral {{ color: #475569; font-weight: 700; background: #f1f5f9; padding: 2px 8px; border-radius: 4px; border: 1px solid #e2e8f0; font-size: 11px; }}
                .footer {{ margin-top: 50px; font-size: 11px; color: #94a3b8; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 20px; }}
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
                <div class="content-block">{macro_indicators}</div>

                <h3>4. Systemic Fear & Technical Anchors</h3>
                <div class="content-block">
                    {technical_insights}
                </div>
                
                <div class="footer">
                    <strong>Autonomous Quantitative Architecture</strong><br>
                    Localized LLM Inference • Live Market Telemetry
                </div>
            </div>
        </body>
    </html>
    """

    # --- PHASE 5: DELIVERY ---
    msg = MIMEMultipart('related')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"EXECUTIVE BRIEF: Institutional Market Flow ({today_date})"
    
    msg_alt = MIMEMultipart('alternative')
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(html_content, 'html'))

    if os.path.exists("yield_curve.png"):
        with open("yield_curve.png", "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<yield_curve_img>')
            img.add_header('Content-Disposition', 'inline', filename='yield_curve.png')
            msg.attach(img)
            
    if os.path.exists("india_vix.png"):
        with open("india_vix.png", "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<india_vix_img>')
            img.add_header('Content-Disposition', 'inline', filename='india_vix.png')
            msg.attach(img)

    if os.path.exists("recession_gauge.png"):
        with open("recession_gauge.png", "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<recession_gauge_img>')
            img.add_header('Content-Disposition', 'inline', filename='recession_gauge.png')
            msg.attach(img)

    if os.path.exists("hyg_spread.png"):
        with open("hyg_spread.png", "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<hyg_spread_img>')
            img.add_header('Content-Disposition', 'inline', filename='hyg_spread.png')
            msg.attach(img)

    if os.path.exists("interbank_rate.png"):
        with open("interbank_rate.png", "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<interbank_rate_img>')
            img.add_header('Content-Disposition', 'inline', filename='interbank_rate.png')
            msg.attach(img)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"\n[SUCCESS] Executive Brief ({today_date}) delivered to inbox.")
    except Exception as e:
        print(f"\n[ERROR] Delivery failed: {e}")

if __name__ == "__main__":
    compile_and_send_brief()