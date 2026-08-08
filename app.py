import requests
from flask import Flask, request, jsonify
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

def check_gmail_status(email):
    # ১. ইমেইল ফরম্যাট যাচাই
    try:
        valid = validate_email(email, check_deliverability=False)
        email_addr = valid.email.lower()
        domain = email_addr.split('@')[1]
    except EmailNotValidError:
        return "Verify"

    if domain != "gmail.com":
        return "Verify"

    # ২. ইউজারনেম ও বেসিক ফিল্টারিং
    username = email_addr.split('@')[0]
    if len(username) < 6:
        return "Verify"

    # ৩. গুগলের সাথে এইচটিটিপিএস হ্যান্ডশেক
    try:
        check_url = f"https://mail.google.com/mail/gxlu?email={email_addr}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(check_url, headers=headers, timeout=4)
        
        if res.status_code == 200:
            return "Good"
        else:
            return "Verify"
    except Exception:
        return "Verify"

@app.route('/check-email', methods=['GET'])
def check_email_api():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "Verify", "email": ""}), 400
    
    result = check_gmail_status(email)
    return jsonify({
        "email": email,
        "status": result
    })

@app.route('/')
def home():
    return "Server is Live", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
