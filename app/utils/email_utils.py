import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import get_config

config = get_config()


class EmailUtility:

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        default_sender_email: str,
    ):
        self.server = smtp_server
        self.port = smtp_port
        self.username = smtp_username
        self.password = smtp_password
        self.default_sender_email = default_sender_email

    def send_email(self, to_address: str, subject: str, body: str, is_html=False):
        try:
            # Create a multipart message
            msg = MIMEMultipart()
            msg["From"] = self.default_sender_email
            msg["To"] = to_address
            msg["Subject"] = subject

            # Add body to the email
            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            # SMTP session
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()  # Secure the connection
                server.login(self.username, self.password)
                server.sendmail(self.default_sender_email, to_address, msg.as_string())
                print(f"Email sent to {to_address}")

        except Exception as e:
            print(f"Failed to send email: {e}")

    # def send_login_failure_email(self, email: str):
    #     # Replace with recipient email address
    #     receiver_email = "darren.mertz@ethereal.email"
    #     subject = "Login Failed"
    #     body = f"Login failed for email: {
    #         email}. Please check your credentials."
    #     self.send_email(receiver_email, subject, body)


# Initialize the EmailUtility with your SMTP configuration from config.py
email_util = EmailUtility(
    smtp_server=config.SMTP_SERVER,
    smtp_port=config.SMTP_PORT,
    smtp_username=config.SMTP_USERNAME,
    smtp_password=config.SMTP_PASSWORD,
    default_sender_email=config.DEFAULT_SENDER_EMAIL,
)
