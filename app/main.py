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
import asyncio
import pytz

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

# # Background task to run the job at startup and then at intervals
# async def run_scheduled_job():
#     while True:
#         await detect_rain()
#         await asyncio.sleep(300)  # Sleep for 5 minutes

# # Event handler for startup
# @app.on_event("startup")
# async def startup_event():
#     # Get the UTC timezone object
#     utc_timezone = pytz.utc

#     # Specify the desired timezone (UTC+7)
#     desired_timezone = pytz.timezone('Asia/Bangkok')  # Adjust this based on your actual timezone

#     # Check the current time in UTC
#     current_time_utc = datetime.utcnow().replace(tzinfo=utc_timezone)

#     # Convert the current time to the desired timezone
#     current_time_desired_timezone = current_time_utc.astimezone(desired_timezone)

#     # Specify the desired start time in the desired timezone (e.g., 10:50 PM)
#     desired_start_time = current_time_desired_timezone.replace(hour=16, minute=10, second=0, microsecond=0)

#     # Calculate the delay until the desired start time
#     delay = (desired_start_time - current_time_desired_timezone).total_seconds()

#     # If the current time is after the desired start time, run the job immediately
#     if delay < 0:
#         await run_scheduled_job()
#     else:
#         # Otherwise, run the job after the calculated delay
#         await asyncio.sleep(delay)
#         await run_scheduled_job()

import schedule
import time
from datetime import datetime, timedelta, timezone

# Set your desired start time in UTC+7
start_time_utc7 = "12:30"  # Include seconds in HH:MM format with :00 for seconds

# Convert the start time to a datetime object with the UTC+7 timezone
start_time_utc7_dt = datetime.strptime(start_time_utc7, "%H:%M").replace(tzinfo=timezone(timedelta(hours=7)))

# Calculate the initial delay until the next 5-minute interval
current_time_utc7 = datetime.now(timezone(timedelta(hours=7)))
initial_delay = (start_time_utc7_dt - current_time_utc7) % timedelta(minutes=5)
initial_delay_seconds = initial_delay.total_seconds()

# Schedule the function to run every 5 minutes
schedule.every(5).minutes.do(detect_rain).tag('repeating_task')

# Wait for the initial delay before starting the loop
time.sleep(initial_delay_seconds)

while True:
    # Run the scheduled tasks
    schedule.run_pending()
    # Sleep for a short time to avoid high CPU usage
    time.sleep(1)