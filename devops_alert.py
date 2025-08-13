from flask import Flask, request
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# === Configure Email ===
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'yourgmail@gmail.com'           # apna Gmail
EMAIL_PASS = 'your_app_password'            # Gmail app password
TO_EMAIL = 'recipient@gmail.com'            # jisko email bhejna hai

# === Function to parse DevOps event JSON ===
def extract_event_info(data):
    user = data.get('user') or data.get('requestedBy') or 'unknown'
    action = data.get('action') or data.get('eventType') or 'unknown'
    project = data.get('project') or data.get('repository') or data.get('pipeline') or 'unknown'
    time = data.get('time') or data.get('createdDate') or 'unknown'
    link = data.get('link') or data.get('url') or ''
    old_approver = data.get('oldApprover', '')
    new_approver = data.get('newApprover', '')
    
    return {
        'user': user,
        'action': action,
        'project': project,
        'time': time,
        'link': link,
        'old_approver': old_approver,
        'new_approver': new_approver
    }

# === Flask endpoint to receive webhook ===
@app.route('/devops-webhook', methods=['POST'])
def devops_webhook():
    data = request.json
    info = extract_event_info(data)

    # Prepare email HTML
    body = f"""
    <h3>🚨 DevOps Alert</h3>
    <p><b>User:</b> {info['user']}</p>
    <p><b>Action:</b> {info['action']}</p>
    <p><b>Project/Repo/Pipeline:</b> {info['project']}</p>
    <p><b>Time:</b> {info['time']}</p>
    """

    if info['old_approver'] or info['new_approver']:
        body += f"<p><b>Old Approver:</b> {info['old_approver']}</p>"
        body += f"<p><b>New Approver:</b> {info['new_approver']}</p>"

    if info['link']:
        body += f"<p><b>Link:</b> <a href='{info['link']}'>{info['link']}</a></p>"

    msg = MIMEText(body, 'html')
    msg['Subject'] = f"DevOps Alert: {info['action']}"
    msg['From'] = EMAIL_USER
    msg['To'] = TO_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
        server.quit()
        return 'Email sent', 200
    except Exception as e:
        return f'Error: {e}', 500

if __name__ == '__main__':
    app.run(port=5000)
