import os


class EmailTemplateType:
    def __init__(self, subject: str, body: str, is_html: bool):
        self.subject = subject
        self.body = body
        self.is_html = is_html

    def get_body_with_variables(self, **kwargs):
        formatted_body = self.body.format(**kwargs)
        return formatted_body


# Function to read the HTML file


# Define the base directory for HTML templates
BASE_HTML_DIR = os.path.join("app", "asset", "html")


def read_html_template(file_name: str) -> str:
    # Construct the full file path
    file_path = os.path.join(BASE_HTML_DIR, file_name)
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Load the HTML template from the external file
SIGN_UP_EMAIL_VERIFICATION_TEMPLATE = EmailTemplateType(
    subject="Sign Up - Email verification",
    # Load HTML content from file, only the file name is needed now
    body=read_html_template("signup_email.html"),
    is_html=True,
)


SIGN_UP_SUCCESS_EMAIL_TEMPLATE = EmailTemplateType(
    subject="Welcome to ZyloAssist!",
    body=read_html_template("signup_success.html"),
    is_html=True,
)

FORGOT_PASSWORD_EMAIL_VERIFICATION_TEMPLATE = EmailTemplateType(
    subject="Reset Password Request",
    body=read_html_template("forgot_password_email.html"),
    is_html=True,
)
USER_EMAIL_VERIFICATION_TEMPLATE = EmailTemplateType(
    subject="User - Email verification",
    body=read_html_template("user_email_verification.html"),
    is_html=True,
)

USER_SUCCESS_EMAIL_TEMPLATE = EmailTemplateType(
    subject="Welcome to ZyloAssist!",
    body=read_html_template("signup_success.html"),
    is_html=True,
)
SUBSCRIPTION_EXPIRE_EMAIL_TEMPLATE = EmailTemplateType(
    subject="Subscription Expiry Reminder",
    body=read_html_template("subscription_reminder_email.html"),
    is_html=True,
)
