from arbitration_vote import run_arbitration_vote_task
from apscheduler.schedulers.background import BackgroundScheduler
from blind_certificate import run_blind_certificate_task
from daily_invoicing import run_daily_invoicing_task
from flask import Flask, request, jsonify
from send_credentials import run_send_credentials_task
from submit_complaint import run_submit_complaint_task
from vrf_pick import run_verify_pick_task

MONGODB_ADDRESS = "mongodb://172.18.0.4:27017/"
SERVER_EMAIL = "aa@gmail.com"
SERVER_EMAIL_PASSWORD = "1234"
COMPANY_NAME = "西瓜有限股份公司"
CREDENTIALS_QUANTITY = 10
NUMBER_PICKED = 3
THRESHOLD = 5
TOTAL_SHARES = 10

app = Flask(__name__)

def setup_scheduler():
    scheduler = BackgroundScheduler(daemon = True)

    scheduler.add_job(run_send_credentials_task, "cron", day = 1, hour = 0, minute = 0, args = [MONGODB_ADDRESS, SERVER_EMAIL, SERVER_EMAIL_PASSWORD, COMPANY_NAME, CREDENTIALS_QUANTITY])
    scheduler.add_job(run_daily_invoicing_task, "cron", hour = 20, minute = 0, args = [MONGODB_ADDRESS, SERVER_EMAIL, SERVER_EMAIL_PASSWORD, THRESHOLD, TOTAL_SHARES])

    scheduler.start()

@app.route("/blind_certificate", methods = ["POST"])
def create_blind_certificate():
    data = request.get_json()
    d = data.get("d")
    n = data.get("n")
    blinded_content = data.get("blinded_content")

    try:
        signed_blinded = run_blind_certificate_task(MONGODB_ADDRESS, d, n, blinded_content)
        return jsonify(signed_blinded), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
    
@app.route("/submit_complaint", methods = ["POST"])
def create_submit_complaint():
    try:
        data = request.get_json()

        credentials = data.get("credentials")
        complaint_content = data.get("complaint_content")
        signed_blinded = data.get("signed_blinded")
        identity_n = data.get("identity_n")
        
        if run_submit_complaint_task(MONGODB_ADDRESS, SERVER_EMAIL, SERVER_EMAIL_PASSWORD, credentials, complaint_content, signed_blinded, identity_n, THRESHOLD, TOTAL_SHARES):  
            return jsonify({"message": "申訴提交成功"}), 201
        else:
            return jsonify({"error": "申訴提交失敗"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify_pick", methods = ["POST"])
def query_verify_pick():
    try:
        data = request.get_json()

        public_key = data.get("public_key")
        random_number = data.get("random_number")
        signature = data.get("signature")
        name = data.get("name")

        if run_verify_pick_task(MONGODB_ADDRESS, public_key, random_number, signature, TOTAL_SHARES, name):     
            return jsonify({"message": "您是本次委員會的成員"}), 201
        else:
            return jsonify({"message": "您不是本次委員會的成員"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/arbitration_vote", methods = ["POST"])
def conduct_arbitration_vote():
    try:
        data = request.get_json()

        complaint_id = data.get("complaint_id")
        private_key_sharding = data.get("private_key_sharding")
        vote = data.get("vote")

        if run_arbitration_vote_task(MONGODB_ADDRESS, complaint_id, private_key_sharding, vote):     
            return jsonify({"message": "投票已成功完成"}), 201
        else:
            return jsonify({"message": "投票未能完成"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    setup_scheduler()

    app.run(host = "0.0.0.0", port = 6375, debug = True)
