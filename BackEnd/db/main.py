from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["heta"]
collection = db["series_flat"]

# Print 5 example records
for doc in collection.find().limit(5):
    print(doc)
