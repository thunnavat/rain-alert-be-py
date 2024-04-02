from pymongo import MongoClient

class userCollection:
    def __init__(self, db):
        self.collection = db['users']

    def get_users_by_district_subscribe(self, district):
        return self.collection.find({"districtSubscribe": {"$in": [district]}})