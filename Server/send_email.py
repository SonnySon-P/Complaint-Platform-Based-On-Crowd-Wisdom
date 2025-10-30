import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def run_send_email_task(from_email, password, to_email, subject, body, attachment_path = None):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(from_email, password)

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    if attachment_path:
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

                encoders.encode_base64(part)

                part.add_header("Content-Disposition", f'attachment; filename="{attachment_path.split("/")[-1]}"')

                message.attach(part)
        except Exception as e:
            print(f"附件處理失敗: {e}")
            return

    try:
        server.sendmail(from_email, to_email, message.as_string())
        print(f"郵件成功發送給 {to_email}")
    except Exception as e:
        print(f"郵件發送失敗: {e}")
    finally:
        server.quit()
