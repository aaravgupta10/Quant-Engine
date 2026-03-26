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

    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; color: #333; padding: 20px; }}
                .container {{ background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }}
                h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h3 {{ color: #34495e; margin-top: 25px; }}
                pre {{ background-color: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Consolas', monospace; font-size: 13px; line-height: 1.4; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #7f8c8d; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Quantitative Executive Brief - {today_date}</h2>
                
                <h3>1. Global Macro & Systemic Risk (RAG Vault)</h3>
                <pre>{macro_intel}</pre>
                
                <h3>2. Market Liquidity & FII/DII Flow</h3>
                <pre>{liquidity_flow}</pre>
                
                <h3>3. Localized Portfolio Risk & Hedging</h3>
                <pre>{portfolio_risk}</pre>
                
                <div class="footer">
                    Generated automatically by the Local Llama Quant Architecture.<br>
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