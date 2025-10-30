from bson import ObjectId
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from generate_rsa_keys import run_generate_rsa_keys_task
from pymongo import MongoClient
from secret_sharing import next_prime, split_secret
from send_email import run_send_email_task
import os
import random

def export_public_key_pem(public_key) -> str:
    pem = public_key.public_bytes(
        encoding = Encoding.PEM,
        format = PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    return pem

def load_public_key(pem_key):
    public_key = serialization.load_pem_public_key(
        pem_key.encode("utf-8")
    )
    return public_key

def encrypt(message, e, n):
    message_int = int.from_bytes(message.encode("utf-8"), byteorder = "big")
    ciphertext_int = pow(message_int, e, n)
    return ciphertext_int

def verify_signature(public_key, random_number, signature):
    message = str(random_number).encode()
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    
    except Exception as e:
        return False

def sign_random_number(private_key, random_number):
    message = str(random_number).encode()
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature

def vrf_pick_members(vrf_public_key, vrf_private_key, members_list, number_picked):
    random_number = os.urandom(32)

    signature = sign_random_number(vrf_private_key, random_number)

    if not verify_signature(vrf_public_key, random_number, signature):
        raise ValueError("簽名無效，隨機數驗證失敗。")

    random.seed(int.from_bytes(random_number, byteorder = "big"))
    picked_members = random.sample(members_list, number_picked)

    return random_number, signature, picked_members

def run_verify_pick_task(mongodb_address, public_key_pem, random_number, signature, total_shares, name):
    public_key = load_public_key(public_key_pem)
    if not verify_signature(public_key, random_number, signature):
        raise ValueError("隨機數驗證失敗")

    members_list = []

    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]

    collection = db["employee"]
    results = collection.find()
    for document in results:
        members_list.append(document["name"])

    random.seed(int.from_bytes(random_number, byteorder = "big"))
    picked_members = random.sample(members_list, total_shares)
    if name in picked_members:
        return True
    else:
        return False

def run_vrf_pick_task(mongodb_address, server_email, server_email_password, complaint_content, complaint_id, threshold, total_shares):
    members_list = []

    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]

    collection_1 = db["employee"]
    results_1 = collection_1.find()
    for document in results_1:
        members_list.append(document["name"])

    vrf_private_key, vrf_public_key = run_generate_rsa_keys_task()
    vrf_public_key_pem = export_public_key_pem(vrf_public_key)
    random_number, signature, picked_members = vrf_pick_members(vrf_public_key, vrf_private_key, members_list, total_shares)

    ts_private_key, ts_public_key = run_generate_rsa_keys_task()
    numbers = ts_private_key.private_numbers()
    n = numbers.public_numbers.n
    e = numbers.public_numbers.e
    secret_int = ts_private_key.private_numbers().d
    prime = next_prime(secret_int)

    ts_private_key_shares = split_secret(secret_int, threshold, total_shares, prime)

    year = datetime.now().year
    month = datetime.now().month
    plaintext = f"{year}-{month}-{random.randint(1, 1000)}-{random.randint(1, 1000)}-{random.randint(1, 1000)}"
    ciphertext = encrypt(plaintext, e, n)

    collection_2 = db["ballot_box"]
    query = {
        "_id": ObjectId(complaint_id)
    }
    update = {
        "$set": {
            "prime": str(prime),
            "n": str(n),
            "complaint_content": complaint_content,
            "plaintext": plaintext,
            "ciphertext": str(ciphertext)
        }
    }
    collection_2.update_one(query, update)

    subject = "邀請您擔任申訴仲裁委員會成員"

    date_after_7_days = datetime.now() + timedelta(days = 7)
    date_only = date_after_7_days.date()

    for i in range(total_shares):
        body = (
            f"親愛的 {picked_members[i]} 先生/女士，您好：\n"
            f"誠摯邀請您擔任 {year} 年 {month} 月申訴仲裁委員會的成員。\n"
            f"--++ 以下為本次申訴的主要內容 ++--\n\n"
            f"{complaint_content}\n\n"
            f"本次申訴案件編號為：{complaint_id}\n\n"
            f"為確保委員投票過程的公正與安全，敬請保存以下私鑰分片資訊： {ts_private_key_shares[i][1]}\n\n"
            f"敬請您於 {date_only} 前完成投票，以確保您的意見能被納入計算。\n\n"
            f"--++ 驗證此次委員會成員選任資訊 ++--\n\n"
            f"公鑰（Public Key）：\n{vrf_public_key_pem}\n\n"
            f"隨機數（Random Number）：{random_number}\n\n"
            f"簽章（Signature）：{signature}\n\n"
            f"感謝您為維護本機構公正透明所作的貢獻。\n\n"
            f"敬祝\n\n"
            f"工作順利，萬事如意！\n\n"
            f"—— 申訴仲裁委員會秘書處"
        )

        document = {
            "name": picked_members[i]
        }
        results_2 = collection_1.find(document)

        #run_send_email_task(server_email, server_email_password, results["email"], subject, body)
