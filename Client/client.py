from arbitration_vote import run_arbitration_vote_task
from blind_content import run_blind_content_task
from blind_certificate import run_blind_certificate_task
from verify_committee_selection import run_verify_committee_selection_task
from verify_identity import run_verify_identity_task
from submit_complaint_content import run_submit_complaint_content_task
import ast

RESTFULAPI_ADDRESS = "http://172.18.0.2:6375"
COMPANY_NAME = "西瓜有限股份公司"

employee_id, r, d, e, n, m_int, complaint_content, blinded_content, signed_blinded, identity_n = None, None, None, None, None, None, None, None, None, None

def get_blind_content():
    global employee_id, r, d, e, n, m_int, identity_n, complaint_content, blinded_content

    employee_id = input("請輸入您的員工編號： ")
    identity_e = input("請輸入加密身份公鑰e： ")
    identity_n = input("請輸入加密身份公鑰n： ")
    complaint_content = input("請詳述您的投訴內容： ")

    if run_verify_identity_task(COMPANY_NAME, employee_id):
        r, d, e, n, m_int, complaint_content, blinded_content = run_blind_content_task(int(identity_e), int(identity_n), employee_id, complaint_content)
        print(f"成功獲取盲化投訴內容：{blinded_content}")
        print(identity_n)
        return True
    else:
        print("身份認證失敗")
        return False

def get_blind_certificate():
    global employee_id, r, d, e, n, m_int, blinded_content, signed_blinded

    if employee_id is None or r is None or d is None or e is None or n is None or m_int is None or blinded_content is None:
        print("盲化內容尚未處理，請先盲化申訴內容")
        return False
    
    signed_blinded = run_blind_certificate_task(RESTFULAPI_ADDRESS, d, n, blinded_content)
    
    if signed_blinded == None:
        print("盲化憑證失敗")
        return False
    
    r_inv = pow(r, -1, n)

    signed = (signed_blinded * r_inv) % n

    if m_int == pow(signed, e, n):
        print(f"成功獲取盲化憑證：{signed}")
        return True
    else:
        print("盲化憑證失敗")
        return False

def submit_complaint_content():
    global complaint_content, signed_blinded, identity_n 
    
    if complaint_content is None or signed_blinded is None:
        print("未得到盲化憑證，請先取得盲化憑證")
        return False
    
    credentials = input("請輸入本月憑證： ")

    result = run_submit_complaint_content_task(RESTFULAPI_ADDRESS, credentials, complaint_content, signed_blinded, identity_n)

    if result:
        print("成功提出申訴案件")
        return True
    else:
        print("盲提出申訴案件失敗")
        return False

def verification_committee_selection():
    public_key = input("請輸入公鑰： ")
    random_number = input("請輸入隨機數： ")
    signature = input("請輸入簽名： ")
    selected_member = input("請輸入你的名字： ")

    result = run_verify_committee_selection_task(RESTFULAPI_ADDRESS, public_key, ast.literal_eval(random_number), ast.literal_eval(signature), selected_member)

    if result:
        print("您是本次委員會的成員")
        return True
    else:
        print("您不是本次委員會的成員")
        return False

def conduct_arbitration_vote():
    complaint_id = input("請提供您的申訴案件編號： ")
    private_key_sharding = input("請輸入您的私鑰分片資訊： ")
    vote = input("請選擇您的投票意向：（同意請輸入「Y」、不同意請輸入「N」） ")

    result = run_arbitration_vote_task(RESTFULAPI_ADDRESS, complaint_id, private_key_sharding, vote)

    if result:
        print("投票已成功完成")
        return True
    else:
        print("投票未能完成")
        return False

def main():
    print("\n")
    print(r"       ___                           .                    .         .___   .           .    ,__") 
    print(r" .'   \   __.  , _ , _   \,___,  |     ___  ` , __   _/_        /   \  |     ___  _/_   /  `   __.  .___  , _ , _") 
    print(r" |      .'   \ |' `|' `. |    \  |    /   ` | |'  `.  |         |,_-'  |    /   `  |    |__  .'   \ /   \ |' `|' `.") 
    print(r" |      |    | |   |   | |    |  |   |    | | |    |  |         |      |   |    |  |    |    |    | |   ' |   |   |") 
    print(r"  `.__,  `._.' /   '   / |`---' /\__ `.__/| / /    |  \__/      /     /\__ `.__/|  \__/ |     `._.' /     /   '   /") 
    print(r"                         \                                                              /")
                                        
    while True:
        print("\n請選擇一個操作選項：")
        print("1. 盲化申訴內容")
        print("2. 取得盲化憑證")
        print("3. 提出申訴案件")
        print("4. 驗證委員挑選結果")
        print("5. 進行仲裁委員投票")
        print("6. 退出程序")

        user_input = input("輸入指令編號： ")

        if user_input == "1":
            if not get_blind_content():
                continue
        elif user_input == "2":
            if not get_blind_certificate():
                continue
        elif user_input == "3":
            if not submit_complaint_content():
                continue
        elif user_input == "4":
            if not verification_committee_selection():
                continue
        elif user_input == "5":
            if not conduct_arbitration_vote():
                continue
        elif user_input == "6":
            print("退出程序...")
            break
        else:
            print("命令無效，請重試！")

if __name__ == "__main__":
    main()