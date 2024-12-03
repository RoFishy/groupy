import base64
import pymongo
from cryptography.fernet import Fernet
from dotenv import dotenv_values

config = dotenv_values(".env")
key = config["ENCRYPTION_KEY"]
connection_str = config["CONNECTION_STR"]

client = pymongo.MongoClient(str(connection_str))
mydb = client["RankBot_Data"]
information = mydb["api_information"]

def guild_already_setup(server_id : int) -> bool:
    search_critera = {"server_id": server_id}
    results = information.find(search_critera)
    if results.count() > 0:
        return True
    else:
        return False

def get_f_key(key : str) -> bytes:
    return base64.urlsafe_b64decode(key.encode("utf-8"))

def decrypt(key : str) -> str:
    stored_key_bytes = get_f_key(str(key))
    fernet = Fernet(stored_key_bytes)
    decrypted_key = fernet.decrypt(key).decode()
    return decrypted_key

def get_api_key(server_id : int) -> str:
    search_critera = {"server_id": server_id}
    results = information.find(search_critera)
    global decrypted_key
    for result in results:
        decrypted_key = decrypt(result["api_key"])
    return decrypted_key

def create_info(server_id : int, api_key : str) -> None:
    if guild_already_setup(server_id):
        update_info(server_id, api_key)
    else:
        stored_key_bytes = get_f_key(str(key))
        fernet = Fernet(stored_key_bytes)
        encrypted_key = fernet.encrypt(api_key.encode())
        data = {
            "server_id" : server_id,
            "api_key" : encrypted_key
        }
        information.insert_one(data)

def update_info(server_id : int, api_key : str) -> None:
    stored_key_bytes = get_f_key(str(key))
    fernet = Fernet(stored_key_bytes)
    encrypted_key = fernet.encrypt(api_key.encode())
    search_critera = {"server_id": server_id}
    new_values = {
        "server_id": server_id,
        "api_key": encrypted_key
    }
    information.update_one(search_critera, new_values)