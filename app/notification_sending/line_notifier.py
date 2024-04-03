import requests
import logging

class LineNotifier:
    def __init__(self, access_token):
        self.access_token = access_token

    def send_notification(self, message):
        try:
            url = 'https://notify-api.line.me/api/notify'
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            payload = {
                'message': message,
            }
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code == 200:
                print('Notification sent successfully!')
            else:
                logging.error(f'Failed to send notification. Status code: {response.status_code}')
        except Exception as e:
            logging.error(f'An error occurred while sending notification: {str(e)}')