import pymongo
from dotenv import dotenv_values

config = dotenv_values(".env")
connection_str = config["CONNECTION_STR"]

client = pymongo.MongoClient(str(connection_str))
mydb = client["RankBot_Data"]
server_config = mydb["server_config"]

def create_configs(server_id : int, data : dict):
    logging_channel = data["logging_channel"]
    required_roles = data["required_roles"]
    
    data = {
        "serverid": server_id,
        "configs": {
            "logging_channel": logging_channel,
            "required_roles": required_roles
        }
    }
    server_config.insert_one(data)

def update_configs(server_id : int, newData : dict):
    search_critera = {"server_id": server_id}
    logging_channel = newData["logging_channel"]
    required_roles = newData["required_roles"]
    new_values = {
        "serverid": server_id,
        "configs": {
            "logging_channel": logging_channel,
            "required_roles": required_roles
        }
    }
    server_config.update_one(search_critera, new_values)

def fetch_configs(server_id : int) -> dict:
    search_critera = {"server_id": server_id}
    results = server_config.find(search_critera)
    global configs
    for result in results:
        configs = result["configs"]
    return configs