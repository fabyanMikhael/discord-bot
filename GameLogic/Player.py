from __future__ import annotations
from Utils.Database import PlayerDatabase as DATABASE
from GameLogic.Items import Item, Inventory
from Utils.Constants import STARTING_AMOUNT_OF_LOOTBOXES

class Player:
    PLAYER_REFERENCES : dict[str, PlayerReference] = {}
    BOT = None

    def __init__(self, id : str, balance: int = 20, inventory: Inventory = None) -> None:
        self.id : str = str(id)
        self.balance : int = balance
        ####### not what i would like , but i need this to retrieve the user's name #######
        from discord.utils import get
        self.name = get(Player.BOT.get_all_members(), id=int(id)).name
        ###################################################################################
        self.inventory : Inventory = Inventory() if inventory == None else inventory

    def __hash__(self) -> int:
        return int(self.id)

    def __eq__(self, other : Player) -> bool:
        if isinstance(other, Player):
            return self.id == other.id
        elif isinstance(other, PlayerReference):
            return self.id == other.player.id
        return self.id == other

    def __repr__(self) -> str:
        return self.name
    ########################################################################################

    def Gift(self, recipient : Player, items: dict[Item, int]) -> None:
        self.inventory.RemoveItems(items=items)
        recipient.inventory.AddItems(items=items)

    ########################################################################################

    @staticmethod
    def GetPlayer(id : str) -> Player:
        id = str(id)
        if id in Player.PLAYER_REFERENCES: return Player.PLAYER_REFERENCES[id]
        return PlayerReference(id = id)

    def ToDict(self) -> dict:
        result = {}
        result["id"] = self.id
        result["balance"] = self.balance
        result["inventory"] = self.inventory.ToDict()
        return result

    @staticmethod
    def FromDict(data : dict) -> Player:
        result = Player(id = data.get('id'),
                        balance = data.get('balance', 20),
                        inventory= Inventory.FromDict( data.get('inventory', {}) )
                        )
        return result

    @staticmethod
    def Save() -> None:
        for id in Player.PLAYER_REFERENCES:
            PlayerRef = Player.PLAYER_REFERENCES[id]
            if PlayerRef.player != None: #PlayerRef.is_mutated:
                DATABASE.Save(key=PlayerRef.player.id, value=PlayerRef.player.ToDict())
                PlayerRef.player = None

    @staticmethod
    def Clear() -> None:
        for id in Player.PLAYER_REFERENCES:
            PlayerRef = Player.PLAYER_REFERENCES[id]
            PlayerRef.player = None

class PlayerReference(object):
    def __init__(self, id : str) -> None:
        self.player : Player = None
        self.id : str = id
        self.is_mutated : bool = False
        Player.PLAYER_REFERENCES[id] = self

    def __repr__(self) -> str:
        if self.player != None:
            return self.player.__repr__()
        return f"<EMPTY REFERENCE TO: {self.id}>"

    def __getattribute__(self, name):
        if name in ["player", "id", "is_mutated", "__attributeAccessed__", "__FetchPlayer__"]: return object.__getattribute__(self, name)
        self.__attributeAccessed__()
        return object.__getattribute__( self.player ,  name)

    def __setattr__(self, name: str, value) -> None:
        if name in ["player", "id", "is_mutated"]: 
            super().__setattr__(name, value)
        else :
            self.__attributeAccessed__()
            self.player.__setattr__(name, value)
            self.is_mutated = True

    def __attributeAccessed__(self):
        if self.player == None:
            self.player = self.__FetchPlayer__(self.id)
            self.is_mutated = False

    @staticmethod
    def __FetchPlayer__(id : str) -> Player:
        data =  DATABASE.Get(key = str(id))
        if data != None:
            return Player.FromDict( data )
        new_player = Player(id=id)
        new_player.inventory.AddItem(item=Item.GetItem("lootbox"), amount=STARTING_AMOUNT_OF_LOOTBOXES)
        return new_player