from pymongo import MongoClient, errors
import json
import datetime
import asyncio

# case = {
#     "name": "Daniel",
#     "chat_id": "1234",
#     "message": "Las cosas no funcionan",
#     "date": datetime.datetime.utcnow(),
#     "active": True
# }

client = MongoClient('localhost', 27017)
db = client["Lab"]

cases = db.cases


# post_id = posts.insert_one(case).inserted_id
# print(post_id)

async def close_case_countdown(case_id):
    print("COUNTDOWN STARTED")
    await asyncio.sleep(10)
    # get the case
    case = cases.find_one({"_id": case_id})
    time_difference = datetime.datetime.utcnow() - case["last_update"]
    if time_difference.total_seconds() > 10:
        cases.update_one({"_id": case_id}, {"$set": {"active": False}})
        print("Case closed")
    else:
        print("Case still active")


async def manage_message(payload):
    # get the last message from the user if it exists
    last_case = cases.find_one({"number": payload["from"]}, sort=[("creation_date", -1)])
    print(last_case)
    if last_case is None:
        print("Case doesn't exist")
        case_id = create_case(payload)
        await close_case_countdown(case_id)
        return

    time_difference = datetime.datetime.utcnow() - last_case["creation_date"]
    print(time_difference.total_seconds())
    if time_difference.total_seconds() > 10 or last_case["active"] is False:
        create_case(payload)
        return
    else:
        print("Case already exists")

    # update last update date
    cases.update_one({"_id": last_case["_id"]}, {"$set": {"last_update": datetime.datetime.utcnow()}})
    # start countdown
    await close_case_countdown(last_case["_id"])


def create_case(payload):
    case = {
        "name": payload["_data"]["notifyName"],
        "number": payload["from"],
        "message": payload["body"],
        "creation_date": datetime.datetime.utcnow(),
        "last_update": datetime.datetime.utcnow(),
        "active": True
    }
    try:
        return cases.insert_one(case).inserted_id
    except errors.DuplicateKeyError:
        print("Case already exists")
