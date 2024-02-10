from fastapi import FastAPI
from database.mongo_connection import MongoConnection
from image_processing.image_fetcher import ImageFetcher
from image_processing.image_cropper import ImageCropper
from image_processing.color_detector import ColorDetector
# from image_processing.text_detector import TextDetector
import numpy as np
from database.models.rain_report_collection import rainReportsCollection
from datetime import datetime
from decouple import config
import schedule
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
        # target_word_1 = "ปรับปรุง"
        # target_word_2 = "=ชั่วคราว"
        # text_detector = TextDetector(image_buffer=radar_image)

        # if text_detector.check_target_text(target_text=target_word_1) or text_detector.check_target_text(target_text=target_word_2):
        #     print("Radar is maintaining...")
        # else:
        #     print("Radar is fine")
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

# schedule.every(300).seconds.do(detect_rain)

# while True:
#     schedule.run_pending()
#     time.sleep(1)
    
# def startup_event():
#     current_time = datetime.now().time()
    
from datetime import datetime, timedelta
from threading import Timer
from time import sleep
import random

def schedule_next_run():
    sleep_time = get_sleep_time()
    t = Timer(sleep_time, do_work)
    t.daemon = True
    t.start()

def get_sleep_time():
    now = datetime.now()
    last_run_time = now.replace(minute=now.minute // 5 * 5, second=0, microsecond=0)
    next_run_time = last_run_time + timedelta(minutes=5)
    return (next_run_time - now).total_seconds()

def do_work():
    now = datetime.now()
    detect_rain()
    sleep(random.uniform(0, 29))
    schedule_next_run()

schedule_next_run()