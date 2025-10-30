import requests

def run_blind_certificate_task(restfulapi_address, d, n, blinded_content):
    data = {
        "d": d,
        "n": n,
        "blinded_content": blinded_content
    }

    try:
        response = requests.post(restfulapi_address + "/blind_certificate", json = data)

        if response.status_code == 201:
            return response.json()
        else:
            print(f"伺服器錯誤，狀態碼：{response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"請求過程中發生錯誤：{e}")

    return None