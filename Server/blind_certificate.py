from datetime import datetime
from pymongo import MongoClient

def run_blind_certificate_task(mongodb_address, d, n, blinded_content):
    signed_blinded = pow(blinded_content, d, n)
    
    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]
    collection = db["blind_certificate"]
    document = {
        "data": datetime.now(),
        "signed_blinded": str(signed_blinded) 
    }
    collection.insert_one(document)

    return signed_blinded
