import smtplib
import socket
import dns.resolver
from flask import Flask, request, jsonify
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

def check_gmail_status(email):
    # ১. ফরম্যাট যাচাই
    try:
        valid = validate_email(email, check_deliverability=False)
        email_addr = valid.email
        domain = email_addr.split('@')[1]
    except EmailNotValidError:
        return "Verify"

    if domain != "gmail.com":
        return "Verify"

    # ২. MX Record বের করা
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)
    except Exception:
        return "Verify"

    # ৩. SMTP দিয়ে জিমেইল সচল নাকি নিষ্ক্রিয় চেক করা
    try:
        server = smtplib.SMTP(timeout=8)
        server.connect(mx_record)
        server.helo(socket.gethostname())
        server.mail("test@example.com")
        code, message = server.rcpt(email_addr)
        server.quit()

        if code == 250:
            return "Good"
        else:
            return "Verify"
    except Exception:
        return "Verify"

# API Route
@app.route('/check-email', methods=['GET'])
def check_email_api():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "Error", "message": "Email parameter is missing"}), 400
    
    result = check_gmail_status(email)
    return jsonify({
        "email": email,
        "status": result
    })

# Render-এর হেলথ চেক রুট (UptimeRobot-এর জন্য)
@app.route('/')
def home():
    return "Server is Running!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
