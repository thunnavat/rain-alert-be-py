from pymongo import MongoClient
from decouple import config

class MongoConnection:
  def __init__(self, db_name, username=None, password=None, host='localhost', port=config("MONGO_PORT", default="27017")):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = self._create_connection()

  def _create_connection(self):
      if self.username and self.password:
          connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"
      else:
          connection_string = f"mongodb://{self.host}:{self.port}/{self.db_name}"

      return MongoClient(connection_string)

  def get_database(self):
      return self.client[self.db_name]

  def close_connection(self):
      self.client.close()