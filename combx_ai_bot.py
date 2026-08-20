COMB X .tech | Autonomous AI Automation Bot
Description: Enterprise-grade script for scraping business websites, 
analyzing pain points using LLMs (GPT-4o), and sending hyper-personalized outreach.
"""

import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Configuration & Security (Keys hidden for security)
OPENAI_API_KEY = "sk-proj-**********************************"
SMTP_SERVER = "server422.hosting.reg.ru"
SMTP_PORT = 465
SMTP_USER = "info@combx.tech"
SMTP_PASS = "****************"

client = OpenAI(api_key=OPENAI_API_KEY)

def scrape_website(url: str) -> str:
    """Scrape and clean text content from target business website."""
    print(f"[*] Scraping target: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True) 
        return text[:3000] # Return first 3000 chars for LLM analysis
    except Exception as e:
        print(f"[!] Scraping failed: {e}")
        return ""

def generate_ai_pitch(business_data: str) -> dict:
    """Use GPT-4o-mini to analyze business data and generate a personalized pitch."""
    print("[*] Generating AI analysis and pitch...")
    
    system_prompt = """
    You are an expert B2B Automation Consultant. Analyze the provided website text.
    Identify process bottlenecks. Generate a highly personalized email proposing 
    an AI or Automation solution that cuts costs or saves time for this specific business.
    Return JSON format: {"subject": "...", "body": "..."}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Website Data: {business_data}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    
    return json.loads(response.choices[0].message.content)

def send_secure_email(target_email: str, subject: str, body: str):
    """Send outreach email via secure SSL SMTP relay."""
    msg = MIMEMultipart()
    msg['From'] = f"Alex | COMB X .tech <{SMTP_USER}>"
    msg['To'] = target_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        print(f"[*] Sending secure email to {target_email}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print("[+] Email successfully delivered.")
    except Exception as e:
        print(f"[!] SMTP Error: {e}")

def run_automation_pipeline(target_url: str, target_email: str):
    """Main Orchestrator."""
    print("=== COMB X .tech | Initialization ===")
    
    # Step 1: Scrape
    website_text = scrape_website(target_url)
    
    # Step 2: AI Processing
    if website_text:
        ai_result = generate_ai_pitch(website_text)
        
        # Step 3: Delivery
        if "subject" in ai_result and "body" in ai_result:
            send_secure_email(target_email, ai_result["subject"], ai_result["body"])
            
    print("=== Pipeline Complete ===")

if __name__ == "__main__":
    # Example execution (Data pulled from CRM in production)
    run_automation_pipeline("https://example-client.com", "director@example-client.com")
