from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

class rainReportModel(BaseModel):
  reportTime: datetime
  reportDistrict: int
  rainStatus: str
  rainArea: str

class rainReportsCollection: 
  def __init__(self, db):
    self.collection = db['rainreports']

  def create_rain_report(self, reportTime, reportDistrict, rainStatus, rainArea):
    report_data = rainReportModel(reportTime=reportTime, reportDistrict=reportDistrict, rainStatus=rainStatus, rainArea=rainArea).model_dump()
    result = self.collection.insert_one(report_data)
    return result.inserted_id
  
  def delete_reports_older_than_7_days(self):
    seven_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
    self.collection.delete_many({'reportTime': {'$lt': seven_days_ago}})
