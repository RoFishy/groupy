import pymongo
from dotenv import dotenv_values

config = dotenv_values(".env")
connection_str = config["CONNECTION_STR"]

client = pymongo.MongoClient(str(connection_str))
mydb = client["RankBot_Data"]
group_config = mydb["group_config"]

def guild_already_setup(server_id : int) -> bool:
    search_critera = {"serverid": server_id}
    results = group_config.count_documents(search_critera)
    if results > 0:
        return True
    else:
        return False

def create_configs(server_id : int, groupId : int):
    new_data = {
        "serverid": server_id,
        "groupid": groupId
    }
    group_config.insert_one(new_data)

def update_configs(server_id : int, groupId : int):
    search_critera = {"serverid": server_id}
    new_values = {
        "$set" : {
            "serverid": server_id,
            "groupid": groupId
        }
    }
    group_config.update_one(search_critera, new_values)


def fetch_id(server_id : int) -> int:
    search_critera = {"serverid": server_id}
    results = group_config.find(search_critera)
    global configs
    for result in results:
        configs = result["groupid"]
    return configs