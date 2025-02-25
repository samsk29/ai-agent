#!/usr/bin/env python
import os
import sys
import time
from dotenv import load_dotenv
from prescription_workflow.crew import PrescriptionWorkflow
from prescription_workflow.tools.email_tool import EmailTools

load_dotenv()

def run():
    """
    Run the crew.
    """
    while True:
        time.sleep(3)

        print("Reading emails...")
        emails = EmailTools.read_emails.invoke("")

        if not emails:
            continue

        latest_email = emails[0]

        # Extract sender, subject, and message id from the email headers
        sender_email = [header['value'] for header in latest_email['headers'] if header['name'] == 'From'][0]
        email_subject = [header['value'] for header in latest_email['headers'] if header['name'] == 'Subject'][0]
        email_message_id = latest_email.get("message_id")
        email_body = latest_email['body']

        email_input = f"""
                        Message_ID: {email_message_id}
                        Sender_Email: {sender_email}
                        Subject: {email_subject}
                        Body: {email_body}
                        """
        print("Email content:", email_input)

        inputs = {
            'email_content': email_input
        }
        PrescriptionWorkflow().crew().kickoff(inputs=inputs)

        break

if __name__ == '__main__':
    run()


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         PrescriptionWorkflow().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         PrescriptionWorkflow().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         PrescriptionWorkflow().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")
