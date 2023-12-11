import cv2
import numpy as np
import pytesseract
from decouple import config

class TextDetector:
    def __init__(self, image_buffer, languages=['eng', 'tha']):
        self.image_buffer = image_buffer
        self.languages = languages
        self.tesseract_cmd = r'' + config('TESSERACT_CMD_DEV') if config('MODE', default='dev') == 'dev' else config('TESSERACT_CMD_PROD')

    def detect_text(self):
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        nparr = np.frombuffer(self.image_buffer, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        text = pytesseract.image_to_string(img, lang='+'.join(self.languages))
        return text

    def check_target_text(self, target_text):
        detected_text = self.detect_text()
        return target_text.lower() in detected_text.lower()