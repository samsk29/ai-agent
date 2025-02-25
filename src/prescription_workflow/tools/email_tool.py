import imaplib
import email
import os
import json
import smtplib
import re
from typing import Tuple, Dict, List, Optional, Any
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging
from langchain.tools import tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class EmailTools:
    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT", 993))
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 465))

    @staticmethod
    @tool
    def read_emails(tool_input: str = ""):
        """
        Fetch unread prescription-related emails via IMAP and return a list of dictionaries containing:
          - message_id
          - subject
          - sender (from)
          - full email body
          - a snippet of the email body
          - all email headers

        Only emails related to prescriptions will be included.
        """
        try:
            mail = imaplib.IMAP4_SSL(EmailTools.email_host, EmailTools.email_port)
            mail.login(EmailTools.email_user, EmailTools.email_pass)
            mail.select("INBOX")

            # Search for unread emails
            result, data = mail.search(None, "UNSEEN")
            email_ids = data[0].split()

            if not email_ids:
                logger.info("No unread emails found.")
                mail.close()
                mail.logout()
                return []

            emails = []
            # Define keywords to filter prescription emails
            prescription_keywords = ["prescription", "medication", "Rx", "medicine", "refill", "pharmacy"]

            for email_id in email_ids:
                result, msg_data = mail.fetch(email_id, "(RFC822)")
                email_body_raw = msg_data[0][1]
                msg = email.message_from_bytes(email_body_raw)

                # Extract email details
                subject = msg.get("Subject", "").lower()
                sender = msg.get("From")
                full_body = EmailTools._get_email_body(msg).lower()
                snippet = full_body[:100] if full_body else ""
                message_id = msg.get("Message-ID")

                # Filter: Check if subject or body contains prescription-related terms
                if any(keyword in subject or keyword in full_body for keyword in prescription_keywords):
                    # Build headers list
                    headers = [{"name": key, "value": value} for key, value in msg.items()]

                    emails.append({
                        "headers": headers,
                        "message_id": message_id,
                        "subject": subject,
                        "from": sender,
                        "body": full_body,
                        "snippet": snippet
                    })

            mail.close()
            mail.logout()

            if emails:
                logger.info(f"Found {len(emails)} prescription-related emails.")
            else:
                logger.info("No prescription-related emails found.")

            return emails

        except Exception as error:
            logger.error(f"An error occurred while reading prescription emails: {error}")
            return None

    @staticmethod
    @tool
    def extract_prescription_fields_from_emails(emails_input: any) -> str:
        """
        Process a list of parsed email dictionaries and extract required prescription fields.
        If emails_input is a dictionary with an "emails" key, that list is used.
        If that value is not a list, it is wrapped into a list.
        Save the extracted data and record any missing fields to a new JSON file.
        
        Expected required fields (extracted from the full email body) include:
        - patient_name, dob, address, email, pharmacy_name, pharmacy_address,
            blood_pressure, heart_rate, medication_name, strength, repeats
        
        Returns:
        The path to the JSON file containing the extracted data and any missing fields.
        """
        try:
            # Normalize input to a list of email dictionaries.
            if isinstance(emails_input, dict) and "emails" in emails_input:
                emails = emails_input["emails"]
                if not isinstance(emails, list):
                    emails = [emails]
            elif isinstance(emails_input, list):
                emails = emails_input
            else:
                logger.error("Invalid input for extract_prescription_fields_from_emails; expected a list or dict with 'emails' key.")
                return "[]"

            all_extracted_data = []
            all_missing_fields = []

            # Updated regex patterns without strict anchors, stopping at the newline.
            required_fields = {
                "patient_name": r"Patient Name:\s*(.+?)(?:\n|$)",
                "dob": r"Date of Birth:\s*([\d-]+)(?:\n|$)",
                "address": r"Address:\s*(.+?)(?:\n|$)",
                "email": r"email:\s*([\w\.-]+@[\\w\\.-]+(?:\.[\\w]{2,})?)(?:\n|$)",
                "pharmacy_name": r"Pharmacy Name:\s*(.+?)(?:\n|$)",
                "pharmacy_address": r"Pharmacy Address:\s*(.+?)(?:\n|$)",
                "blood_pressure": r"Blood Pressure:\s*([\d/]+)(?:\n|$)",
                "heart_rate": r"Heart Rate:\s*(\d+)(?:\n|$)",
                "medication_name": r"Medication Name:\s*(.+?)(?:\n|$)",
                "strength": r"Strength:\s*(.+?)(?:\n|$)",
                "repeats": r"Repeats:\s*(\d+)(?:\n|$)"
            }

            for email_data in emails:
                extracted_data = {}
                missing_fields = []

                body = email_data.get("body", "")
                for field, pattern in required_fields.items():
                    match = re.search(pattern, body, re.IGNORECASE | re.MULTILINE)
                    if match:
                        # Take the match and strip any extra whitespace or newline characters.
                        value = match.group(1).strip().split("\n")[0]
                        extracted_data[field] = value
                    else:
                        extracted_data[field] = None
                        missing_fields.append(field)

                # Include meta details from the email
                extracted_data["message_id"] = email_data.get("message_id")
                extracted_data["subject"] = email_data.get("subject")
                extracted_data["from"] = email_data.get("from")

                all_extracted_data.append(extracted_data)
                all_missing_fields.append(missing_fields)

            # Save extracted data to JSON
            output_path = r"C:\Users\Cubegle\Desktop\sam\Prescription workflow\prescription\tests\extracted_prescriptions.json"
            with open(output_path, "w") as f:
                json.dump({
                    "extracted_data": all_extracted_data,
                    "missing_fields": all_missing_fields
                }, f, indent=2)

            return output_path

        except Exception as e:
            logger.error(f"Error extracting prescription fields from emails: {e}")
            return "[]"

    @staticmethod
    @tool
    def handle_missing_fields(json_file_path: str) -> Dict:
        """
        Process the extracted prescription data JSON file and for each email with missing fields,
        send an email to the patient requesting the missing information.
        
        Returns:
          A dictionary with the email addresses as keys and the status of the email response (True/False).
        """
        try:
            with open(json_file_path, "r") as f:
                data = json.load(f)
            extracted_data = data.get("extracted_data", [])
            missing_fields_list = data.get("missing_fields", [])
            
            status = {}
            for email_data, missing_fields in zip(extracted_data, missing_fields_list):
                if missing_fields:
                    recipient = email_data.get("from")
                    if recipient:
                        subject = "Missing Prescription Information"
                        missing_str = ", ".join(missing_fields)
                        body = (
                            f"Dear Patient,\n\n"
                            f"We noticed that the following required fields are missing from your prescription email: {missing_str}.\n"
                            f"Please provide the missing information at your earliest convenience.\n\n"
                            f"Thank you."
                        )
                        sent = EmailTools.send_email(
                            recipient, subject, body, original_message_id=email_data.get("message_id")
                        )
                        status[recipient] = sent
            return status
        except Exception as e:
            logger.error(f"Error handling missing fields: {e}")
            return {}

    @staticmethod
    def _get_email_body(msg) -> str:
        """
        Extracts the full email body.
        """
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition") or "")
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        part_body = part.get_payload(decode=True)
                        if part_body:
                            body += part_body.decode(errors="ignore") + "\n"
                    except Exception as e:
                        logger.error(f"Error decoding email part: {e}")
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors="ignore")
            except Exception as e:
                logger.error(f"Error decoding email body: {e}")
        return body.strip()
    
    @staticmethod
    @tool
    def send_email(recipient: str, subject: str, body: str, 
                   original_message_id: Optional[str] = None) -> bool:
        """
        Send an email with optional reply headers.
        """
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = f"Re: {subject}" if original_message_id else subject
            msg["From"] = EmailTools.email_user
            msg["To"] = recipient

            if original_message_id:
                msg["In-Reply-To"] = original_message_id
                msg["References"] = original_message_id

            with smtplib.SMTP_SSL(EmailTools.smtp_server, EmailTools.smtp_port) as server:
                server.login(EmailTools.email_user, EmailTools.email_pass)
                server.sendmail(EmailTools.email_user, recipient, msg.as_string())

            logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False