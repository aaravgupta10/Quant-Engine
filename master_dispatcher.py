import os
import sys
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load the hidden variables from the .env file
load_dotenv()

# --- CONFIGURATION (SECURED) ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
# -------------------------------

def execute_engine(script_name):
    print(f"Triggering {script_name}...")
    try:
        # sys.executable FORCES the child process to stay inside the active venv
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"CRITICAL FAILURE IN {script_name}:\n{e.stderr}"

def compile_and_send_brief():
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("[ERROR] Credentials missing. Check your .env file.")
        return

    today_date = datetime.now().strftime("%B %d, %Y")
    print(f"Initiating Master Pipeline for {today_date}...\n")
    
    macro_intel = execute_engine("rag_pipeline.py")
    liquidity_flow = execute_engine("nse_flow_tracker.py")
    portfolio_risk = execute_engine("risk_hedger.py")
    
    print("\nAll engines executed. Compiling Executive HTML Report...")

    # 2. Build the HTML Email (Clean, Institutional Corporate Aesthetic)
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f5f7; color: #111827; padding: 20px; line-height: 1.6; }}
                .container {{ background-color: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); max-width: 850px; margin: auto; border: 1px solid #e5e7eb; }}
                h2 {{ color: #0f172a; border-bottom: 3px solid #2563eb; padding-bottom: 12px; font-size: 26px; margin-bottom: 30px; letter-spacing: -0.5px; }}
                h3 {{ color: #1e40af; margin-top: 35px; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }}
                .content-block {{ 
                    background-color: #f8fafc; 
                    color: #334155; 
                    padding: 20px 25px; 
                    border-radius: 8px; 
                    border-left: 4px solid #3b82f6; 
                    font-family: 'Segoe UI', system-ui, sans-serif; 
                    font-size: 14px; 
                    white-space: pre-wrap; 
                    margin-top: 15px;
                    line-height: 1.7;
                }}
                .footer {{ margin-top: 45px; font-size: 12px; color: #94a3b8; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 20px; }}
                .highlight {{ font-weight: bold; color: #0f172a; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Quantitative Executive Brief <span style="color: #64748b; font-size: 18px; font-weight: normal;">| {today_date}</span></h2>
                
                <h3>1. Global Macro & Systemic Risk</h3>
                <div class="content-block">{macro_intel}</div>
                
                <h3>2. Market Liquidity & Institutional Flow</h3>
                <div class="content-block">{liquidity_flow}</div>
                
                <h3>3. Localized Portfolio Risk Assessment</h3>
                <div class="content-block">{portfolio_risk}</div>
                
                <div class="footer">
                    Automated Quantitative Architecture • Localized LLM Inference<br>
                    Data extracted from NSE India and DDGS Syndication.
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
        print("Authenticating with Google SMTP server...")
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