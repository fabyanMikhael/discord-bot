from __future__ import annotations
###################### IMPORTS ######################
from Utils.Database import PlantDatabase as DATABASE
from GameLogic.Items import Item
from GameLogic.Player import Player
from Utils.Constants import RewardUI, SEED_DURATION, pretty_time_delta
import random, time
#####################################################

class PlantStorage:
    PLANTSTORAGE_REFERENCES : dict[str, PlantStorageReference] = {}
    __slots__ = ["storage", "id"]
    def __init__(self, id : str, storage : dict[str, Plant] = None) -> None:
        self.storage: dict[str, Plant] = {} if storage == None else storage
        self.id = str(id)

    def ToDict(self) -> dict:
        storage = {}
        for slot in self.storage:
            storage[slot] = self.storage[slot].ToDict()
        result = {}
        result['storage'] = storage
        result['id'] = self.id
        return result

    @staticmethod
    def FromDict(data : dict) -> PlantStorage:
        storage = {}
        for slot in data['storage']:
            storage[slot] = Plant.FromDict(data['storage'][slot], data['id'])
        result = PlantStorage(id = data['id'], storage=storage)
        return result

    @staticmethod
    def PlantForUser(user : Player, plant : Plant) -> None:
        plant_storage = PlantStorage.GetPlantStorage(user.id)
        plant_storage.storage[str(len(plant_storage.storage))] = plant

    async def CheckForCompletion(self, ctx):
        current_time = time.time()
        for slot in self.storage.copy():
            plant = self.storage[slot]
            if plant.finishing_time < current_time:
                await self.storage.pop(slot).__call__(ctx) #Removes the grown plant and calls its corresponding event
                #print(plant, " is done!")

    @staticmethod
    def Save() -> None:
        for id in PlantStorage.PLANTSTORAGE_REFERENCES:
            PlantStorageRef = PlantStorage.PLANTSTORAGE_REFERENCES[id]
            if PlantStorageRef.ReferencedItem != None: #PlantStorageRef.is_mutated:
                DATABASE.Save(key=PlantStorageRef.ReferencedItem.id, value=PlantStorageRef.ReferencedItem.ToDict())
                PlantStorageRef.ReferencedItem = None

    @staticmethod
    def GetPlantStorage(id : str) -> PlantStorage:
        id = str(id)
        if id in PlantStorage.PLANTSTORAGE_REFERENCES: return PlantStorage.PLANTSTORAGE_REFERENCES[id]
        return PlantStorageReference(id = id)

    @staticmethod
    def DeletePlantStorage(id : str) -> None:
        id = str(id)
        PlantStorage.GetPlantStorage(id)
        PlantStorage.PLANTSTORAGE_REFERENCES.pop(id).ReferencedItem = None
        DATABASE.Delete(id)

class Plant:
    def __init__(self, time: int, on_finish, user : Player, name : str = "Plant", type="normal") -> None:
        self.finishing_time: int = time
        self.user: Player = user
        self.__call__: function = on_finish
        self.name: str = name
        self.type: str = type

    def __repr__(self) -> str:
        return f"{self.name} - time left: `{pretty_time_delta( int(self.finishing_time - time.time()) )}`"

    def ToDict(self) -> dict:
        result = {}
        result['finishing_time'] = int(self.finishing_time)
        result['name'] = self.name
        result['type'] = self.type
        return result

    @staticmethod    
    def FromDict(data : dict, id : str) -> Plant:
        plant_type = data['type']
        if plant_type == "x":
            return XSeedPlant(user=Player.GetPlayer(id = id), time_left=data['finishing_time'] - time.time(), dont_plant=True)
        if plant_type == "wooden":
            return WoodenPlant(user=Player.GetPlayer(id = id), time_left=data['finishing_time'] - time.time(), dont_plant=True)
        if plant_type == "arctic":
            return ArcticParasitePlant(user=Player.GetPlayer(id = id), time_left=data['finishing_time'] - time.time(), dont_plant=True)

        raise TypeError(f"attempted to load unknown plant time!! (type={plant_type})")

class PlantStorageReference(object):
    def __init__(self, id : str) -> None:
        self.ReferencedItem : PlantStorage = None
        self.id : str = id
        self.is_mutated : bool = False
        PlantStorage.PLANTSTORAGE_REFERENCES[id] = self

    def __getattribute__(self, name):
        if name in ["ReferencedItem", "id", "is_mutated", "__attributeAccessed__", "__FetchReferencedItem__"]: return object.__getattribute__(self, name)
        self.__attributeAccessed__()
        return object.__getattribute__( self.ReferencedItem ,  name)

    def __setattr__(self, name: str, value) -> None:
        if name in ["ReferencedItem", "id", "is_mutated"]: 
            super().__setattr__(name, value)
        else :
            self.__attributeAccessed__()
            self.ReferencedItem.__setattr__(name, value)
            self.is_mutated = True

    def __attributeAccessed__(self):
        if self.ReferencedItem == None:
            self.ReferencedItem = self.__FetchReferencedItem__(self.id)
            self.is_mutated = False

    @staticmethod
    def __FetchReferencedItem__(id : str) -> PlantStorage:
        data =  DATABASE.Get(key = str(id))
        if data != None:
            return PlantStorage.FromDict( data )
        return PlantStorage(id=id)






############################## PLANT REWARDS ##############################
def XSeedPlant(user : Player, time_left : int = None, dont_plant = False) -> Plant:
    if time_left == None: time_left = SEED_DURATION.x_seed
    async def Reward(ctx):
        items_to_give = [Item.GetRandomItem() for _ in range(random.randint(2,8))]
        await RewardUI(ctx=ctx,
                user=user,
                items_to_give=items_to_give,
                title="`💠` Harvesting Plants `💠`")

    plant = Plant(time= int(time_left + time.time()), on_finish = Reward, user = user, name="`🌱 X Plant`", type="x")
    if not dont_plant:
        PlantStorage.PlantForUser(user = user,
                                plant = plant,
                                )
    return plant

def WoodenPlant(user : Player, time_left : int = None, dont_plant = False) -> Plant:
    if time_left == None: time_left = SEED_DURATION.wooden_seed
    async def Reward(ctx):
        items_to_give = Item.GetRandomItemsFrom(category="wooden", count=random.randint(1,2)) + Item.GetRandomItems(count=random.randint(1,3))

        await RewardUI(ctx=ctx,
                user=user,
                items_to_give=items_to_give,
                title="`💠` Harvesting Plants `💠`")

    plant = Plant(time= int(time_left + time.time()), on_finish = Reward, user = user, name="<:WoodenSeed:865434094917124157> Wooden Plant", type="wooden")
    if not dont_plant:
        PlantStorage.PlantForUser(user = user,
                                plant = plant,
                                )
    return plant

def ArcticParasitePlant(user : Player, time_left : int = None, dont_plant = False) -> Plant:
    if time_left == None: time_left = SEED_DURATION.arctic_parasite
    async def Reward(ctx):
        items_to_give = Item.GetRandomItemsFrom(category="arctic", count=random.randint(0,2)) + Item.GetRandomItems(count=random.randint(2,5))

        await RewardUI(ctx=ctx,
                user=user,
                items_to_give=items_to_give,
                title="`💠` Harvesting Plants `💠`")

    plant = Plant(time= int(time_left + time.time()), on_finish = Reward, user = user, name="<:arcticParasitePlant:865436985237176330> Arctic Parasite", type="arctic")
    if not dont_plant:
        PlantStorage.PlantForUser(user = user,
                                plant = plant,
                                )
    return plant