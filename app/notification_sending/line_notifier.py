import requests

class LineNotifier:
    def __init__(self, access_token):
        self.access_token = access_token

    def send_notification(self, message):
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
            print(f'Failed to send notification. Status code: {response.status_code}')