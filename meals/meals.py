from flask import Flask, request
import requests
import json
import pymongo
app = Flask(__name__)
ERR_STATUS, OK_STATUS = 409, 200

X_Api_key = '7+4oMBnrMSKOOU1Ck62Pvg==2O3G4LxAIbnXo8Ms'

dishes = []
meals = []
client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["meal_diets"]
meals_collection = db["meals"]
if meals_collection.find_one({"_id": 0}) is None:
    meals_collection.insert_one({"_id": 0, "curr_key": 0})
    print("inserted key")

dishes_collection = db["dishes"]
if dishes_collection.find_one({"_id": 0}) is None:
    dishes_collection.insert_one({"_id": 0, "curr_key": 0})
    print("inserted key")


@app.route('/dishes', methods=['POST'])
def post_dish_from_user():

    try:
        json_string = json.dumps(request.get_json(), indent=4)
    except:
        return str(0), 415

    data = json.loads(json_string)
    try:
        name = data['name']

    except:
        return str(-1), 400

    dish_data = get_ninja_api(name)
    if dish_data == "Error":
        return str(-4), 400
    if dish_data == "empty":
        return str(-3), 400

    dishes = dishes_collection.find_one({"name": name})
    if dishes:
        return str(-2), 400
    else:
        docID = {"_id": 0}
        curr_key = dishes_collection.find_one(docID)["curr_key"] + 1
        dishes_collection.update_one(docID, {"$set": {"curr_key": curr_key}})
        dishes_collection.insert_one({"_id": curr_key, "name": name, "cal": dish_data["calories"],
                                      "size": dish_data["serving_size_g"], "sodium": dish_data["sodium_mg"], "sugar": dish_data["sugar_g"]})

        return str(curr_key), 201


@app.route('/dishes/<int:_id>', methods=['GET'])
def get_dish_by__id(_id):

    dishes = dishes_collection.find_one({"_id": _id})
    if dishes is not None:
        return str(-5), 404
    else:
        return json.dumps(dishes, indent=4), OK_STATUS


@app.route('/dishes/<string:name>', methods=['GET'])
def get_dish_by_name(name):

    dishes = dishes_collection.find_one({"name": name})
    if dishes is not None:
        return str(-5), 404
    else:
        return json.dumps(dishes, indent=4), OK_STATUS


@app.route('/dishes', methods=['DELETE'])
def err_delete():
    return str(-5), 404


@app.route('/dishes', methods=['GET'])
def get_all_dishes():
    cursor = dishes_collection.find({"_id": {"$gte": 1}})
    cursor.rewind()
    cursor = list(cursor)
    cursor = json.dumps(cursor, indent=4)
    return cursor, OK_STATUS


@app.route('/dishes/<string:name>', methods=['DELETE'])
def delete_dish_by_name(name):
    dish = dishes_collection.find_one({'name': name})
    if dish:
        dishes_collection.delete_one({'name': name})
        return str(name), OK_STATUS
    else:
        return str(-5), 404


@app.route('/dishes/<int:_id>', methods=['DELETE'])
def delete_dish_by__id(_id):
    dish = dishes_collection.find_one({'_id': _id})
    if dish:
        dishes_collection.delete_one({'_id': _id})
        return str(_id), OK_STATUS
    else:
        return str(-5), 404


def is_dish_already_exist(name):
    dish = dishes_collection.find_one({'name': name})
    if dish:
        return -2
    return 0
#query = '1lb brisket and fries'


def get_ninja_api(query):
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
    response = requests.get(api_url, headers={'X-Api-Key': X_Api_key})
    if response.status_code == requests.codes.ok:
        print(response.text)
        if response.text == "[]":
            return "empty"
        return make_dish(json.loads(response.text))
    else:
        print("Error:", response.status_code, response.text)
        return "Error"


def make_dish(dishes_arrary):
    res_dish = {"calories": 0, "serving_size_g": 0,
                "sodium_mg": 0, "sugar_g": 0}
    for dish in dishes_arrary:
        res_dish["calories"] += dish["calories"]
        res_dish["serving_size_g"] += dish["serving_size_g"]
        res_dish["sodium_mg"] += dish["sodium_mg"]
        res_dish["sugar_g"] += dish["sugar_g"]

    return res_dish


@app.route('/meals', methods=['POST'])
def post_meal_from_user():

    try:
        json_string = json.dumps(request.get_json(), indent=4)
    except:
        return str(0), 415

    data = json.loads(json_string)
    try:
        meal_name = data["name"]
        appetizer = int(data["appetizer"])
        main = int(data["main"])
        dessert = int(data["dessert"])
    except:
        return str(-1), 400
    meals = meals_collection.find_one({'name': meal_name})
    if meals is not None:
        return str(-2), 400
    meal_obj = {}
    meal__id = [appetizer, main, dessert]
    match = 0
    for i in meal__id:
        dish = dishes_collection.find_one({'_id': i})
        if dish is not None:
            meal_obj[i] = dish
            match += 1

    if match != 3:
        return str(-5), 400
    docID = {"_id": 0}
    curr_key = meals_collection.find_one(docID)["curr_key"] + 1
    meals_collection.update_one(docID, {"$set": {"curr_key": curr_key}})
    meals_collection.insert_one({
        "name": meal_name, "_id": curr_key, "appetizer": appetizer, "main": main, "dessert": dessert,
        "cal": meal_obj[appetizer]["cal"] + meal_obj[main]["cal"] + meal_obj[dessert]["cal"],
        "size": meal_obj[appetizer]["size"] + meal_obj[main]["size"] + meal_obj[dessert]["size"],
        "sodium": meal_obj[appetizer]["sodium"] + meal_obj[main]["sodium"] + meal_obj[dessert]["sodium"],
        "sugar": meal_obj[appetizer]["sugar"] + meal_obj[main]["sugar"] + meal_obj[dessert]["sugar"]})

    return str(curr_key), 201


def add_meal_by_id(_id, json_string):

    data = json.loads(json_string)
    try:
        meal_name = data["name"]
        appetizer = int(data["appetizer"])
        main = int(data["main"])
        dessert = int(data["dessert"])
    except:
        return str(-1), 400
    for meal in meals:
        if meal_name == meal["name"]:
            return str(-2), 400
    meal_obj = {}
    meal__id = [appetizer, main, dessert]
    match = 0
    for i in meal__id:
        dish = dishes_collection.find_one({'_id': i})
        if dish is not None:
            meal_obj[i] = dish
            match += 1

    if match != 3:
        return str(-5), 400

    meal = {"name": meal_name, "_id": _id, "appetizer": appetizer, "main": main, "dessert": dessert,
            "cal": meal_obj[appetizer]["cal"] + meal_obj[main]["cal"] + meal_obj[dessert]["cal"],
            "size": meal_obj[appetizer]["size"] + meal_obj[main]["size"] + meal_obj[dessert]["size"],
            "sodium": meal_obj[appetizer]["sodium"] + meal_obj[main]["sodium"] + meal_obj[dessert]["sodium"],
            "sugar": meal_obj[appetizer]["sugar"] + meal_obj[main]["sugar"] + meal_obj[dessert]["sugar"]}
    result = meals_collection.update_one({'_id': _id}, {'$set': meal})

    if result.modified_count > 0:
        return str(_id), 200
    else:
        return str(-2), 404


@app.route('/meals', methods=['GET'])
def get_meals():
    query_params = request.args
    if len(query_params) == 0:
        meals = list(meals_collection.find({"_id": {"$gte": 1}}))
        return json.dumps(meals, indent=4), OK_STATUS

    url = 'http://172.17.0.1:5002/diets/'+str(query_params['diet'])
    print(url)
    response = requests.get(url)
    print(response)

    # Access the response from the other server if needed
    response_data = response.json()
    if response.status_code == 404:  # to fix
        return str(-5), 400
    meals = list(meals_collection.find({"_id": {"$gte": 1}}))
    res = []

    for meal in meals:
        if meal["cal"] <= response_data["cal"] and meal["sodium"] <= response_data["sodium"] and meal["sugar"] <= response_data["sugar"]:
            res.append(meal)

    return json.dumps(res, indent=4), OK_STATUS


@app.route('/meals/<int:_id>', methods=['GET'])
def get_meal_by__id(_id):

    if len(meals) < _id:
        return str(-5), 404
    meal = meals_collection.find_one({"_id": _id})
    if meal is not None:
        return json.dumps(meal, indent=4), OK_STATUS

    return str(-5), 404


@app.route('/meals/<int:_id>', methods=['DELETE'])
def delete_meal_by__id(_id):
    result = meals_collection.delete_one({'_id': _id})

    if result.deleted_count > 0:
        return str(_id), 200
    else:
        return str(-5), 404


@app.route('/meals/<int:_id>', methods=['PUT'])
def put_meal_by__id(_id):
    json_string = json.dumps(request.get_json(), indent=4)
    return add_meal_by_id(_id, json_string)


@app.route('/meals/<string:name>', methods=['GET'])
def get_meal_by_name(name):
    meal = meals_collection.find_one({"name": name})
    if meal is not None:
        return json.dumps(meal, indent=4), 200
    else:
        return str(-5), 404


@app.route('/meals/<string:name>', methods=['DELETE'])
def delete_meal_by_name(name):
    result = meals_collection.delete_one({'name': name})

    if result.deleted_count > 0:
        return str(name), 200
    else:
        return str(-5), 404


@app.route('/meals', methods=['DELETE'])
def delete_meals():
    return str(-5), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
