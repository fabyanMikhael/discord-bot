from __future__ import annotations
from typing import Union
from GameLogic.Player import Player
from GameLogic.Items import Item
from Utils.ErrorHandling import TradeError

def IsTrading(user : Player) -> bool:
    return PendingTrade.IsTrading(user) or Trade.IsTrading(user)
    
def GetAnyTradeInvolving(user: Player) -> Union[PendingTrade, Trade]:
    if PendingTrade.IsTrading(user):
        return PendingTrade.GetTradeBy(user)
    if Trade.IsTrading(user):
        return Trade.GetTradeBy(user)
    raise TradeError(f"user {user} is not involved in any trades!")

def CancelAllTrades() -> None:
    for trade_id in PendingTrade.PENDING_TRADES.copy():
        trade : PendingTrade = PendingTrade.PENDING_TRADES[trade_id]
        trade.Cancel()
    for trade_id in Trade.TRADES.copy():
        trade : Trade = Trade.TRADES[trade_id]
        trade.Cancel()
    print("cancelled all trades")


class PendingTrade:
    PENDING_TRADES : dict[int, PendingTrade] = {}
    __slots__ = ["seller_items", "seller", "possible_traders", "id"]
    def __init__(self, Items_on_trade: dict[Item, int], seller : Player, possible_traders : list[Player], id : int) -> None:
        self.seller_items = Items_on_trade
        self.seller = seller
        self.possible_traders = possible_traders
        self.id = id
        PendingTrade.PENDING_TRADES[id] = self

    def Cancel(self) -> PendingTrade:
        self.seller.inventory.AddItems(items=self.seller_items)
        PendingTrade.PENDING_TRADES.pop(self.id)
        return self

    def CanTrade(self, Trader : Player) -> bool:
        return len(self.possible_traders) == 0 or Trader in self.possible_traders

    def ConvertToTrade(self, Trader : Player, items : dict[Item, int]) -> Trade:
        PendingTrade.PENDING_TRADES.pop(self.id)
        return Trade(UserOne=self.seller, UserTwo=Trader, UserOneItems=self.seller_items, UserTwoItems=items, id=self.id)

    @staticmethod
    def Has(id : int) -> bool:
        return id in PendingTrade.PENDING_TRADES
        
    @staticmethod
    def Get(id : int) -> PendingTrade:
        if id in PendingTrade.PENDING_TRADES:
            return PendingTrade.PENDING_TRADES[id]
        raise TradeError(f"Cannot get pending trade with id: {id} as it does not exist!")

    @staticmethod
    def GetTradesWith(user: Player) -> list[PendingTrade]:
        result = []
        for trade_id in PendingTrade.PENDING_TRADES:
            trade : PendingTrade = PendingTrade.PENDING_TRADES[trade_id]
            if user == trade.seller or user in trade.possible_traders:
                result.append(trade)
        return result

    @staticmethod
    def GetTradeBy(user: Player) -> PendingTrade:
        for trade_id in PendingTrade.PENDING_TRADES:
            trade : PendingTrade = PendingTrade.PENDING_TRADES[trade_id]
            if user == trade.seller:
                return trade
        raise TradeError(f"Cannot find any pending trade by {user}!")

    @staticmethod
    def IsTrading(user: Player) -> bool:
        for trade_id in PendingTrade.PENDING_TRADES:
            trade : PendingTrade = PendingTrade.PENDING_TRADES[trade_id]
            if user == trade.seller:
                return True
        return False

class Trade:
    TRADES : dict[int, Trade] = {}
    __slots__ = ["UserOne", "UserTwo", "UserOneItems", "UserTwoItems", "id"]
    def __init__(self, UserOne : Player, UserTwo : Player, UserOneItems : dict[Item, int], UserTwoItems : dict[Item, int], id : int) -> None:
        self.UserOne : Player = UserOne
        self.UserTwo : Player = UserTwo
        self.UserOneItems = UserOneItems
        self.UserTwoItems = UserTwoItems
        self.id = id
        Trade.TRADES[id] = self
    
    def Cancel(self) -> Trade:
        self.UserOne.inventory.AddItems(self.UserOneItems)
        self.UserTwo.inventory.AddItems(self.UserTwoItems)
        Trade.TRADES.pop(self.id)
        return self

    def confirm(self) -> None:
        self.UserOne.inventory.AddItems(self.UserTwoItems)
        self.UserTwo.inventory.AddItems(self.UserOneItems)
        Trade.TRADES.pop(self.id)

    @staticmethod
    def Get(id : int) -> Trade:
        if id in Trade.TRADES:
            return Trade.TRADES[id]
        raise TradeError(f"Cannot get trade with id: {id} as it does not exist!")

    @staticmethod
    def GetTradesWith(user: Player) -> list[Trade]:
        result = []
        for trade_id in Trade.TRADES:
            trade : Trade = Trade.TRADES[trade_id]
            if user == trade.UserOne or user == trade.UserTwo:
                result.append(trade)
        return result

    @staticmethod
    def CancelTradesWith(id : str) -> list[Trade]:
        user = Player.GetPlayer(id)
        result = []
        for trade_id in Trade.TRADES.copy():
            trade : Trade = Trade.TRADES[trade_id]
            if user == trade.UserOne or user == trade.UserTwo:
                trade.Cancel()
        return result

    @staticmethod
    def GetTradeBy(user: Player) -> Trade:
        for trade_id in Trade.TRADES:
            trade : Trade = Trade.TRADES[trade_id]
            if user == trade.UserOne or user == trade.UserTwo:
                return trade
        raise TradeError(f"Cannot find any trade involving {user}!")

    @staticmethod
    def IsTrading(user: Player) -> bool:
        for trade_id in Trade.TRADES:
            trade : Trade = Trade.TRADES[trade_id]
            if user == trade.UserOne or user == trade.UserTwo:
                return True
        return False