import requests

def run_arbitration_vote_task(restfulapi_address, complaint_id, private_key_sharding, vote):
    data = {
        "complaint_id": complaint_id,
        "private_key_sharding": private_key_sharding,
        "vote": vote
    }

    try:
        response = requests.post(restfulapi_address + "/arbitration_vote", json = data)

        if response.status_code == 201:
            return True
        else:
            print(f"伺服器錯誤，狀態碼：{response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"請求過程中發生錯誤：{e}")
    
    return False