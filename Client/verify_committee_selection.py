import requests

def run_verify_committee_selection_task(restfulapi_address, public_key, random_number, signature, selected_member):
    data = {
        "public_key": public_key,
        "random_number": random_number,
        "signature": signature,
        "selected_member": selected_member
    }

    try:
        response = requests.post(restfulapi_address + "/verify_pick", json = data)

        if response.status_code == 201:
            return True
        else:
            print(f"伺服器錯誤，狀態碼：{response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"請求過程中發生錯誤：{e}")
    
    return False