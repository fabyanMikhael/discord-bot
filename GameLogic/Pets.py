from __future__ import annotations

###################### IMPORTS ######################
from GameLogic.Player import Player
from GameLogic.Items import Item
from Utils.Constants import PET_GROWTH_DURATION, RewardUI, pretty_time_delta
from Utils.Database import BeeDatabase as DATABASE
import random, time
#####################################################

class PetStorage:
    PETSTORAGE_REFERENCES : dict[Player, PetStorageReference] = {}
    __slots__ = ["storage", "id"]
    def __init__(self, id : str, storage : dict[str, Pet] = None) -> None:
        self.storage : dict[str, Pet] = {} if storage == None else storage
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
    def FromDict(data : dict) -> PetStorage:
        storage = {}
        for slot in data['storage']:
            storage[str(slot)] = Pet.FromDict(data['storage'][slot], id = data['id'])
        result = PetStorage(id=data['id'], storage=storage)
        return result

    @staticmethod
    def GrowPetForUser(user : Player, pet : Pet) -> None:
        pet_storage = PetStorage.GetPetStorage(user.id)
        pet_storage.storage[str(len(pet_storage.storage))] = pet

    async def CheckForCompletion(self, ctx):
        current_time = time.time()
        for slot in self.storage:
            pet = self.storage[slot]
            if pet.grown == False and pet.finishing_time < current_time:
                await self.storage.get(slot).__call__(ctx)

    @staticmethod
    def Save() -> None:
        for id in PetStorage.PETSTORAGE_REFERENCES:
            PetStorageRef = PetStorage.PETSTORAGE_REFERENCES[id]
            if PetStorageRef.ReferencedItem != None: #PetStorageRef.is_mutated:
                DATABASE.Save(key=PetStorageRef.ReferencedItem.id, value=PetStorageRef.ReferencedItem.ToDict())
                PetStorageRef.ReferencedItem = None

    @staticmethod
    def GetPetStorage(id : str) -> PetStorage:
        id = str(id)
        if id in PetStorage.PETSTORAGE_REFERENCES: return PetStorage.PETSTORAGE_REFERENCES[id]
        return PetStorageReference(id = id)

    @staticmethod
    def DeletePetStorage(id : str) -> None:
        id = str(id)
        PetStorage.GetPetStorage(id)
        PetStorage.PETSTORAGE_REFERENCES.pop(id).ReferencedItem = None
        DATABASE.Delete(id)

class Pet:
    def __init__(self, time: int, on_finish, user : Player, name : str = "Unnamed", type = "egg") -> None:
        self.user: Player = user

        self.name: str = name
        self.level = 1
        self.experience = 0
        self.experience_cap = 100
        self.species = type
        self.type: str = type

        ########### Used for growing an egg ###########
        self.finishing_time: int = time
        self.grown = False
        self.__call__: function = on_finish
        ###############################################

    def __repr__(self) -> str:
        return f"{self.name} - time left: `{pretty_time_delta( int(self.finishing_time - time.time()) )}`"

    def ToDict(self) -> dict:
        result = {}
        result['name'] = self.name
        result['level'] = self.level
        result['experience'] = self.experience
        result['experience_cap'] = self.experience_cap
        result['type'] = self.type

        result['time_left'] = int(self.finishing_time - time.time())
        return result

    @staticmethod    
    def FromDict(data : dict, id : str) -> Pet:
        pet = GrowEgg(user= Player.GetPlayer(id = id), time_left=data['time_left'], dont_grow=True)
        pet.name           = data['name']
        pet.level          = data['level']
        pet.experience     = data['experience']
        pet.experience_cap = data['experience_cap']
        pet.type           = data['type']
        return pet


def GrowEgg(user : Player, time_left : int = None, dont_grow = False) -> Pet:
    if time_left == None: time_left = PET_GROWTH_DURATION
    async def Reward(ctx):
        pass # TODO: implement the mechanism for changing pet to a grown one
     
    pet = Pet(time = int( time_left + time.time() ), on_finish = Reward, user = user)
    if not dont_grow:    
        PetStorage.GrowPetForUser(user = user,
                                  pet  = pet,
                                )
    return pet



class PetStorageReference(object):
    def __init__(self, id : str) -> None:
        self.ReferencedItem : PetStorage = None
        self.id : str = id
        self.is_mutated : bool = False
        PetStorage.PETSTORAGE_REFERENCES[id] = self

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
    def __FetchReferencedItem__(id : str) -> PetStorage:
        data =  DATABASE.Get(key = str(id))
        if data != None:
            return PetStorage.FromDict( data )
        return PetStorage(id=id)