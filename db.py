import pymongo
import os

cluster = pymongo.MongoClient(f"mongodb+srv://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}"
                              f"@cluster0.2uexc.mongodb.net/{os.environ['MAIN_DB_NAME']}?retryWrites=true&w=majority")

main_db = cluster["main_data"]
