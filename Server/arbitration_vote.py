from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient

def run_arbitration_vote_task(mongodb_address, complaint_id, private_key_sharding, vote):
    client = MongoClient(mongodb_address)
    db = client["complaint_platform"]
    collection = db["ballot_box"]

    query = {
        "_id": ObjectId(complaint_id)
    }
    results = collection.find_one(query)

    if results:
        if vote.lower() == "y" or vote.lower() == "n":
            if datetime.now() <= results["deadline"]:
                query = {
                    "_id": ObjectId(complaint_id)
                }
                
                if vote.lower() == "y":
                    update = {
                                "$push": {
                                    "agree": 1,
                                    "agreed_private_key_sharding": private_key_sharding
                                }
                    }
                else:
                    update = {"$push": {"disagree": 1}}
                
                result = collection.update_one(query, update)

                if result.modified_count > 0:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False