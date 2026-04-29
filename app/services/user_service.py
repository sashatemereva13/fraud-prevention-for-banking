from datetime import datetime, timezone

from app.db.mongo import users_collection

# CREATE USER
def create_user(data):
    user = {
        "user_id": data["user_id"],
        "name": data["name"],
        "email": data["email"],
        "created_at": datetime.now(timezone.utc)
    }

    users_collection.insert_one(user)

    return {
        "message": "User created successfully",
        "user_id": data["user_id"]
    }


# GET ALL USERS
def get_all_users():
    return list(users_collection.find({}, {"_id": 0}))


# GET USER BY ID
def get_user_by_id(user_id):
    return users_collection.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )