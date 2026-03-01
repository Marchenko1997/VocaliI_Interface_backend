from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates"))
)


def _render_template(template_name: str, **context):
    template = env.get_template(template_name)
    return template.render(**context)




def _send_email(to_email: str, subject: str, html_content: str):

    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("BREVO_SENDER_EMAIL")

    if not api_key or not sender_email:
        raise RuntimeError("BREVO configuration missing in environment variables")

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={
            "name": "Vocali",
            "email": sender_email
        },
        subject=subject,
        html_content=html_content,
    )

    try:
        response = api_instance.send_transac_email(email)
        print(f"Email sent successfully to {to_email}")
        return response

    except ApiException as e:
        print("Brevo API error:")
        print(e)
        raise

    except Exception as e:
        print("Unexpected email error:")
        print(e)
        raise




def send_confirmation_email(to_email: str, code: str):
    html = _render_template(
        "confirmation.html",
        code=code,
        year=datetime.utcnow().year
    )
    _send_email(to_email, "Email Confirmation", html)




def send_reset_password_email(to_email: str, code: str):
    html = _render_template(
        "reset_password.html",
        code=code,
        year=datetime.utcnow().year
    )
    _send_email(to_email, "Password Reset", html)