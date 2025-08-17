from dataclasses import dataclass

@dataclass
class Category:
    SCHOOL = "school"
    
@dataclass
class FriendshipStatus:
    INVITE_SENT = "INVITE_SENT"
    INVITE_RECEIVED = "INVITE_RECEIVED"
    FRIEND = "FRIEND"
    VOID = "VOID"
    
@dataclass
class Direction:
    ASC = "ASC"
    DESC = "DESC"
    
@dataclass
class Currency:
    RUB = "RUB"
    EUR = "EUR"
    USD = "USD"
    KZT = "KZT"
    ALL = [RUB, EUR, USD, KZT]