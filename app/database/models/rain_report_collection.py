from pydantic import BaseModel
from datetime import datetime

class rainReportModel(BaseModel):
  reportTime: datetime
  reportDistrict: int
  rainStatus: str

class rainReportsCollection: 
  def __init__(self, db):
    self.collection = db['rainreports']

  def create_rain_report(self, reportTime, reportDistrict, rainStatus):
    report_data = rainReportModel(reportTime=reportTime, reportDistrict=reportDistrict, rainStatus=rainStatus).model_dump()
    result = self.collection.insert_one(report_data)
    return result.inserted_id