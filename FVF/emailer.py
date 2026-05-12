import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.iliad-free.fr")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
STREAMLIT_URL = os.getenv("STREAMLIT_URL")  # corrigé : ULT -> URL
RECIPIENTS = os.getenv("RECIPIENTS", "").split(",")

def send_weekly_report():
    today = date.today().strftime("%d/%m/%Y")

    msg = MIMEMultipart("alternative")  # manquait cette ligne
    msg["Subject"] = f"[Télématique] Top 10 Fraude Kilométrique - {today}"
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(RECIPIENTS)
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Dashboard Fraude Télématique</h2>
        <p>Bonjour,</p>
        <p>Le rapport hebdomadaire de suivi kilométrique hors journée de travail est disponible :</p>
        <p>
          <a href="{STREAMLIT_URL}" style="
            background-color: #e8002d;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
          ">
            Accéder au Dashboard
          </a>
        </p>
        <p style="color: #888; font-size: 12px;">Rapport généré automatiquement le {today}</p>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())
        print(f"Mail envoyé à {RECIPIENTS}")