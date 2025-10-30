from cryptography.hazmat.primitives import hashes
from datetime import datetime
from pymongo import MongoClient
from set_up_ballot_box import run_set_up_ballot_box_task
from vrf_pick import run_vrf_pick_task

def run_submit_complaint_task(mongodb_address, server_email, server_email_password, credentials, complaint_content, signed_blinded, identity_n, threshold, total_shares):
    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]
    
    collection_1 = db["blind_certificate"]
    document_1 = {
        "signed_blinded": str(signed_blinded)
    }
    results_1 = collection_1.find(document_1)
    results_1 = list(results_1)
    quantity = len(results_1)

    year = datetime.now().year
    month = datetime.now().month

    collection_2 = db["credentials"]
    document_2 = {
        "data": f"{year}-{month}"
    }
    results_2 = collection_2.find(document_2)
    for document_3 in results_2:
        if quantity > 0 and credentials in document_3["credentials"]:
            complaint_id = run_set_up_ballot_box_task(mongodb_address, identity_n)

            run_vrf_pick_task(mongodb_address, server_email, server_email_password, complaint_content, complaint_id, threshold, total_shares)

            return True
        else:
            return False
