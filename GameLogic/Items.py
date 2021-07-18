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
    CATEGORIES : dict[str, list[Item]] = {}
    ID_COUNTER = 0
    def __init__(self, name : str, icon : str, id : int = None, block=True, rarity : str = "common", category : str = None) -> None:
        if id == None:
            id = Item.ID_COUNTER
            Item.ID_COUNTER += 1
        self.id = id
        self.icon = f"`{icon}`" if block else icon
        self.name = name
        self.rarity = rarity
        Item.ITEMS[id] = self
        Item.NAME_TO_ITEM[name.lower()] = self
        if category != None:
            category = category.lower()
            if not category in Item.CATEGORIES: Item.CATEGORIES[category] = []
            Item.CATEGORIES[category].append(self)
        Item.RARITY[rarity].append(self)

    def SetName(self, name : str) -> Item:
        self.name = name
        return self

    def SetRarity(self, rarity : str) -> Item:
        self.rarity = rarity
        return self

    def AddToCategory(self, category : str) -> Item:
        category = category.lower()
        if not category in Item.CATEGORIES: Item.CATEGORIES[category] = []
        Item.CATEGORIES[category].append(self)
        return self

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

    @staticmethod
    def GetRandomItemFrom(category : str) -> Item:
        """grabs a random item from the specified category in the static variables"""
        Item.LoadItems()
        if not category in Item.CATEGORIES: raise InventoryError(f"cannot find category: {category}")
        item = random.choice( Item.CATEGORIES[category] )
        return item

    @staticmethod
    def GetRandomItems(count : int) -> list:
        """returns a list of random items"""
        items = []
        for _ in range(count):
            items.append( Item.GetRandomItem() )
        return items

    @staticmethod
    def GetRandomItemsFrom(category : str, count : int) -> list[Item]:
        """returns a list of random items from the specified category"""
        items = []
        for _ in range(count):
            items.append( Item.GetRandomItemFrom(category) )
        return items

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

    def Clear(self) -> dict[Item, int]:
        old = self.items
        self.items = {}
        return old

    def GetItemCount(self, item : Item) -> int:
        return self.items.get(item, 0)

    def GetRandomItems(self, count : int) -> dict[Item, int]:
        """returns a dictionary of random items from the user's inventory. if the user has less items than count, all of them will be returned"""
        if count > self.GetTotalItems():
            return self.items.copy()
        items = {}
        for _ in range(count):
            item = random.choice( list(self.items) )
            if item in items:
                while items[item] >= self.items[item]:
                    item = random.choice( list(self.items) )
            items[item] = items.get(item, 0) + 1
        return items

    @staticmethod
    def GetDictAsList(items) -> list[Item]:
        """returns a list from a dictionary of items->int"""
        result = []
        for item in items:
            for _ in range(items[item]):
                result.append(item)
        return result

    def GetTotalItems(self) -> int:
        return sum(self.items.values())

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
    Item(name="water droplet", icon="💧").AddToCategory("plants")
    Item(name="X Seed", icon="🌱").AddToCategory("plants")
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

    Item(name="Grapes", icon="🍇").AddToCategory("plants")
    Item(name="Melon", icon="🍈").AddToCategory("plants")
    Item(name="Watermelon", icon="🍉").AddToCategory("plants")
    Item(name="Tangerine", icon="🍊").AddToCategory("plants")
    Item(name="Lemon", icon="🍋").AddToCategory("plants")
    Item(name="Banana", icon="🍌").AddToCategory("plants")
    Item(name="Pineapple", icon="🍍").AddToCategory("plants")
    Item(name="Mango", icon="🥭").AddToCategory("plants")
    Item(name="Apple", icon="🍎").AddToCategory("plants")
    Item(name="Green Apple", icon="🍏").AddToCategory("plants")
    Item(name="Pear", icon="🍐").AddToCategory("plants")
    Item(name="Peach", icon="🍑").AddToCategory("plants")
    Item(name="Cherries", icon="🍒").AddToCategory("plants")

    Item(name="Satellite", icon="🛰️")
    Item(name="Rocket", icon="🚀")
    Item(name="Parachute", icon="🪂")
    Item(name="Seat", icon="💺")
    Item(name="Helicopter", icon="🚁")

    Item(name="Fireworks", icon="🎆")
    Item(name="Sparkler", icon="🎇")

    Item(name="Bee", icon="🐝").AddToCategory("bees")
    Item(name="Honey", icon="🍯").AddToCategory("bees")
    Item(name="Teddy bear", icon="🧸")
    Item(name="Lootbox", icon="📦").AddToCategory("lootbox")
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
    Item(name="Clover", icon="☘️").AddToCategory("plants").AddToCategory("usable")
    Item(name="Four Leaf Clover", icon="🍀").AddToCategory("plants").AddToCategory("usable")
    Item(name="Tulip", icon="🌷").AddToCategory("plants")
    Item(name="Rose", icon="🌹").AddToCategory("plants")
    Item(name="Sunflower", icon="🌻").AddToCategory("plants")
    Item(name="Onion", icon="🧅").AddToCategory("plants")
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
    Item(name="Dice", icon="🎲").AddToCategory("usable")
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

    Item(name="Arctic Parasite Seed", icon="<:arcticParasitePlant:865436985237176330>", block=False).AddToCategory("plants").AddToCategory("arctic")
    Item(name="Arctic Parasite", icon="<:arcticParasite:865437942851043338>", block=False).AddToCategory("plants").AddToCategory("arctic").AddToCategory("usable")

    Item(name="Wooden Seed", icon="<:WoodenSeed:865434094917124157>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Rhino", icon="<:WoodenRino:865434109962878996>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Bear", icon="<:WoodenBear:865438515784581170>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Boar", icon="<:WoodenBoar:865438515293847563>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Bunny", icon="<:WoodenBunny:865438515897303040>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Moose", icon="<:WoodenMoose:865438515989708810>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Owl", icon="<:WoodenOwl:865438515541573652>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Snail", icon="<:WoodenSnail:865438515617726487>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wooden Squirrel", icon="<:WoodenSquirrel:865438515764265020>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wood Log", icon="<:WoodenLog:865439400723611648>", block=False).AddToCategory("plants").AddToCategory("wooden")
    Item(name="Wood Plank", icon="<:WoodPlank:865439400691630120>", block=False).AddToCategory("plants").AddToCategory("wooden")


    Item(name="Devil's Feathers", icon="<:ArcticDevilsfeathers:865452032965345340>", block=False).AddToCategory("arctic").AddToCategory("devil")
    Item(name="Axe", icon="<:Axe:865452032894697502>", block=False).AddToCategory("Barbarian")
    Item(name="arrows", icon="<:arrows:865452032513409075>", block=False).AddToCategory("Barbarian")
    Item(name="Fish", icon="<:Fish_:865452032378535947>", block=False).AddToCategory("Barbarian")
    Item(name="Barbarian Helmet", icon="<:BarbarianHelmet:865452032579469332>", block=False).AddToCategory("Barbarian")
    Item(name="Dagger", icon="<:Dagger:865452032541196298>", block=False).AddToCategory("Barbarian")
    Item(name="Bow", icon="<:Bow:865452032756154398>", block=False).AddToCategory("Barbarian")