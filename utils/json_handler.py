import json
import asyncio

async def wrapper(delay, coro):
    await asyncio.sleep(delay)
    return await coro

async def decrement_json_val(filename, user_id):
    if filename == "ranking":
        user_data = open_file("temp/json/rank_changes.json", "r", "UTF-8")[str(user_id)]
        if user_data["Changes"] == 0:
            remove_user_to_json("ranking", user_id)
        else:
            data = {"amount" : -1}
            add_data_to_user("ranking", user_id, data)

def open_file(path, mode, encoding, data=None, indent=None):
    if mode == "r":
        with open(path, mode, encoding=encoding) as f:
            return json.load(f)
    elif mode == "w":
        with open(path, mode, encoding=encoding) as f:
            json.dump(data, f, indent=indent)

def remove_user_to_json(filename, user_id):
    if filename=="ranking":
        data = open_file("temp/json/rank_changes.json", "r", "UTF-8")
        del data[str(user_id)]
        open_file("temp/json/rank_changes.json", "w", "UTF-8", data, 4)

def add_user_to_json(filename, user_id):
    if filename=="ranking":
        data = open_file("temp/json/rank_changes.json", "r", "UTF-8")
        data[str(user_id)] = {
            "Changes" : 0,
        }
        open_file("temp/json/rank_changes.json", "w", "UTF-8", data, 4)
        wrapper(60, decrement_json_val("ranking", user_id))

def add_data_to_user(filename, user_id, data):
    if filename=="ranking":
        file_data = open_file("temp/json/rank_changes.json", "r", "UTF-8")
        global user_data
        user_data = file_data[str(user_id)]
        user_data = {
            "Changes" : user_data["Changes"] + data["amount"],
        }

def check_user_in_file(filename, user_id):
    if filename == "ranking":
        data = open_file("temp/json/rank_changes.json", "r", "UTF-8")
        if str(user_id) in data:
            return False
        else:
            return True