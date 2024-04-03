from fastapi import FastAPI
from database.mongo_connection import MongoConnection
from image_processing.image_fetcher import ImageFetcher
from image_processing.image_cropper import ImageCropper
from image_processing.color_detector import ColorDetector
from image_processing.text_detector import TextDetector
import numpy as np
from database.models.rain_report_collection import rainReportsCollection
from database.models.user_collection import userCollection
from notification_sending.email_sender import EmailSender
from notification_sending.line_notifier import LineNotifier
from datetime import datetime
from decouple import config
import time
import threading
import cv2

app = FastAPI()

def notification_sender(district, rain_status):
    # Connect to MongoDB
    mongo_connection = MongoConnection(
        db_name= config('MONGO_DBNAME'),
        username = config('MONGO_USERNAME'),
        password = config('MONGO_PASSWORD'),
        host= config('MONGO_HOST_DEV') if config('MODE', default='dev') == 'dev' else config('MONGO_HOST_PROD'),
    )
    db = mongo_connection.get_database()
    user = userCollection(db=db)
    users = user.get_users_by_district_subscribe(district)
    if users:
        for user in users:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%d-%m-%Y %H:%M")
            report_message = f"รายงานฝนตกในเขต {district} ณ เวลา {formatted_datetime} มีฝนตก {rain_status} ในพื้นที่"
            if user['notificationByEmail']:
                print(f"Sending email to {user['email']}")
                email_sender = EmailSender("supphakorn.praisakuldecha@mail.kmutt.ac.th", "Kuroba__1412")
                email_sender.send_email(user['email'], f"Rainfall Report of {district} by RainAlert", report_message)
            if user['notificationByLine']:
                print(f"Sending notification to {user['email']}")
                line_notifier = LineNotifier(user['notifyToken'])
                line_notifier.send_notification(report_message)
    else:
        print("No users subscribe to this district")
    # Close MongoDB connection when done
    mongo_connection.close_connection()

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
    # image = cv2.imread('radarh.jpg')
    # success, buffer = cv2.imencode(".jpg", image)
    # radar_image = buffer.tobytes()

    districts = db['districts'].find()

    if radar_image:
        target_word_1 = "ขออภัยในความไม่สะดวก"
        target_word_2 = "อยู่ระหว่างการซ่อมบํารุง"
        text_detector = TextDetector(image_buffer=radar_image)
        
        if not text_detector.check_target_text(target_text=target_word_1) or not text_detector.check_target_text(target_text=target_word_2):
            print("Radar is fine")
            if districts:
                for district in districts:
                    image_cropper = ImageCropper(image_buffer=radar_image)
                    cropped_image = image_cropper.crop_polygon(polygon_vertices=np.array(district['coords']))
                    if cropped_image:
                        color_detector = ColorDetector(image_buffer=cropped_image, total_pixel=district['totalPixel'])
                        rain_result = color_detector.get_rain_intensity()
                        rain_report = rainReportsCollection(db=db)
                        rain_report.create_rain_report(reportTime=datetime.now(), reportDistrict=district['_id'], rainStatus=rain_result['rainStatus'], rainArea=rain_result['rainArea'])
                        if rain_result['rainStatus'] != "NO RAIN":
                            notification_sender(district=district['districtName'], rain_status=rain_result['rainStatus'])
                        # print("Rain report created for district: " + str(district['_id']))
                    else:
                        print("Cannot crop image")
            else: 
                print("Cannot find districts collection")
        else:
            print("Radar is maintaining...")            
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
        if current_hour == 17 and current_minute == 0:
            threading.Thread(target=delete_reports_older_than_7_days).start()
            
        if current_minute % 5 == 0:
            # เรียกใช้งาน detect_rain() ในเทรดใหม่เพื่อให้ไม่บล็อกการทำงานของ schedule_task()
            threading.Thread(target=detect_rain).start()
        # คำนวณเวลาที่เหลือจนถึงนาทีที่ลงท้ายด้วย 0 ใกล้ที่สุดแล้วรอจนกว่าจะถึงเวลานั้น
        time.sleep((5 - (current_minute % 5)) * 60)

schedule_task()
    
# detect_rain()