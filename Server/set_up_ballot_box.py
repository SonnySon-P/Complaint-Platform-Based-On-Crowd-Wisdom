from bson import Binary
from datetime import datetime, timedelta
from pymongo import MongoClient

def run_set_up_ballot_box_task(mongodb_address, identity_n):
    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]
    collection = db["ballot_box"]

    date_after_7_days = datetime.now() + timedelta(days = 7)

    document = {
        "deadline": date_after_7_days,
        "agree": [],
        "disagree": [],
        "prime": "",
        "n": "",
        "complaint_content": "",
        "plaintext": "",
        "ciphertext": "",
        "agreed_private_key_sharding": [],
        "identity_n": identity_n
    }

    result = collection.insert_one(document)

    return result.inserted_id