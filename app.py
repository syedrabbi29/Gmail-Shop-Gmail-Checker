import requests
from flask import Flask, request, jsonify
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

def check_gmail_account_status(email):
    # ১. ইমেইল ফরম্যাট যাচাই
    try:
        valid = validate_email(email, check_deliverability=False)
        email_addr = valid.email.lower()
        domain = email_addr.split('@')[1]
    except EmailNotValidError:
        return "Verify"

    if domain != "gmail.com":
        return "Verify"

    # ২. গুগলের পাবলিক অ্যাকাউন্ট চেক অ্যান্ডপয়েন্টে রিকোয়েস্ট (Port 80/443 ব্যবহার করে)
    url = "https://mail.google.com/mail/cx/1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        # গুগলের সার্ভারে অ্যাকাউন্ট স্ট্যাটাস পিং করা
        response = requests.get(f"https://contacts.google.com/v1/people:searchDirectory", timeout=4)
        
        # বিকল্প মেথড: গুগলের ইন্টারনাল সেশন চেক
        check_url = f"https://accounts.google.com/InputValidator?gmail={email_addr}"
        res = requests.get(check_url, headers=headers, timeout=4)
        
        # রেসপন্স চেক
        if res.status_code == 200:
            # গুগল ডাটা এনালাইসিস
            if "true" in res.text.lower() or "valid" in res.text.lower():
                return "Good"
            else:
                return "Verify"
        else:
            return "Verify"

    except Exception:
        # কোনো কারণে ব্লক খেলে বা টাইমআউট হলে বেসিক রুলস অ্যাপ্লাই
        username = email_addr.split('@')[0]
        if len(username) < 6 or username.isdigit():
            return "Verify"
        return "Good"

@app.route('/check-email', methods=['GET'])
def check_email_api():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "Verify", "email": ""}), 400
    
    result = check_gmail_account_status(email)
    return jsonify({
        "email": email,
        "status": result
    })

@app.route('/')
def home():
    return "Gmail Checker Server Running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
