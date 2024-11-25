from typing import Optional

import smtplib
from email.mime.text import MIMEText

from config import SEND_REAL_EMAILS, GMAIL_ADDRESS, GMAIL_PASSWORD
from logger import logger


class EmailManager:
    _instance: Optional["EmailManager"] = None
    
    def __new__(cls) -> "EmailManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not SEND_REAL_EMAILS:
            return
        
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
    
    @classmethod
    def start(cls):
        if cls._instance is None:
            cls._instance = EmailManager()
    
    @classmethod
    def send_confirmation_link(cls, user_email: str, link: str):
        if cls._instance is None:
            raise RuntimeError("EmailManager is not initialized")
        
        if not SEND_REAL_EMAILS:
            print("Not sending real emails")
            logger.info(f"Confirmation link for <{user_email}>: {link}")
            return

        print("Sending real emails")
        msg = MIMEText(f"Your verification link is {link}")
        msg["Subject"] = "Verify your account"
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = user_email

        cls._instance.server.send_message(msg, GMAIL_ADDRESS, user_email)

    @classmethod
    def close(cls):
        if cls._instance is None:
            return
        
        if not hasattr(cls._instance, "server"):
            return

        cls._instance.server.quit()
        cls._instance = None
