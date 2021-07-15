from __future__ import annotations

###################### IMPORTS ######################
from GameLogic.Player import Player
from GameLogic.Items import Item
from Utils.Constants import BEE_DURATION, pretty_time_delta
from Utils.Database import BeeDatabase as DATABASE
import discord,random, asyncio, time
#####################################################

class BeeStorage:
    BEESTORAGE_REFERENCES : dict[Player, BeeStorageReference] = {}
    __slots__ = ["storage", "id"]
    def __init__(self, id : str, storage : dict[str, Bee] = None) -> None:
        self.storage : dict[str, Bee] = {} if storage == None else storage
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
    def FromDict(data : dict) -> BeeStorage:
        storage = {}
        for slot in data['storage']:
            storage[str(slot)] = Bee.FromDict(data['storage'][slot], id = data['id'])
        result = BeeStorage(id=data['id'], storage=storage)
        return result

    @staticmethod
    def GrowBeeForUser(user : Player, bee : Bee) -> None:
        bee_storage = BeeStorage.GetBeeStorage(user.id)
        bee_storage.storage[str(len(bee_storage.storage))] = bee

    async def CheckForCompletion(self, ctx):
        current_time = time.time()
        for slot in self.storage.copy():
            bee = self.storage[slot]
            if bee.finishing_time < current_time:
                await self.storage.pop(slot).__call__(ctx) #Removes the grown bee and calls its corresponding event
                #print(bee, " is done!")

    @staticmethod
    def Save() -> None:
        for id in BeeStorage.BEESTORAGE_REFERENCES:
            BeeStorageRef = BeeStorage.BEESTORAGE_REFERENCES[id]
            if BeeStorageRef.ReferencedItem != None: #BeeStorageRef.is_mutated:
                DATABASE.Save(key=BeeStorageRef.ReferencedItem.id, value=BeeStorageRef.ReferencedItem.ToDict())
                BeeStorageRef.ReferencedItem = None

    @staticmethod
    def GetBeeStorage(id : str) -> BeeStorage:
        id = str(id)
        if id in BeeStorage.BEESTORAGE_REFERENCES: return BeeStorage.BEESTORAGE_REFERENCES[id]
        return BeeStorageReference(id = id)

class Bee:
    def __init__(self, time: int, on_finish, user : Player, name : str = "Bee", type = "normal") -> None:
        self.finishing_time: int = time
        self.user: Player = user
        self.__call__: function = on_finish
        self.name: str = name
        self.type: str = type

    def __repr__(self) -> str:
        return f"{self.name} - time left: `{pretty_time_delta( int(self.finishing_time - time.time()) )}`"

    def ToDict(self) -> dict:
        result = {}
        result['time_left'] = int(self.finishing_time - time.time())
        result['name'] = self.name
        result['type'] = self.type
        return result

    @staticmethod    
    def FromDict(data : dict, id : str) -> Bee:
        plant_type = data['type']
        if plant_type == "normal":
            return NormalBee(user= Player.GetPlayer(id = id), time_left=data['time_left'], dont_grow=True)
        raise TypeError(f"attempted to load unknown plant time!! (type={plant_type})")



def NormalBee(user : Player, time_left : int = BEE_DURATION.NORMAL_BEE, dont_grow = False) -> Bee:
    async def Reward(ctx):
        amount_to_give = random.randint(1,3)

        items_to_give = [Item.GetItem("honey") for _ in range(random.randint(1,3))] + [Item.GetRandomItem() for _ in range(amount_to_give)]
        hidden_content = ["**->** <a:loading:794672829202300939>" for _ in range(amount_to_give)]
        embed = discord.Embed(
        title="🐝 Harvesting Bee 🐝",
        description= "\n\n".join(hidden_content),
        color=discord.Color.dark_teal(),
        )
        msg = await ctx.reply(embed=embed)
        for i in range(amount_to_give):
            await asyncio.sleep(0.9)
            hidden_content[i] = f"**->** {items_to_give[i]}"
            embed.description = "\n\n".join(hidden_content)
            Player.GetPlayer(user.id).inventory.AddItem(items_to_give[i])
            await msg.edit(embed=embed)
     
    bee = Bee(time = int( time_left + time.time() ), on_finish = Reward, user = user, name="`🐝 Bee`", type="normal")
    if not dont_grow:    
        BeeStorage.GrowBeeForUser(user = user,
                                bee  = bee,
                                )
    return bee



class BeeStorageReference(object):
    def __init__(self, id : str) -> None:
        self.ReferencedItem : BeeStorage = None
        self.id : str = id
        self.is_mutated : bool = False
        BeeStorage.BEESTORAGE_REFERENCES[id] = self

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
    def __FetchReferencedItem__(id : str) -> BeeStorage:
        data =  DATABASE.Get(key = str(id))
        if data != None:
            return BeeStorage.FromDict( data )
        return BeeStorage(id=id)