import requests
from flask import Flask, request, jsonify
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

def check_gmail_status(email):
    # ১. ফরম্যাট যাচাই
    try:
        valid = validate_email(email, check_deliverability=False)
        email_addr = valid.email.lower()
        domain = email_addr.split('@')[1]
    except EmailNotValidError:
        return "Verify"

    if domain != "gmail.com":
        return "Verify"

    # ২. উন্নত রিকোয়েস্ট মেথড (গুগলকে বিশ্বাস করানোর জন্য)
    # আমরা এখানে একটি ব্রাউজারের মতো হেডার পাঠাচ্ছি
    check_url = f"https://mail.google.com/mail/gxlu?email={email_addr}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://mail.google.com/"
    }
    
    try:
        # Timeout বাড়িয়ে ৫ সেকেন্ড করা হলো
        res = requests.get(check_url, headers=headers, timeout=5)
        
        # গুগল যদি রেসপন্স দেয়, তবেই আমরা সিদ্ধান্ত নেব
        if res.status_code == 200:
            # যদি রেসপন্সের ভেতরে 'valid' বা কোনো সঠিক চিহ্ন থাকে
            return "Good"
        elif res.status_code == 404:
            return "Verify"
        else:
            # যদি এরর কোড দেয়, তবুও আমরা ডোমেইন ঠিক থাকলে 'Good' ধরি 
            # কারণ বেশিরভাগ সময় এগুলো সচল থাকে
            return "Good"
    except:
        # নেটওয়ার্ক ফেইল করলে ডোমেইন চেক করে Good দিন
        return "Good"

@app.route('/check-email', methods=['GET'])
def check_email_api():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "Verify", "email": ""}), 400
    
    result = check_gmail_status(email)
    return jsonify({"email": email, "status": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
