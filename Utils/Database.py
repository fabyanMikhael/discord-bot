from __future__ import annotations, print_function
import os, pymongo
from pymongo.collection import Collection
from dotenv import load_dotenv
load_dotenv()

client =pymongo.MongoClient(os.environ["MONGO_KEY"]) 
MongoDatabase = client.get_database(name = "Arrodes")

class AbstractDatabase:
    def __init__(self, collection : Collection) -> None:
        self.collection = collection
    
    def Get(self, key : str) -> dict:
        return self.collection.find_one({"id" : str(key)})

    def Update(self, key : str, value : dict, upsert=False) -> None:
        self.collection.update_one({'id':str(key)}, {"$set": value}, upsert=upsert)

    def Insert(self, key : str, value : dict) -> None:
        value['id'] = str(key)
        self.collection.insert_one(value)

    def Save(self, key : str,  value : dict) -> None:
        if self.Get(key=key) != None:
            self.collection.update_one({'id':str(key)}, {"$set": value}, upsert=False)
        else :
            print("inserting: ", value)
            self.collection.insert_one(value)

    def Delete(self, query : dict) -> None:
        self.collection.delete_one(query)

    def GetAll(self) -> list[dict]:
        return self.collection.find({})

class PlayerCollection(AbstractDatabase):
    def __init__(self) -> None:
        super().__init__(MongoDatabase["Players"])
class ShopCollection(AbstractDatabase):
    def __init__(self) -> None:
        super().__init__(MongoDatabase["Shop"])
class PlantCollection(AbstractDatabase):
    def __init__(self) -> None:
        super().__init__(MongoDatabase["Plants"])
class BeeCollection(AbstractDatabase):
    def __init__(self) -> None:
        super().__init__(MongoDatabase["Bees"])


PlayerDatabase = PlayerCollection()
ShopDatabase = ShopCollection()
PlantDatabase = PlantCollection()
BeeDatabase = BeeCollection()