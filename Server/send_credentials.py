from datetime import datetime
from generate_rsa_keys import run_generate_rsa_keys_task
from secret_sharing import next_prime, split_secret
from send_email import run_send_email_task
from pymongo import MongoClient
from zip_file import run_zip_file_task
import hashlib

def generate_hash(text):
    hash = hashlib.new("sha256")
    hash.update(text.encode("utf-8"))
    return hash.hexdigest()

def run_send_credentials_task(mongodb_address, server_email, server_email_password, company_name, credentials_quantity):
    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]

    collection_1 = db["employee"]
    results = collection_1.find({})

    results = list(results)
    total_shares = len(results)
    threshold = total_shares // 3 * 2

    private_key, public_key = run_generate_rsa_keys_task()
    numbers = private_key.private_numbers()
    n = numbers.public_numbers.n
    e = numbers.public_numbers.e
    secret_int = private_key.private_numbers().d
    prime = next_prime(secret_int)
    
    shares = split_secret(secret_int, threshold, total_shares, prime)
    
    year = datetime.now().year
    month = datetime.now().month

    content_1 = f"{company_name} {year}年{month}月申訴憑證\n"
    content_2 = content_1 + f"\n加密身份公鑰e： {e}\n"
    content_2 += f"\n加密身份公鑰n： {n}\n"
    content_2 += "\n申訴憑證：\n"
    content_2 += "------------------------------------------------------------------------------\n"

    credentials = []

    for i in range(credentials_quantity):
        hash = generate_hash(f"{content_1}-{i + 1}")
        content_2 += f"第{i + 1}筆：{hash}\n"
        credentials.append(hash)
        content_2 += "------------------------------------------------------------------------------\n"

    collection_2 = db["credentials"]
    document_2 = {
        "data": f"{year}-{month}",
        "credentials": credentials,
        "n": str(n),
        "prime": str(prime)
    }
    collection_2.insert_one(document_2)

    i = 0
    for document_1 in results:
        content_3 = content_2 + f"\n解密身份私鑰分片：\n{shares[i][1]}\n"

        with open("credentials.txt", "w", encoding = "utf-8") as file:
            file.write(content_3)

        run_zip_file_task("credentials.txt", document_1["id_number"])
        body = f'{document_1["name"]} 您好:\n附件為{content_1}請注意：壓縮附件檔案的密碼，為您的身份字號。'
        #run_send_email_task(server_email, server_email_password, document["email"], content_1, body, "credentials.zip")

        i += 1
