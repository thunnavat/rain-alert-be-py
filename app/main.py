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
        target_word_1 = "ปรับปรุง"
        target_word_2 = "ชั่วคราว"
        target_word_3 = "หยุดการให้บริการ"
        target_word_4 = "maintenance"
        text_detector = TextDetector(image_buffer=radar_image)

        if text_detector.check_target_text(target_text=target_word_1) or text_detector.check_target_text(target_text=target_word_2) or text_detector.check_target_text(target_text=target_word_3) or text_detector.check_target_text(target_text=target_word_4):
            print("Radar is maintaining...")
        else:
            print("Radar is fine")
            if districts:
                for district in districts:
                    image_cropper = ImageCropper(image_buffer=radar_image)
                    cropped_image = image_cropper.crop_polygon(polygon_vertices=np.array(district['coords']))
                    color_detector = ColorDetector(image_buffer=cropped_image)
                    rain_report = rainReportsCollection(db=db)
                    rain_report.create_rain_report(reportTime=datetime.now(), reportDistrict=district['_id'], rainStatus=color_detector.get_rain_intensity())
                    # print("Rain report created for district: " + str(district['_id']))
            else: 
                print("Cannot find districts collection")
    else:
        print("Cannot fetch radar image")

    # Close MongoDB connection when done
    mongo_connection.close_connection()

def schedule_task():
    while True:
        current_minute = int(time.strftime("%M"))
        if current_minute % 5 == 0 or current_minute % 5 == 5:
            detect_rain()
        time.sleep((5 - (current_minute % 5)) * 60)

schedule_task()