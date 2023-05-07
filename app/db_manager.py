from pymongo import MongoClient, errors
import json
import datetime
import asyncio
import logging
import os
import pandas as pd

from wahaAPI import send_safe_message
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# case = {
#     "name": "Daniel",
#     "chat_id": "1234",
#     "message": "Las cosas no funcionan",
#     "date": datetime.datetime.utcnow(),
#     "active": True
# }

client = MongoClient(os.getenv("DB_HOST", "localhost"), int(os.getenv("DB_PORT", "27017")))
db = client["Lab"]

cases = db.cases
lab_data = json.load(open('support_data.json', 'r'))  # TODO: migrate to db


# post_id = posts.insert_one(case).inserted_id
# print(post_id)
def solicitude_handler(name, message):
    # TODO: migrate to db
    return f"Nueva solicitud de: {name}\n\n{message}."


async def manage_message(payload):
    # get the last message from the user if it exists
    last_case = cases.find_one({"number": payload["from"]}, sort=[("creation_date", -1)])
    print(last_case)
    if last_case is not None:
        if last_case["active"] is True:
            logging.info("ACTIVE CASE MESSAGE RECEIVED")
            await send_safe_message(payload["from"], payload["id"], payload.get('participant'), "open case", True)
            print("Case already exists")
        else:
            print("Case doesn't exist")
            await create_case(payload)
            return
    else:
        print("Case doesn't exist")
        await create_case(payload)
        return

    # update last update date
    cases.update_one({"_id": last_case["_id"]}, {"$set": {"last_update": datetime.datetime.utcnow()}})


async def create_case(payload):
    logging.info("NEW CASE MESSAGE RECEIVED")
    text = payload["body"]
    chat_id = payload["from"]
    message_id = payload['id']
    participant = payload.get('participant')

    await send_safe_message(chat_id, message_id, participant, lab_data["DEFAULT_REPLY_MESSAGE"], True)
    await send_safe_message(lab_data["SUPPORT_GROUP_ID"], message_id, participant,
                            solicitude_handler(payload["_data"]["notifyName"], text), False)
    case = {
        "name": payload["_data"]["notifyName"],
        "number": payload["from"],
        "message": payload["body"],
        "creation_date": datetime.datetime.utcnow(),
        "last_update": datetime.datetime.utcnow(),
        "active": True
    }
    try:
        cases.insert_one(case)
        # close the case in 10 seconds
        logging.info("CASE CREATED")
        await asyncio.create_task(close_case(case["_id"]))

    except errors.DuplicateKeyError:
        print("Case already exists")


async def close_case(case_id):
    while cases.find_one({"_id": case_id})["last_update"] + datetime.timedelta(seconds=10) > datetime.datetime.utcnow():
        await asyncio.sleep(9)

    cases.update_one({"_id": case_id}, {"$set": {"active": False}})
    print("Case closed")
    logging.info("CASE CLOSED")


def get_cases_df():
    # get all cases
    all_cases = cases.find()
    # convert to dataframe
    df = pd.DataFrame(all_cases)
    # convert date columns to datetime
    df["creation_date"] = pd.to_datetime(df["creation_date"])
    df["last_update"] = pd.to_datetime(df["last_update"])
    # convert active column to boolean
    df["active"] = df["active"].astype(bool)
    # convert _id column to string
    df["_id"] = df["_id"].astype(str)
    # convert number column to string
    df["number"] = df["number"].astype(str)
    # order by last update
    df = df.sort_values(by=["last_update"], ascending=False)
    # fix index and start from 1
    df = df.reset_index(drop=True)
    df.index += 1
    df.number = df.number.apply(lambda x: x[2:-5])

    # save to csv
    # df.to_csv("cases.csv", index=False)
    print(df)
    return df


if __name__ == "__main__":
    print(get_cases_df())
