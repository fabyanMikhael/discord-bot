from __future__ import annotations

from Utils.ErrorHandling import ShopError
from GameLogic.Player import  Player
from GameLogic.Items import Item
from Utils.Constants import CURRENCY_SYMBOL, PAGE_ITEM_LIMIT
from Utils.Database import ShopDatabase
import random, string

class Sale:
    __slots__ = ["item", "amount", "price", "seller", "shop", "id"]
    def __init__(self, item : Item, amount : int, price : int, seller : Player) -> None:
        self.item = item
        self.amount = amount
        self.price = price
        self.seller = seller
        self.shop : Shop = None
        self.id : int = None

    def ToDict(self) -> dict:
        result = {}
        result['item'] = self.item.id
        result['amount'] = self.amount
        result['price'] = self.price
        result['seller'] = self.seller.id
        return result

    @staticmethod
    def FromDict(data : dict) -> Sale:
        result = Sale(  item   = Item.GetItem(id=data['item']),
                        amount = data['amount'],
                        price  = data['price'],
                        seller = Player.GetPlayer(id=data['seller']))
        return result

    def __repr__(self) -> str:
        return f"[**{self.id}**] - {self.item} `x{self.amount}` : `{CURRENCY_SYMBOL}{self.price}`"

    def Buy(self, client : Player) -> None:
        if client.balance < self.price:
            raise ShopError(f"You cannot buy {self.item} as you do not have enough money!")
        client.inventory.AddItem(self.item, self.amount)
        client.balance -= self.price
        self.seller.balance += self.price
        self.RemoveFromAuction()

    def Cancel(self, remove = True) -> None:
        self.seller.inventory.AddItem(self.item, self.amount)
        if remove: self.RemoveFromAuction()

    def RemoveFromAuction(self) -> None:
        if self.shop == None: raise ValueError("attempted to remove sale from non-existent auction!")
        self.shop.RemoveSale(self.id)

class Shop:
    __slots__ = ["auction"]
    def __init__(self) -> None:
        self.auction : dict[int, Sale] = {}

    #SALE_ID: int = 0
    def AddSale(self, sale : Sale, first_time = True) -> Sale:
        #################ID LOGIC#################
        amount = 3
        while amount ** 36 < len(self.auction):
            amount += 1
        id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(3))
        while id in self.auction:
            id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(3))
        ##########################################
        sale.id = id
        sale.shop = self
        self.auction[id] = sale
        
        if first_time:
            ShopDatabase.Insert(sale.seller.id, sale.ToDict())
        return sale

    def GetSale(self, id : str) -> Sale:
        if id in self.auction:
            return self.auction[id]
        raise ValueError(f"cannot find sale with id: {id}")
    
    def GetAllSales(self) -> list[Sale]:
        return list(self.auction.values())

    def GetAllSalesFor(self, user : Player) -> list[Sale]:
        result : list[Sale] = [] 
        for sale_id in self.auction:
            sale = self.auction[sale_id]
            if sale.seller == user:
                result.append(sale)
        return result

    def HasSale(self, id : str) -> bool:
        return (id in self.auction)

    def ToPages(self) -> list[str]:
        return Shop.__ToPages__(items= self.auction)

    @staticmethod
    def __ToPages__(items : dict[int, Sale]) -> list[str]:
        pages = []
        result = "\u200b"
        for (idx,sale_id) in enumerate(items):
            if idx % PAGE_ITEM_LIMIT == 0 and idx != 0:
                pages.append(result)
                result = "\u200b"
            sale = items[sale_id]
            result += f"{sale}\n"
        pages.append(result)
        return pages

    def RemoveSale(self, id : int) -> Shop:
        sale = self.auction.pop(id)
        ShopDatabase.Delete({'seller': sale.seller.id, 'item': sale.item.id, 'amount': sale.item.id, 'price': sale.price})
        return self

    def __repr__(self) -> str:
        result = "\u200b"
        for sale_id in self.auction:
            sale = self.auction[sale_id]
            result += f"{sale}\n"
        return result

    def LoadAll(self):
        sales = ShopDatabase.GetAll()
        for sale in sales:
            self.AddSale(sale = Sale.FromDict(sale), first_time=False)