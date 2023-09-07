from flask import Flask, request
import requests
import json
import pymongo
app = Flask(__name__)
ERR_STATUS, OK_STATUS = 409, 200
counter = 1
diets = []
client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["meal_diets"]
collection = db["diets"]
if collection.find_one({"_id": 0}) is None:
    collection.insert_one({"_id": 0, "curr_key": 0})
    print("inserted key")


@app.route('/diets', methods=['POST'])
def post_diets_from_user():
    global counter
    try:
        json_string = json.dumps(request.get_json(), indent=4)
    except:
        return "POST expects content type to be application/json", 415
    # print(json_string)
    data = json.loads(json_string)
    try:
        name = data['name']
        calories = data['cal']
        sodium = data['sodium']
        sugar = data['sugar']
    except:
        return "Incorrect POST format", 422

    diets = collection.find_one({"name": name})
    if diets is not None:
        return f"Diet with {name} already exists", 422
    docID = {"_id": 0}
    curr_key = collection.find_one(docID)["curr_key"] + 1
    collection.update_one(docID, {"$set": {"curr_key": curr_key}})
    collection.insert_one({"_id": curr_key, "name": name,
                          "cal": calories, "sodium": sodium, "sugar": sugar})
    return f"Diet {name} was created successfully", 201


@app.route('/diets', methods=['GET'])
def get_diet():
    cursor = collection.find({"_id": {"$gte": 1}})
    cursor.rewind()
    cursor = list(cursor)
    cursor = json.dumps(cursor, indent=4)
    return cursor, OK_STATUS


@app.route('/diets/<string:name>', methods=['GET'])
def get_diet_by_name(name):
    res = collection.find_one({"name": name})
    if res is None:
        return f"Diet {name} not found", 404
    else:
        return json.dumps(res, indent=4), OK_STATUS


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
