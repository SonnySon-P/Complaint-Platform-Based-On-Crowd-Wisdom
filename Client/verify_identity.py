import hashlib

def generate_hash(text):
    hash = hashlib.new("sha256")
    hash.update(text.encode("utf-8"))
    return hash.hexdigest()

def run_verify_identity_task(company_name, employee_id):
    for i in range(1000):
        if employee_id == generate_hash(f"{company_name}，編號第{i + 1}位員工"):
            return True
    return False