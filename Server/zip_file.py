import os
import pyzipper

def generate_zip_path(file_name):
    file_name = os.path.basename(file_name)
    zip_name = os.path.splitext(file_name)[0] + ".zip"
    return zip_name

def run_zip_file_task(file_name, password):
    zip_name = generate_zip_path(file_name)
    with pyzipper.AESZipFile(zip_name, mode = "w", encryption = pyzipper.WZ_AES, compresslevel = 5) as zipfile:
        zipfile.setpassword(password.encode())
        zipfile.write(file_name, os.path.basename(file_name)) 