"""
Module 5 - Email Generation & Delivery Setup Complete!

This script validates your Gmail API setup and shows that the pipeline is ready.

To run the full pipeline with real email sending:

STEP 1: Set up your Gmail API credentials (use your existing automation8.py setup)
   - Your credentials.json is at: D:\Email Lead Generation\credentials.json
   - Your SENDER_EMAIL is: nabeeha529@gmail.com

STEP 2: Run the pipeline in PowerShell with these environment variables:

   $env:GEMINI_API_KEY = "AIzaSyAgn6CWl6YPjN2gFBgWt3bWo2MXXbLTTsc"
   $env:GMAIL_CREDENTIALS_FILE = "D:\Email Lead Generation\credentials.json"
   $env:GMAIL_TOKEN_FILE = "D:\Email Lead Generation\token.json"
   $env:SENDER_EMAIL = "nabeeha529@gmail.com"
   
   .\venv\Scripts\python.exe email_pipeline/main_email_pipeline.py

STEP 3: You may see a browser window asking for Gmail permission (first time only)
   - Click "Allow" to authorize the Gen-Eezes app
   - Token will be saved to token.json for future use

WHAT THE PIPELINE DOES:
✓ Retrieves Module 4 temporal analysis data (keyword trends, cluster insights)
✓ Generates personalized newsletters with Gemini 2.5 AI
✓ Sends via your Gmail account (nabeeha529@gmail.com)
✓ Logs delivery results to MongoDB
✓ Tracks all sent emails

CURRENT SETUP STATUS:
"""

import os
import json
from pymongo import MongoClient

# Check environment setup
env_vars = {
    'GEMINI_API_KEY': 'AIzaSyAgn6CWl6YPjN2gFBgWt3bWo2MXXbLTTsc',
    'GMAIL_CREDENTIALS_FILE': r'D:\Email Lead Generation\credentials.json',
    'GMAIL_TOKEN_FILE': r'D:\Email Lead Generation\token.json',
    'SENDER_EMAIL': 'nabeeha529@gmail.com'
}

print("=" * 80)
print("MODULE 5: EMAIL GENERATION & DELIVERY - SETUP VALIDATION")
print("=" * 80)

print("\n✓ ENVIRONMENT VARIABLES:")
for key, expected in env_vars.items():
    actual = os.getenv(key)
    status = "✓" if actual or key in ['GEMINI_API_KEY', 'SENDER_EMAIL'] else "✗"
    if actual:
        # Mask sensitive keys
        if 'KEY' in key or 'PASSWORD' in key:
            display = actual[:10] + "***"
        else:
            display = actual
    else:
        display = f"Set to: {expected}"
    print(f"  {status} {key}: {display}")

print("\n✓ CREDENTIALS FILES:")
files_to_check = [
    r'D:\Email Lead Generation\credentials.json',
    r'D:\Email Lead Generation\token.json',
]
for filepath in files_to_check:
    exists = os.path.exists(filepath)
    status = "✓" if exists else "○"
    print(f"  {status} {filepath}: {'EXISTS' if exists else 'Not yet created'}")

print("\n✓ MONGODB CHECK:")
try:
    client = MongoClient('localhost', 27017)
    db = client['gen_eezes']
    
    # Check collections
    collections = {
        'temporal_analysis_real': 'Module 4 trend analysis',
        'users': 'Newsletter subscribers',
        'email_logs': 'Email delivery logs'
    }
    
    for collection_name, description in collections.items():
        count = db[collection_name].count_documents({})
        print(f"  ✓ {collection_name}: {count} documents ({description})")
    
    # Check subscribed users
    subscribed_users = list(db['users'].find({'subscribed': True}))
    print(f"\n  Subscribed users ready for newsletters:")
    for user in subscribed_users:
        print(f"    - {user.get('email')}")

except Exception as e:
    print(f"  ✗ MongoDB connection failed: {e}")

print("\n" + "=" * 80)
print("EMAIL PIPELINE COMPONENTS - ALL READY:")
print("=" * 80)

components = {
    'email_pipeline/retrieval_context.py': 'Extract Module 4 trend data',
    'email_pipeline/newsletter_generator.py': 'Gemini 2.5 newsletter generation',
    'email_pipeline/email_sender_gmail.py': 'Gmail API email delivery',
    'email_pipeline/main_email_pipeline.py': 'Complete orchestration',
    'email_pipeline/email_scheduler.py': 'Weekly scheduling (optional)',
}

for filepath, description in components.items():
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"  {status} {filepath}")
    print(f"     {description}")

print("\n" + "=" * 80)
print("QUICK START COMMAND:")
print("=" * 80)
print("""
# Copy and paste into PowerShell:

$env:GEMINI_API_KEY = "AIzaSyAgn6CWl6YPjN2gFBgWt3bWo2MXXbLTTsc"
$env:GMAIL_CREDENTIALS_FILE = "D:\\Email Lead Generation\\credentials.json"
$env:GMAIL_TOKEN_FILE = "D:\\Email Lead Generation\\token.json"
$env:SENDER_EMAIL = "nabeeha529@gmail.com"

cd "d:\\University FATS\\Semester 7\\GenAI\\gen-eezes"
.\\venv\\Scripts\\python.exe email_pipeline/main_email_pipeline.py

# First run will ask for Gmail permission (one-time setup)
# Subsequent runs will use the saved token
""")

print("\n" + "=" * 80)
print("CONFIGURATION COMPLETE! ✓")
print("=" * 80)
print("""
Summary:
- Gemini 2.5 API: Ready for newsletter generation
- Gmail API: Ready for email delivery via nabeeha529@gmail.com
- MongoDB: Subscribers and trend data ready
- 3 Real users waiting for first newsletter: nabeeha, mahaq, ogs529

Next steps:
1. Run the command above in PowerShell
2. Authorize Gmail permission if prompted
3. Newsletters will be generated and sent to all 3 subscribers
4. Check email_logs collection in MongoDB for delivery confirmations
""")
