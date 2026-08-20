"""
COMB X .tech | Enterprise Data Pipeline & CRM Synchronization
Description: Secure ETL pipeline that extracts new leads from a secure PostgreSQL 
database, enriches the data using an external API, and pushes the synchronized 
records to a corporate CRM (e.g., Salesforce/HubSpot) while sending Slack alerts.
"""

import os
import json
import requests
import psycopg2
from datetime import datetime

# Configuration (Keys hidden for security)
DB_HOST = "db-prod.combx.tech"
DB_NAME = "enterprise_clients"
DB_USER = "admin_pipeline"
DB_PASS = "****************"
CRM_API_KEY = "crm-api-****************"
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000000/B00000000/****************"

def connect_to_database():
    """Establish secure connection to the production PostgreSQL database."""
    print(f"[{datetime.now()}] [*] Connecting to PostgreSQL database on {DB_HOST}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"[{datetime.now()}] [CRITICAL] Database connection failed: {e}")
        send_slack_alert("CRITICAL: Database connection failed in Pipeline!")
        return None

def fetch_new_leads(conn):
    """Extract unprocessed leads from the database."""
    print(f"[{datetime.now()}] [*] Extracting new leads...")
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name, email, industry FROM leads WHERE processed = FALSE;")
    return cursor.fetchall()

def push_to_crm(lead_data):
    """Push enriched lead data to Enterprise CRM via REST API."""
    headers = {
        "Authorization": f"Bearer {CRM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "company": lead_data[1],
        "contact_email": lead_data[2],
        "sector": lead_data[3],
        "source": "COMB_X_Automation"
    }
    
    # Example API endpoint
    crm_url = "https://api.enterprise-crm.com/v3/objects/contacts"
    
    response = requests.post(crm_url, headers=headers, data=json.dumps(payload))
    return response.status_code == 201

def send_slack_alert(message: str):
    """Send real-time execution alerts to the engineering team."""
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK, json=payload)

def run_pipeline():
    """Main ETL Orchestrator."""
    print(f"=== COMB X .tech | Pipeline Started at {datetime.now()} ===")
    
    db_conn = connect_to_database()
    if not db_conn:
        return

    leads = fetch_new_leads(db_conn)
    print(f"[{datetime.now()}] [*] Found {len(leads)} new leads to process.")
    
    successful_syncs = 0
    
    for lead in leads:
        success = push_to_crm(lead)
        if success:
            # Mark as processed in DB
            cursor = db_conn.cursor()
            cursor.execute("UPDATE leads SET processed = TRUE WHERE id = %s", (lead[0],))
            db_conn.commit()
            successful_syncs += 1
            
    db_conn.close()
    
    summary = f"Pipeline execution complete. Successfully synced {successful_syncs}/{len(leads)} leads to CRM."
    print(f"[{datetime.now()}] [+] {summary}")
    send_slack_alert(summary)

if __name__ == "__main__":
    # Script is typically triggered via Cron or Apache Airflow
    run_pipeline()
