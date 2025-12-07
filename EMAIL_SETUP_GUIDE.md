"""
EMAIL DOMAIN SETUP GUIDE FOR GEN-EEZES

This guide explains how to set up email sending from your own domain.

Options:
1. Gmail with App Password (Easiest, recommended for testing)
2. Your Domain Email + SMTP Provider (Production recommended)
3. SendGrid / Mailgun / AWS SES (Professional services)
"""

# ============================================================================
# OPTION 1: GMAIL WITH APP PASSWORD (Easiest - 5 minutes)
# ============================================================================

"""
PREREQUISITES:
- Google Account
- 2-Factor Authentication enabled on your Google Account

STEPS:

1. Enable 2-Factor Authentication on Google Account:
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow the prompts to enable 2FA

2. Create App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your device)
   - Google will generate a 16-character password
   - Copy this password - you'll use it as SENDER_PASSWORD

3. Set Environment Variables:
   
   On Windows PowerShell (temporary - session only):
   ```powershell
   $env:SENDER_EMAIL = "your-email@gmail.com"
   $env:SENDER_PASSWORD = "your-16-char-app-password"
   ```
   
   On Windows PowerShell (permanent - add to profile):
   ```powershell
   # Edit your PowerShell profile
   notepad $PROFILE
   
   # Add these lines:
   $env:SENDER_EMAIL = "your-email@gmail.com"
   $env:SENDER_PASSWORD = "your-16-char-app-password"
   ```
   
   On Windows CMD:
   ```cmd
   setx SENDER_EMAIL "your-email@gmail.com"
   setx SENDER_PASSWORD "your-16-char-app-password"
   ```

4. SMTP Configuration (already set in code):
   - SMTP Server: smtp.gmail.com
   - SMTP Port: 587
   - Use TLS: Yes

5. Run the Pipeline:
   ```powershell
   cd "d:\University FATS\Semester 7\GenAI\gen-eezes"
   .\venv\Scripts\python.exe email_pipeline/email_sender.py
   ```

PROS:
✓ Free
✓ Quick setup
✓ Reliable
✓ No domain needed
✓ Good for testing/development

CONS:
✗ Google Account tied to newsletters
✗ May hit Gmail's sending limits (300 emails/day)
✗ Recipients may see your Gmail address
"""

# ============================================================================
# OPTION 2: CUSTOM DOMAIN EMAIL (Professional)
# ============================================================================

"""
STEP-BY-STEP SETUP FOR YOUR OWN DOMAIN:

Prerequisites:
- Registered domain (e.g., yourcompany.com from GoDaddy, Namecheap, etc.)
- Domain registrar access
- SMTP provider account (see list below)

SUBSTEP A: Choose an SMTP Provider

Option A1: Your Domain Host's Email Service (if available)
   Example: If you use GoDaddy:
   - GoDaddy Workspace Email
   - SMTP: smtp.office365.com (for Microsoft)
   - SMTP: mail.yourcompany.com (for GoDaddy)

Option A2: Professional Email Hosting Services:

   **Recommended: Microsoft Office 365 / Outlook Business**
   - Cost: ~$6/user/month
   - SMTP: smtp.office365.com
   - Port: 587 (TLS) or 25 (unencrypted)
   - Setup: Sign up at office.com
   - Steps:
     1. Buy domain or connect existing domain
     2. Add users (yourname@yourdomain.com)
     3. Enable IMAP/SMTP in settings
     4. Use credentials to set environment variables

   **Alternative: Google Workspace**
   - Cost: ~$6-18/user/month
   - SMTP: smtp.gmail.com
   - Port: 587
   - Setup: 
     1. Go to https://workspace.google.com
     2. Sign up, connect your domain
     3. Add users
     4. Create app passwords like Option 1

   **Alternative: Zoho Mail (Free tier available)**
   - Cost: Free up to 5 users, then $1-5/user/month
   - SMTP: smtp.zoho.com
   - Port: 587 or 465
   - Setup: https://www.zoho.com/mail

   **For High Volume: SendGrid / Mailgun**
   - Mailgun: 100 free emails/day, then paid
   - SendGrid: 100 free emails/day
   - These are NOT traditional email hosts, but transactional email services
   - See Option 3 below

SUBSTEP B: Configure Your Domain's MX Records

Once you choose a provider, you need to point your domain to their mail servers:

1. Log into your domain registrar (GoDaddy, Namecheap, etc.)
2. Find DNS Settings or DNS Management
3. Find or create MX (Mail Exchange) Records
4. Add the MX records provided by your email provider

Example for Microsoft 365:
   MX Record Priority 10: yourcompany-com.mail.protection.outlook.com

Example for Google Workspace:
   MX Record Priority 10: aspmx.l.google.com
   MX Record Priority 20: alt1.aspmx.l.google.com
   (Additional records needed - provider will show all)

5. Wait 24-48 hours for DNS to propagate

SUBSTEP C: Create Email User Account

In your email provider's admin panel:
1. Create user: newsletter@yourdomain.com (or newsletters@, noreply@, etc.)
2. Set password
3. Optional: Enable "App Password" if available (like Gmail)

SUBSTEP D: Set Environment Variables

On Windows PowerShell:
```powershell
$env:SENDER_EMAIL = "newsletter@yourdomain.com"
$env:SENDER_PASSWORD = "your-email-password"
$env:SMTP_SERVER = "smtp.office365.com"  # or smtp.gmail.com, smtp.zoho.com, etc.
$env:SMTP_PORT = "587"

# Test with:
.\venv\Scripts\python.exe email_pipeline/email_sender.py
```

SUBSTEP E: Test Email Sending

```python
from email_pipeline.email_sender import EmailSender

sender = EmailSender()
success, message = sender.send_test_email("your-personal-email@gmail.com")
print(f"Test email: {message}")
```
"""

# ============================================================================
# OPTION 3: TRANSACTIONAL EMAIL SERVICES (Best for Production)
# ============================================================================

"""
For HIGH VOLUME email delivery (1000+ emails/month), consider:

MAILGUN (Recommended - Free tier generous)
- Cost: Free 100 emails/day, then $0.50 per 1000 emails
- Setup: https://www.mailgun.com
- SMTP Details:
  Server: smtp.mailgun.org
  Port: 587
  Username: postmaster@your-domain-mg.mailgun.org
  Password: API key from Mailgun
  
- Steps:
  1. Sign up
  2. Add your domain (yourdomain.com or subdomain)
  3. Verify domain with DNS records (simpler than full email setup)
  4. Copy SMTP credentials
  5. Set environment variables

SENDGRID
- Cost: Free 100 emails/day, then paid
- Setup: https://sendgrid.com
- SMTP Details:
  Server: smtp.sendgrid.net
  Port: 587
  Username: apikey
  Password: Your SG API key

AWS SES (Simple Email Service)
- Cost: $0.10 per 1000 emails (cheap!)
- Setup: Requires AWS account
- Server: email-smtp.region.amazonaws.com
- More complex setup but very scalable

POSTMARK
- Cost: $0.75 per 1000 emails
- Server: smtp.postmarkapp.com
- Port: 2525 or 587
"""

# ============================================================================
# QUICK COMPARISON TABLE
# ============================================================================

"""
┌──────────────────┬────────────┬──────────┬────────────┬─────────────┐
│ Provider         │ Cost       │ Setup    │ Reputation │ Use Case    │
├──────────────────┼────────────┼──────────┼────────────┼─────────────┤
│ Gmail + App Pass │ Free       │ 5 min    │ Excellent  │ Testing     │
│ Office 365       │ $6/month   │ 1 hour   │ Excellent  │ Professional│
│ Google Workspace │ $6/month   │ 1 hour   │ Excellent  │ Professional│
│ Zoho Mail        │ Free-$5    │ 30 min   │ Very Good  │ Small Bus   │
│ Mailgun          │ Free-cheap │ 30 min   │ Very Good  │ Transactional
│ SendGrid         │ Free-cheap │ 30 min   │ Excellent  │ Transactional
│ AWS SES          │ Very cheap │ Complex  │ Excellent  │ High Vol    │
└──────────────────┴────────────┴──────────┴────────────┴─────────────┘

RECOMMENDATION:
- For testing now: Gmail App Password (OPTION 1) ✓
- For production: Office 365 or Google Workspace (OPTION 2) with your domain
- For high volume: Mailgun or SendGrid (OPTION 3)
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Problem: "SMTP Authentication failed"
Solution: Check environment variables are set correctly
  - Check email is correct
  - Check password is correct (not your Gmail password if using App Password)
  - Verify SMTP server is correct

Problem: "Connection refused on port 587"
Solution: 
  - Provider might require port 25 or 465 instead
  - Some networks block port 587 (corporate firewall)
  - Try different port or contact provider

Problem: "Sending limit exceeded"
Solution:
  - Gmail limits ~300 emails/day
  - Office 365 limits vary by plan
  - Use SendGrid/Mailgun for higher volume

Problem: "Emails sent but going to spam"
Solution:
  - Add SPF record: v=spf1 include:provider.com ~all
  - Add DKIM record (provided by your email provider)
  - Add DMARC record: v=DMARC1; p=none
  - These go in your domain's DNS settings
  - Takes 24-48 hours to propagate
"""

# ============================================================================
# COMMANDS TO TEST YOUR SETUP
# ============================================================================

"""
After setting environment variables, test with:

1. Check environment variables are set:
   ```powershell
   echo $env:SENDER_EMAIL
   echo $env:SENDER_PASSWORD
   ```

2. Run email sender test:
   ```powershell
   cd "d:\University FATS\Semester 7\GenAI\gen-eezes"
   .\venv\Scripts\python.exe email_pipeline/email_sender.py
   ```

3. Send test email to yourself:
   ```powershell
   $env:GEMINI_API_KEY = "AIzaSyAgn6CWl6YPjN2gFBgWt3bWo2MXXbLTTsc"
   $env:SENDER_EMAIL = "your-email@domain.com"
   $env:SENDER_PASSWORD = "your-password"
   .\venv\Scripts\python.exe -c "
from email_pipeline.email_sender import EmailSender
sender = EmailSender()
success, msg = sender.send_test_email('your-test-email@gmail.com')
print(f'✓ {msg}' if success else f'✗ {msg}')
   "
   ```

4. Run full pipeline:
   ```powershell
   .\venv\Scripts\python.exe email_pipeline/main_email_pipeline.py
   ```

5. View sent emails log:
   ```powershell
   cat pipeline_execution_log.json | ConvertFrom-Json | ForEach-Object { $_ }
   ```
"""

# ============================================================================
# RECOMMENDED PATH FOR YOU
# ============================================================================

"""
Based on your setup, here's what I recommend:

STEP 1 (NOW - for testing): Use Gmail App Password
  - Quickest way to test everything works
  - Takes 5 minutes
  - Perfect for validating the full pipeline

STEP 2 (LATER - for production): Get a professional domain
  
  Option A: Simple way
  - Keep your Gmail but create a custom domain
  - Use Google Workspace (same interface as Gmail)
  - Cost: $6/month
  - Setup: 30 minutes
  - Can send from: newsletter@yourdomain.com
  - Recipients see professional domain instead of Gmail
  
  Option B: Advanced way
  - Use Office 365 with your custom domain
  - Professional email hosting
  - Cost: $6/month for basic
  - More features than Google Workspace

STEP 3 (HIGH VOLUME): Switch to Mailgun/SendGrid if needed
  - Only if you exceed limits of your email host
  - No domain complications
  - Designed for newsletters

WHICH ONE DO YOU HAVE?
- Just a Gmail account? → Use Option 1 (Gmail App Password)
- Own domain but no email? → Use Option 2A (Google Workspace)
- Own domain + business email? → Use your existing email provider's SMTP
- Want to scale to 10k+ emails? → Use Option 3 (Mailgun/SendGrid)
"""
