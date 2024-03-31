import cv2
import numpy as np

class ColorDetector:
    def __init__(self, image_buffer, total_pixel):
        # แปลง image buffer เป็น NumPy array
        nparr = np.frombuffer(image_buffer, np.uint8)
        self.image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.totalPixel = total_pixel

    def detect_color(self, lower, upper):
        mask = cv2.inRange(self.hsv, lower, upper)
        pixel_count = cv2.countNonZero(mask)
        return pixel_count
    
    def get_rain_area(self, total_rain_pixel):
         # พื้นที่ของฝนที่ตก
        one_percent_of_area = 0.01 * self.totalPixel
        twenty_percent_of_area = 0.2 * self.totalPixel
        fourty_percent_of_area = 0.4 * self.totalPixel
        sixty_percent_of_area = 0.6 * self.totalPixel
        eighty_percent_of_area = 0.8 * self.totalPixel

        if one_percent_of_area < total_rain_pixel < twenty_percent_of_area:
            return 'ISOLATED'
        elif twenty_percent_of_area <= total_rain_pixel < fourty_percent_of_area:
            return 'WIDELY SCATTERED'
        elif fourty_percent_of_area <= total_rain_pixel < sixty_percent_of_area:
            return 'SCATTERED'
        elif sixty_percent_of_area <= total_rain_pixel < eighty_percent_of_area:
            return 'ALMOST WIDESPREAD'
        elif total_rain_pixel >= eighty_percent_of_area:
            return 'WIDESPREAD'
        else:
            return ''


    def get_rain_intensity(self):
        # กำหนดช่วงสีสำหรับแต่ละสี
        lower_green = np.array([40, 117, 89])
        upper_green = np.array([80, 255, 255])
        lower_yellow = np.array([19, 100, 100])
        upper_yellow = np.array([40, 255, 255])
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([19, 255, 255])

        # นับจำนวนพิกเซลในแต่ละ mask
        green_pixel_count = self.detect_color(lower_green, upper_green)
        yellow_pixel_count = self.detect_color(lower_yellow, upper_yellow)
        red_pixel_count = self.detect_color(lower_red, upper_red)

        # กำหนดค่าระดับการฝน
        one_percent_of_area = 0.01 * self.totalPixel
        if red_pixel_count > yellow_pixel_count and red_pixel_count > green_pixel_count and red_pixel_count > one_percent_of_area:
            rain_area = self.get_rain_area(total_rain_pixel=red_pixel_count+yellow_pixel_count+green_pixel_count)
            return {'rainStatus': 'HEAVY RAIN', 'rainArea': rain_area}
        elif (yellow_pixel_count > green_pixel_count or (yellow_pixel_count + red_pixel_count) > green_pixel_count) and yellow_pixel_count > one_percent_of_area:
            rain_area = self.get_rain_area(total_rain_pixel=red_pixel_count+yellow_pixel_count+green_pixel_count)
            return {'rainStatus': 'MODERATE RAIN', 'rainArea': rain_area}
        else:
            rain_area = self.get_rain_area(total_rain_pixel=red_pixel_count+yellow_pixel_count+green_pixel_count)
            return {'rainStatus': 'LIGHT RAIN', 'rainArea': rain_area} if green_pixel_count > one_percent_of_area else {'rainStatus': 'NO RAIN', 'rainArea': rain_area}