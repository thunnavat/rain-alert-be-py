from pydantic import BaseModel
from datetime import datetime

class rainReportModel(BaseModel):
  reportTime: datetime
  reportDistrict: int
  reportStatus: bool

class rainReportsCollection: 
  def __init__(self, db):
    self.collection = db['rain_reports']

  def create_rain_report(self, rain_report: rainReportModel):
    return self.collection.insert_one(rain_report.model_dump())