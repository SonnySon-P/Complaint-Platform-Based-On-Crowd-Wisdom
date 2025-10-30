from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import secrets
import math

def encrypt(message, e, n):
    message_int = int.from_bytes(message.encode("utf-8"), byteorder = "big")
    ciphertext_int = pow(message_int, e, n)
    return ciphertext_int

def run_blind_content_task(identity_e, identity_n, employee_id, complaint_content):
    ciphertext = encrypt(employee_id, identity_e, identity_n)

    temporary_content = f"加密後的員工編號：\n"
    temporary_content += "------------------------------------------------------------------------------\n"
    temporary_content += f"{ciphertext}\n"
    temporary_content += "------------------------------------------------------------------------------\n\n"
    temporary_content += f"申訴內容：\n"
    temporary_content += complaint_content

    key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048
    )    
    n = key.public_key().public_numbers().n
    e = key.public_key().public_numbers().e
    d = key.private_numbers().d

    hash = hashes.Hash(hashes.SHA256())
    hash.update(temporary_content.encode("utf-8"))
    m_int = int.from_bytes(hash.finalize(), byteorder = "big")

    while True:
        r = secrets.randbelow(n - 2) + 2
        if math.gcd(r, n) == 1:
            break
    
    blinded_content = (m_int * pow(r, e, n)) % n

    return r, d, e, n, m_int, temporary_content, blinded_content