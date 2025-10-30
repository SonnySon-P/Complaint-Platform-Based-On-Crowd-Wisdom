from datetime import datetime, timedelta
from pymongo import MongoClient
from secret_sharing import reconstruct_secret
from set_up_ballot_box import run_set_up_ballot_box_task
from vrf_pick import run_vrf_pick_task

def decrypt(ciphertext_int, d, n):
    message_int = pow(ciphertext_int, d, n)
    length = (message_int.bit_length() + 7) // 8
    return message_int.to_bytes(length, byteorder = "big").decode("utf-8")

def run_daily_invoicing_task(mongodb_address, server_email, server_email_password, threshold, total_shares):
    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]
    collection = db["ballot_box"]

    one_day_ago = datetime.now() - timedelta(days = 1)
    day_start = datetime(one_day_ago.year, one_day_ago.month, one_day_ago.day)
    day_end = day_start + timedelta(days = 1)

    query = {
        "deadline": {
            "$gte": day_start,
            "$lt": day_end
        }
    }

    results = collection.find(query)

    for document in results:
        private_key_sharding = []
        i = 1
        for agreed_private_key_shardin in document["agreed_private_key_sharding"]:
            private_key_sharding.append((i, int(agreed_private_key_shardin)))
            i += 1

        total_votes = len(document["agree"]) + len(document["disagree"])
        if total_votes >= threshold:
            if len(document["agree"]) > total_votes // 2:
                prime = int(document["prime"])
                n = int(document["n"])
                plaintext = document["plaintext"]
                ciphertext = int(document["ciphertext"])

                reconstructed_d = reconstruct_secret(private_key_sharding, threshold, prime)

                decrypted_message = decrypt(ciphertext, reconstructed_d, n)

                if decrypted_message == plaintext:
                    print("成立專責委員會")
                else:
                    print("簽章有問題")
            else:
                print("申訴案件不成立")
        else:
            print("新一輪投票")

            complaint_id = run_set_up_ballot_box_task(mongodb_address)

            run_vrf_pick_task(mongodb_address, server_email, server_email_password, document["complaint_content"], complaint_id, threshold, total_shares)


run_daily_invoicing_task("mongodb://172.18.0.4:27017/", "123", "456", 5, 10)