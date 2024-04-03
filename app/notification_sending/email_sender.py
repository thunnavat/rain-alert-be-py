import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

class EmailSender:
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_email(self, receiver_email, subject, message):
        try:
            # Set up the MIME
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            # Attach message
            msg.attach(MIMEText(message, 'plain'))

            # Connect to the SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            # Login to the sender email account
            server.login(self.sender_email, self.sender_password)

            # Send the email
            server.sendmail(self.sender_email, receiver_email, msg.as_string())

            # Close the connection
            server.quit()
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")