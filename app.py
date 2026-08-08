import smtplib
import socket
import dns.resolver
from flask import Flask, request, jsonify
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

def verify_gmail_account(email):
    # ১. ইমেইল সিনট্যাক্স ও ডোমেইন ফিল্টার
    try:
        valid = validate_email(email, check_deliverability=False)
        email_addr = valid.email.lower()
        domain = email_addr.split('@')[1]
    except EmailNotValidError:
        return "Verify"

    if domain != "gmail.com":
        return "Verify"

    # ২. জিমেইল MX Server বের করা
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)
    except Exception:
        return "Verify"

    # ৩. SMTP Handshake (আসল অ্যাকাউন্ট অস্তিত্ব যাচাই করা)
    try:
        server = smtplib.SMTP(timeout=5)
        server.connect(mx_record, 25)
        server.helo(socket.gethostname())
        server.mail('check@example.com')
        
        # গুগলের কাছে নির্দিষ্ট ইউজার আছে কিনা জিজ্ঞেস করা
        code, message = server.rcpt(email_addr)
        server.quit()

        # গুগল যদি কোড ২৫০ পাঠায়, তার মানে অ্যাকাউন্টটি সচল (Good)
        if code == 250:
            return "Good"
        else:
            return "Verify" # নিষ্ক্রিয়, ইনভ্যালিড বা ব্যানড অ্যাকাউন্ট

    except Exception:
        # কোনো ধরনের সংযোগ বা রেসপন্স সমস্যা হলে Verify
        return "Verify"

@app.route('/check-email', methods=['GET'])
def check_email_api():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "Verify", "email": ""}), 400
    
    result = verify_gmail_account(email)
    return jsonify({
        "email": email,
        "status": result
    })

@app.route('/')
def home():
    return "Gmail Checker Server Alive", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
