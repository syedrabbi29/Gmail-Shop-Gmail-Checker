import dns.resolver
from flask import Flask, request, jsonify
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

def check_gmail_fast(email):
    # ১. ইমেইল ইনপুট ও ডোমেইন ভ্যালিডেশন
    try:
        valid = validate_email(email, check_deliverability=False)
        email_addr = valid.email.lower()
        domain = email_addr.split('@')[1]
    except EmailNotValidError:
        return "Verify"

    if domain != "gmail.com":
        return "Verify"

    # ২. ইউজারনেম ফিল্টারিং (খুব ছোট বা অস্বাভাবিক ক্যারেক্টার চেক)
    username = email_addr.split('@')[0]
    if len(username) < 6 or ".." in username:
        return "Verify"

    # ৩. DNS MX Record দ্রুত চেক
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        if len(mx_records) > 0:
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
    
    result = check_gmail_fast(email)
    return jsonify({
        "email": email,
        "status": result
    })

@app.route('/')
def home():
    return "Server is Active", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
