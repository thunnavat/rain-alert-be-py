import cv2
import numpy as np

class ColorDetector:
    def __init__(self, image_buffer):
        # แปลง image buffer เป็น NumPy array
        nparr = np.frombuffer(image_buffer, np.uint8)
        self.image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

    def detect_color(self, lower, upper):
        mask = cv2.inRange(self.hsv, lower, upper)
        pixel_count = cv2.countNonZero(mask)
        return pixel_count

    def get_rain_intensity(self):
        # กำหนดช่วงสีสำหรับแต่ละสี
        # lower_green = np.array([40, 40, 40])
        # upper_green = np.array([80, 255, 255])
        lower_green = np.array([18,117,89])
        upper_green = np.array([80,255,255])
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])

        # นับจำนวนพิกเซลในแต่ละ mask
        green_pixel_count = self.detect_color(lower_green, upper_green)
        yellow_pixel_count = self.detect_color(lower_yellow, upper_yellow)
        red_pixel_count = self.detect_color(lower_red, upper_red)

        # กำหนดค่าระดับการฝน
        if red_pixel_count > yellow_pixel_count and red_pixel_count > green_pixel_count:
            return 'HEAVY RAIN'
        elif yellow_pixel_count > green_pixel_count:
            return 'MODERATE RAIN'
        else:
            return 'LIGHT RAIN' if green_pixel_count > 0 else 'NO RAIN'