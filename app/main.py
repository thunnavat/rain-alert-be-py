from fastapi import FastAPI
from database.mongo_connection import MongoConnection
from image_processing.image_fetcher import ImageFetcher
from image_processing.image_cropper import ImageCropper
from image_processing.color_detector import ColorDetector
from image_processing.text_detector import TextDetector
import numpy as np
from database.models.rain_report_collection import rainReportsCollection
from datetime import datetime
from decouple import config
import time
import threading

app = FastAPI()

def detect_rain():
    # # Connect to MongoDB
    mongo_connection = MongoConnection(
        db_name= config('MONGO_DBNAME'),
        username = config('MONGO_USERNAME'),
        password = config('MONGO_PASSWORD'),
        host= config('MONGO_HOST_DEV') if config('MODE', default='dev') == 'dev' else config('MONGO_HOST_PROD'),
    )
    db = mongo_connection.get_database()
    
    # Fetch radar image from URL
    radar_image = ImageFetcher(url='https://weather.bangkok.go.th/Images/Radar/radarh.jpg').get_image()



    districts = db['districts'].find()

    if radar_image:
        target_word_1 = "ขออภัยในความไม่สะดวก"
        target_word_2 = "อยู่ระหว่างการซ่อมบํารุง"
        text_detector = TextDetector(image_buffer=radar_image)

        if text_detector.check_target_text(target_text=target_word_1) or text_detector.check_target_text(target_text=target_word_2):
            print("Radar is maintaining...")
        else:
            print("Radar is fine")
            if districts:
                for district in districts:
                    image_cropper = ImageCropper(image_buffer=radar_image)
                    cropped_image = image_cropper.crop_polygon(polygon_vertices=np.array(district['coords']))
                    color_detector = ColorDetector(image_buffer=cropped_image, total_pixel=district['totalPixel'])
                    rain_result = color_detector.get_rain_intensity()
                    rain_report = rainReportsCollection(db=db)
                    rain_report.create_rain_report(reportTime=datetime.now(), reportDistrict=district['_id'], rainStatus=rain_result['rainStatus'], rainArea=rain_result['rainArea'])
                    # print("Rain report created for district: " + str(district['_id']))
            else: 
                print("Cannot find districts collection")
    else:
        print("Cannot fetch radar image")

    # Close MongoDB connection when done
    mongo_connection.close_connection()

def delete_reports_older_than_7_days():
    # Connect to MongoDB
    mongo_connection = MongoConnection(
        db_name= config('MONGO_DBNAME'),
        username = config('MONGO_USERNAME'),
        password = config('MONGO_PASSWORD'),
        host= config('MONGO_HOST_DEV') if config('MODE', default='dev') == 'dev' else config('MONGO_HOST_PROD'),
    )
    db = mongo_connection.get_database()
    rain_report = rainReportsCollection(db=db)
    rain_report.delete_reports_older_than_7_days()
    # Close MongoDB connection when done
    mongo_connection.close_connection()

def schedule_task():
    while True:
        current_hour = int(time.strftime("%H"))
        current_minute = int(time.strftime("%M"))
        # Execute midnight task if current time is midnight
        if current_hour == 0 and current_minute == 0:
            delete_reports_older_than_7_days()  # Execute the midnight task
            
        if current_minute % 5 == 0:
            # เรียกใช้งาน detect_rain() ในเทรดใหม่เพื่อให้ไม่บล็อกการทำงานของ schedule_task()
            threading.Thread(target=detect_rain).start()
        # คำนวณเวลาที่เหลือจนถึงนาทีที่ลงท้ายด้วย 0 ใกล้ที่สุดแล้วรอจนกว่าจะถึงเวลานั้น
        time.sleep((5 - (current_minute % 5)) * 60)

schedule_task()