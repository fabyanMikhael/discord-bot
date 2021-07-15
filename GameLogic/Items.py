from __future__ import annotations
from typing import Union
from Utils.Constants import PAGE_ITEM_LIMIT
from Utils.ErrorHandling import InventoryError
import random

class Item:
    __slots__ = ("id", "icon", "name", "rarity")
    ITEMS : dict [int, Item] = {}
    NAME_TO_ITEM : dict[str, Item] = {}
    RARITY : dict[str, list[Item]] = {"common" : []}
    ID_COUNTER = 0
    def __init__(self, name : str, icon : str, id : int = None, block=True, rarity : str = "common") -> None:
        if id == None:
            id = Item.ID_COUNTER
            Item.ID_COUNTER += 1
        self.id = id
        self.icon = f"`{icon}`" if block else icon
        self.name = name
        self.rarity = rarity
        Item.ITEMS[id] = self
        Item.NAME_TO_ITEM[name.lower()] = self
        Item.RARITY[rarity].append(self)

    def __repr__(self) -> str:
        return f"{self.icon} - **{self.name}**"

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other : Item) -> bool:
        return self.id == other.id

    @staticmethod
    def GetItem(id : Union[int, str]) -> Item:
        Item.LoadItems()
        try: id = int(id)
        except: pass
        if isinstance(id, str):
            id = id.lower()
            if id in Item.NAME_TO_ITEM: return Item.NAME_TO_ITEM[id]
            raise InventoryError(f"cannot find item with name: {id}")
        if id in Item.ITEMS: return Item.ITEMS[id]
        raise InventoryError(f"cannot find item with id: {id}")

    @staticmethod
    def GetRandomItem() -> Item:
        Item.LoadItems()
        id = random.choice( list(Item.ITEMS) )
        return Item.GetItem(id=id)

    ITEMS_LOADED = False
    @staticmethod
    def LoadItems(force : bool = False):
        if Item.ITEMS_LOADED and not force: return

        LoadAllItems() #this is where all items get registered!

        Item.ITEMS_LOADED = True

class Inventory:
    __slots__ = ("items")
    def __init__(self) -> None:
        self.items : dict[Item, int] = {}
        
    def ToDict(self) -> dict:
        result = {}
        for item in self.items:
            result[str(item.id)] = self.items[item]
        return result

    @staticmethod
    def FromDict(data : dict) -> Inventory:
        result = Inventory()
        for item_id in data:
            result.AddItem(Item.GetItem(id = int(item_id)), data[item_id])
        return result

    def __repr__(self) -> str:
        result = "\u200b"
        for item in self.items:
            result += f"{item} `x{self.items[item]}`\n\n"
        return result

    def ToPages(self) -> list[str]:
        pages = []
        result = "\u200b"
        for (idx, item) in enumerate(self.items):
            if idx % PAGE_ITEM_LIMIT == 0 and idx != 0: 
                pages.append(result)
                result = "\u200b"
            result += f"{item} `x{self.items[item]}`\n\n"
        pages.append(result)
        return pages

    def AddItem(self, item : Item , amount : int = 1) -> Inventory:
        self.items[item] = max(0, self.items.get(item,0) + amount )
        #print(f"added item {item} x{self.items[item]}")
        if self.items[item] == 0:
            self.items.pop(item)
        return self

    def AddItems(self, items : dict[Item, int]) -> Inventory:
        for item in items:
            self.AddItem(item, items[item])
        return self

    def RemoveItem(self, item : Item, amount : int = 1) -> Inventory:
        self.items[item] = max(0, self.items.get(item,0) - amount )
        if self.items[item] == 0:
            self.items.pop(item)
        return self

    def RemoveItems(self, items : dict[Item, int]) -> Inventory:
        for item in items:
            self.RemoveItem(item, items[item])
        return self

    def GetItemCount(self, item : Item) -> int:
        return self.items.get(item, 0)

    def HasItem(self, item : Item) -> bool:
        return self.GetItemCount(item) > 0

    def HasAmount(self, item : Item, amount : int) -> bool:
        return self.GetItemCount(item) >= amount

    @staticmethod
    def CreatePageFrom(items : dict[Item, int]) -> str:
        result = "\u200b"
        for item in items:
            result += f"**->**\u200b {item} `x{items[item]}`\n"
        result += "\n\n"
        return result

#this is where all items get registered!
# Add/edit these items to change what items exist in the game
def LoadAllItems():
    Item(name="Ticket to Hell", icon="🎟️")
    Item(name="Sagittarius", icon="♐")
    Item(name="Infinity", icon="♾️")
    Item(name="Departure", icon="🛫")
    Item(name="Fire", icon="🔥")
    Item(name="Extinguisher", icon="🧯")
    Item(name="Ant", icon="🐜")
    Item(name="Trash Can", icon="🗑️")
    Item(name="Purse", icon="👛")
    Item(name="Equivalent Exchange", icon="💱")
    Item(name="Surrender", icon="🏳️")
    Item(name="Syringe", icon="💉")
    Item(name="The World", icon="🌎")
    Item(name="The Universe", icon="🌌")
    Item(name="water droplet", icon="💧")
    Item(name="X Seed", icon="🌱")
    Item(name="Comet", icon="☄️")
    Item(name="Shooting Star", icon="🌠")
    Item(name="Clown", icon="🤡")
    Item(name="Sparkles", icon="✨")
    Item(name="Cake", icon="🍰")
    Item(name="Bobert", icon="🚮")
    Item(name="Ray", icon="🐈")
    Item(name="Ham", icon="🍖")
    Item(name="Confetti", icon="🎊")
    Item(name="Candle", icon="🕯️")

    Item(name="Grapes", icon="🍇")
    Item(name="Melon", icon="🍈")
    Item(name="Watermelon", icon="🍉")
    Item(name="Tangerine", icon="🍊")
    Item(name="Lemon", icon="🍋")
    Item(name="Banana", icon="🍌")
    Item(name="Pineapple", icon="🍍")
    Item(name="Mango", icon="🥭")
    Item(name="Apple", icon="🍎")
    Item(name="Green Apple", icon="🍏")
    Item(name="Pear", icon="🍐")
    Item(name="Peach", icon="🍑")
    Item(name="Cherries", icon="🍒")

    Item(name="Satellite", icon="🛰️")
    Item(name="Rocket", icon="🚀")
    Item(name="Parachute", icon="🪂")
    Item(name="Seat", icon="💺")
    Item(name="Helicopter", icon="🚁")

    Item(name="Fireworks", icon="🎆")
    Item(name="Sparkler", icon="🎇")

    Item(name="Bee", icon="🐝")
    Item(name="Honey", icon="🍯")
    Item(name="Teddy bear", icon="🧸")
    Item(name="Lootbox", icon="📦")
    Item(name="Zonu", icon="<:zonu:864377761337180170>", block=False)
    
    Item(name="Mask", icon="👺")
    Item(name="Poop", icon="💩")
    Item(name="Alien", icon="👽")
    Item(name="Pumpkin", icon="🎃")
    Item(name="Lipstick", icon="💄")
    Item(name="Dress Shirt", icon="👚")
    Item(name="T-Shirt", icon="👕")
    Item(name="Bikini", icon="👙")
    Item(name="Heels", icon="👠")
    Item(name="Sneakers", icon="👟")
    Item(name="Mittens", icon="🧤")
    Item(name="Scarf", icon="🧣")
    Item(name="Socks", icon="🧦")
    Item(name="Bone", icon="🦴")
    Item(name="Cap", icon="🧢")
    Item(name="Top Hat", icon="🎩")
    Item(name="Crown", icon="👑")
    Item(name="Ring", icon="💍")
    Item(name="Glasses", icon="👓")
    Item(name="Backpack", icon="🎒")
    Item(name="Baby Chick", icon="🐣")
    Item(name="Duck", icon="🦆")
    Item(name="Spider", icon="🕷️")
    Item(name="Scorpion", icon="🦂")
    Item(name="Lady Bug", icon="🐞")
    Item(name="Snail", icon="🐌")
    Item(name="Butterfly", icon="🦋")
    Item(name="Maple Leaf", icon="🍁")
    Item(name="Mushroom", icon="🍄")
    Item(name="Cactus", icon="🌵")
    Item(name="Christmas Tree", icon="🎄")
    Item(name="Clover", icon="☘️")
    Item(name="4 Leaf Clover", icon="🍀")
    Item(name="Tulip", icon="🌷")   
    Item(name="Rose", icon="🌹")
    Item(name="Sunflower", icon="🌻") 
    Item(name="Onion", icon="🧅") 
    Item(name="Egg", icon="🥚") 
    Item(name="Cheese", icon="🧀") 
    Item(name="Pancakes", icon="🥞") 
    Item(name="Fries", icon="🍟") 
    Item(name="Hamburger", icon="🍔") 
    Item(name="Sushi", icon="🍣") 
    Item(name="Dumpling", icon="🥟") 
    Item(name="Can of Soup", icon="🥫") 
    Item(name="Soccer Ball", icon="⚽") 
    Item(name="Basket Ball", icon="🏀") 
    Item(name="Football", icon="🏈") 
    Item(name="Baseball", icon="⚾") 
    Item(name="Tennis Ball", icon="🥎") 
    Item(name="Medal", icon="🏅") 
    Item(name="Dice", icon="🎲")
    Item(name="Scooter", icon="🛴")
    Item(name="Bicycle", icon="🚲")
    Item(name="Wheelchair", icon="🦽")
    Item(name="Anchor", icon="⚓")
    Item(name="Phone", icon="📱")
    Item(name="Watch", icon="⌚")
    Item(name="Pencil", icon="✏️")
    Item(name="Scissors", icon="✂️")
    Item(name="Paint Brush", icon="🖌️")
    Item(name="Crayon", icon="🖍️")

    Item(name="Scroll", icon="<:scroll:864727743206785045>", block=False)
    Item(name="Soul Stone", icon="<:SoulStone:864725973379186688>", block=False)
    Item(name="Purple Crystal", icon="<:PurpleCrystal:864725697833992222>", block=False)
    Item(name="Health Potion", icon="<:healthpotion:864727727357427753>", block=False)
    Item(name="Ember Insect", icon="<:emberedInsect:864725884212609054>", block=False)

    