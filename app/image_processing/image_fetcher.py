import requests
import cv2
import numpy as np

class ImageFetcher:
    def __init__(self, url):
        self.url = url

    def get_image(self):
        try:
            # Make a request to the URL
            response = requests.get(self.url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Convert the image data to a NumPy array using OpenCV
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)

                # Read the image using OpenCV
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                # Convert the image to bytes
                success, image_buffer = cv2.imencode('.jpg', image)

                if success:
                    return image_buffer.tobytes()
                else:
                    print("Failed to encode image to bytes")
                    return None

            else:
                print(f"Failed to fetch image. Status code: {response.status_code}")
                return None

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None