from imapclient import IMAPClient
import email
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")

def fetch_emails():
    with IMAPClient(IMAP_SERVER) as server:
        server.login(EMAIL, PASSWORD)
        server.select_folder("INBOX")

        messages = server.search(['BODY', 'unsubscribe'])
        print(f"Found {len(messages)} emails with 'unsubscribe'.")

        for msg_id in messages:
            raw_message = server.fetch([msg_id], ["RFC822"])[msg_id][b"RFC822"]
            message = email.message_from_bytes(raw_message)

        sender = message.get("From")
        subject = message.get("Subject")
        print(f"Email from: {sender}, Subject: {subject}")

        for part in message.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode()
                soup = BeautifulSoup(html_content, "html.parser")
                unsubscribe_links = soup.find_all("a", href=True, text=re.compile("unsubscribe", re.I))

                for link in unsubscribe_links:
                    print("Unsubscribe link: ", link['href'])

if __name__ == "__main__":
    fetch_emails()