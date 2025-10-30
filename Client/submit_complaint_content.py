import requests

def run_submit_complaint_content_task(restfulapi_address, credentials, complaint_content, signed_blinded, identity_n):
    data = {
        "credentials": credentials,
        "complaint_content": complaint_content,
        "signed_blinded": signed_blinded,
        "identity_n": identity_n
    }

    try:
        response = requests.post(restfulapi_address + "/submit_complaint", json = data)

        if response.status_code == 201:
            return True
        else:
            print(f"伺服器錯誤，狀態碼：{response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"請求過程中發生錯誤：{e}")
    
    return False
