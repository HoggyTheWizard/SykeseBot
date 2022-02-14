from config import database_user, database_password, main_db_name
import pymongo

cluster = pymongo.MongoClient(f"mongodb+srv://{database_user}:{database_password}@cluster0.2uexc.mongodb.net/"
                              f"{main_db_name}?retryWrites=true&w=majority")

main_db = cluster["main_data"]
