from datetime import datetime
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

load_dotenv()


def send_confirmation_email(to_email: str, code: str):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    subject = "Your confirmation code"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Email Confirmation</title>
    </head>
    <body style="margin:0;padding:0;background-color:#f4f6fb;font-family:Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6fb;padding:40px 0;">
        <tr>
        <td align="center">
            <table width="600" cellpadding="0" cellspacing="0" 
                style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.08);">

            <!-- Header -->
            <tr>
                <td align="center" style="padding:40px 20px;background:linear-gradient(135deg,#4F46E5,#9333EA);color:white;">
                <h1 style="margin:0;font-size:28px;">Vocali</h1>
                <p style="margin:8px 0 0 0;font-size:14px;opacity:0.9;">
                    Email Verification
                </p>
                </td>
            </tr>

            <!-- Body -->
            <tr>
                <td style="padding:40px 30px;color:#333333;">
                <h2 style="margin-top:0;font-size:22px;">
                    Confirm your email address
                </h2>

                <p style="font-size:15px;line-height:1.6;color:#555;">
                    Thanks for signing up! Use the confirmation code below to activate your account.
                </p>

                <!-- Code Box -->
                <div style="margin:30px 0;text-align:center;">
                    <div style="
                    display:inline-block;
                    padding:18px 36px;
                    font-size:28px;
                    font-weight:bold;
                    letter-spacing:6px;
                    color:#4F46E5;
                    background:#eef2ff;
                    border-radius:12px;
                    ">
                    {code}
                    </div>
                </div>

                <p style="font-size:14px;color:#777;">
                    This code expires in 10 minutes.
                </p>

                <p style="font-size:14px;color:#777;margin-top:30px;">
                    If you didn’t create an account, you can safely ignore this email.
                </p>
                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td align="center" style="padding:20px;color:#aaa;font-size:12px;border-top:1px solid #f0f0f0;">
                © {datetime.utcnow().year} Vocali. All rights reserved.
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={
            "name": "Vocali",
            "email": os.getenv("BREVO_SENDER_EMAIL")
        },
        subject=subject,
        html_content=html_content,
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Brevo error:", e)