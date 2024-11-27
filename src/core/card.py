"""
Poker card related classes and utilities
包含扑克牌相关的类和工具函数
"""

from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass

class Suit(Enum):
    """花色枚举"""
    SPADES = 's'    # 黑桃
    HEARTS = 'h'    # 红心
    DIAMONDS = 'd'  # 方块
    CLUBS = 'c'     # 梅花

class Rank(Enum):
    """
    牌面值枚举
    symbol: 显示符号
    rank_value: 数值大小
    """
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = 'T'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

    @property
    def rank_value(self) -> int:
        """获取牌面的数值"""
        values = {
            'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
            '9': 9, '8': 8, '7': 7, '6': 6, '5': 5,
            '4': 4, '3': 3, '2': 2
        }
        return values[self.value]

@dataclass
class Card:
    """
    扑克牌类，包含牌面值和花色
    """
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        """返回牌的字符串表示，如'Ah'表示红心A"""
        return f"{self.rank.value}{self.suit.value}"

    def __eq__(self, other: 'Card') -> bool:
        """比较两张牌是否相等"""
        return self.rank == other.rank and self.suit == other.suit
    
    def __lt__(self, other: 'Card') -> bool:
        """比较两张牌的大小"""
        return self.rank.rank_value < other.rank.rank_value

    @classmethod
    def from_string(cls, card_str: str) -> 'Card':
        """
        从字符串创建Card对象
        :param card_str: 牌的字符串表示，如'Ah'表示红心A
        :return: Card对象
        """
        if len(card_str) != 2:
            raise ValueError("Invalid card string format")
        
        # 解析rank和suit
        rank_char = card_str[0].upper()
        suit_char = card_str[1].lower()

        # 找到对应的Rank枚举
        rank = next((r for r in Rank if r.value == rank_char), None)
        if not rank:
            raise ValueError(f"Invalid rank: {rank_char}")

        # 找到对应的Suit枚举
        suit = next((s for s in Suit if s.value == suit_char), None)
        if not suit:
            raise ValueError(f"Invalid suit: {suit_char}")

        return cls(rank, suit)

@dataclass
class Hand:
    """
    手牌类，表示一组牌（通常是两张）
    """
    cards: List[Card]

    @classmethod
    def from_string(cls, hand_str: str) -> 'Hand':
        """
        从字符串创建手牌对象
        :param hand_str: 手牌字符串，如'AhKh'表示红心AK
        :return: Hand对象
        """
        if len(hand_str) != 4:
            raise ValueError("Invalid hand string format")
        
        # 分割成两张牌的字符串
        card1_str = hand_str[:2]
        card2_str = hand_str[2:]
        
        # 创建两张Card对象
        card1 = Card.from_string(card1_str)
        card2 = Card.from_string(card2_str)
        
        return cls([card1, card2])

    def __str__(self) -> str:
        """返回手牌的字符串表示"""
        return ''.join(str(card) for card in self.cards)

    def is_suited(self) -> bool:
        """判断是否同花"""
        return len(self.cards) == 2 and self.cards[0].suit == self.cards[1].suit

    def is_pair(self) -> bool:
        """判断是否对子"""
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank