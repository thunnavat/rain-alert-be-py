from fastapi import FastAPI, BackgroundTasks
from database.mongo_connection import MongoConnection
from image_processing.image_fetcher import ImageFetcher
from image_processing.image_cropper import ImageCropper
from image_processing.color_detector import ColorDetector
import numpy as np
from database.models.rain_report_collection import rainReportsCollection
from datetime import datetime
from decouple import config
import asyncio
import pytz

app = FastAPI()

async def detect_rain():
    # # Connect to MongoDB
    mongo_connection = MongoConnection(
        db_name='rainalert',
        username = config("MONGO_USERNAME"),
        password = config("MONGO_PASSWORD"),
        host='cp23tt3.sit.kmutt.ac.th',
    )
    db = mongo_connection.get_database()
    
    # Fetch radar image from URL
    radar_image = ImageFetcher(url='https://weather.bangkok.go.th/Images/Radar/radarh.jpg').get_image()

    districts = db['districts'].find()

    if districts:
        for district in districts:
            image_cropper = ImageCropper(image_buffer=radar_image)
            cropped_image = image_cropper.crop_polygon(polygon_vertices=np.array(district['coords']))
            color_detector = ColorDetector(image_buffer=cropped_image)
            rain_report = rainReportsCollection(db=db)
            rain_report.create_rain_report(reportTime=datetime.now(), reportDistrict=district['_id'], rainStatus=color_detector.get_rain_intensity())
    else: 
        print("Cannot find districts collection")

    # Close MongoDB connection when done
    mongo_connection.close_connection()

# Background task to run the job at startup and then at intervals
async def run_scheduled_job():
    while True:
        await detect_rain()
        await asyncio.sleep(300)  # Sleep for 5 minutes

# Event handler for startup
@app.on_event("startup")
async def startup_event():
    # Get the UTC timezone object
    utc_timezone = pytz.utc

    # Specify the desired timezone (UTC+7)
    desired_timezone = pytz.timezone('Asia/Bangkok')  # Adjust this based on your actual timezone

    # Check the current time in UTC
    current_time_utc = datetime.utcnow().replace(tzinfo=utc_timezone)

    # Convert the current time to the desired timezone
    current_time_desired_timezone = current_time_utc.astimezone(desired_timezone)

    # Specify the desired start time in the desired timezone (e.g., 10:50 PM)
    desired_start_time = current_time_desired_timezone.replace(hour=0, minute=10, second=0, microsecond=0)

    # Calculate the delay until the desired start time
    delay = (desired_start_time - current_time_desired_timezone).total_seconds()

    # If the current time is after the desired start time, run the job immediately
    if delay < 0:
        await run_scheduled_job()
    else:
        # Otherwise, run the job after the calculated delay
        await asyncio.sleep(delay)
        await run_scheduled_job()

