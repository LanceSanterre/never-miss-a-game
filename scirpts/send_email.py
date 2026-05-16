import os
import smtplib
from email.message import EmailMessage
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load .env reliably (project root)
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
print("Loaded EMAIL_USER:", os.getenv("EMAIL_USER"))
print("Loaded EMAIL_APP_PASSWORD length:", len(os.getenv("EMAIL_APP_PASSWORD") or ""))

def send_bulk_bcc(sender, app_password, recipients, subject, body):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = sender
    msg["Bcc"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(sender, app_password)
        s.send_message(msg)

if __name__ == "__main__":
    sender = os.getenv("EMAIL_USER")
    app_pw = os.getenv("EMAIL_APP_PASSWORD")
    raw = os.getenv("RECIPIENT_EMAIL", "")

    if not sender or not app_pw:
        raise RuntimeError(f"Missing EMAIL_USER or EMAIL_APP_PASSWORD in {ENV_PATH}")

    recipients = [r.strip() for r in raw.split(",") if r.strip()]
    if not recipients:
        raise RuntimeError(f"Missing RECIPIENT_EMAIL in {ENV_PATH}")

    subject = "Today’s Games"
    csv_path = Path(__file__).resolve().parents[1] / "email_data" / "todays_games.csv"
    data = pd.read_csv(csv_path)

    body_lines = ["Hi,", "", "Here are today’s games:", ""]

    for _, row in data.iterrows():
        game_between = row.iloc[0]
        time_of_game = row.iloc[1]
        channels = row.iloc[2]

        body_lines.append(f"• {game_between}")
        body_lines.append(f"  Time: {time_of_game}")
        body_lines.append(f"  Channels: {channels}")
        body_lines.append("")

    body_lines.extend(["Thanks,", "Lance"])
    body = "\n".join(body_lines)

    send_bulk_bcc(sender, app_pw, recipients, subject, body)
    print("Sent.")
