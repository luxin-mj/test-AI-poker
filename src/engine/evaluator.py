"""
Hand strength and equity evaluation
手牌强度和期望值评估系统
"""

from typing import List, Tuple, Dict, Optional, Set
from itertools import combinations
from collections import Counter
import random
from ..core.card import Card, Hand, Rank, Suit
from ..core.game_state import GameState
from ..utils.constants import Stage, Position, POSITION_WEIGHTS_6MAX

class HandRank:
    """
    手牌等级定义
    """
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9

class HandEvaluator:
    """
    手牌评估器：计算手牌强度和胜率
    """
    
    @staticmethod
    def _get_rank_counts(cards: List[Card]) -> Dict[Rank, int]:
        """获取每个点数的数量"""
        return Counter(card.rank for card in cards)
    
    @staticmethod
    def _get_suit_counts(cards: List[Card]) -> Dict[Suit, int]:
        """获取每个花色的数量"""
        return Counter(card.suit for card in cards)
    
    @staticmethod
    def _has_straight(ranks: Set[int]) -> Optional[int]:
        """
        检查是否有顺子
        :return: 顺子的最大牌值，如果没有则返回None
        """
        # 处理A可以当1用的特殊情况
        if 14 in ranks:  # Ace
            ranks.add(1)
            
        ranks = sorted(ranks)
        count = 1
        max_rank = ranks[0]
        
        for i in range(1, len(ranks)):
            if ranks[i] == ranks[i-1] + 1:
                count += 1
                if count >= 5:
                    max_rank = ranks[i]
            else:
                count = 1
                
        return max_rank if count >= 5 else None

    @staticmethod
    def evaluate_hand_strength(cards: List[Card]) -> Tuple[int, List[int]]:
        """
        评估一手牌的强度
        :return: (牌型等级, [用于比较的关键牌值])
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")
            
        # 获取点数和花色统计
        rank_counts = HandEvaluator._get_rank_counts(cards)
        suit_counts = HandEvaluator._get_suit_counts(cards)
        
        # 获取所有点数值
        ranks = {card.rank.value for card in cards}
        
        # 检查同花
        flush_suit = next(
            (suit for suit, count in suit_counts.items() if count >= 5),
            None
        )
        
        # 检查顺子
        straight_high = HandEvaluator._has_straight(ranks)
        
        # 如果有同花和顺子，检查是否是同花顺
        if flush_suit and straight_high:
            flush_cards = [card for card in cards if card.suit == flush_suit]
            flush_ranks = {card.rank.value for card in flush_cards}
            straight_flush_high = HandEvaluator._has_straight(flush_ranks)
            
            if straight_flush_high:
                # 检查是否是皇家同花顺
                if straight_flush_high == 14:
                    return (HandRank.ROYAL_FLUSH, [14])
                return (HandRank.STRAIGHT_FLUSH, [straight_flush_high])
        
        # 检查四条
        quads = [rank for rank, count in rank_counts.items() if count == 4]
        if quads:
            kicker = max(rank for rank in rank_counts if rank not in quads)
            return (HandRank.FOUR_OF_A_KIND, [quads[0].value, kicker.value])
            
        # 检查葫芦
        trips = [rank for rank, count in rank_counts.items() if count == 3]
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if trips and pairs:
            return (HandRank.FULL_HOUSE, [trips[0].value, pairs[0].value])
            
        # 检查同花
        if flush_suit:
            flush_cards = [card for card in cards if card.suit == flush_suit]
            flush_values = sorted([card.rank.value for card in flush_cards], reverse=True)
            return (HandRank.FLUSH, flush_values[:5])
            
        # 检查顺子
        if straight_high:
            return (HandRank.STRAIGHT, [straight_high])
            
        # 检查三条
        if trips:
            kickers = sorted(
                [rank.value for rank in rank_counts if rank != trips[0]],
                reverse=True
            )
            return (HandRank.THREE_OF_A_KIND, [trips[0].value] + kickers[:2])
            
        # 检查两对
        if len(pairs) >= 2:
            pairs_values = sorted([p.value for p in pairs], reverse=True)
            kicker = max(rank.value for rank in rank_counts if rank not in pairs)
            return (HandRank.TWO_PAIR, pairs_values[:2] + [kicker])
            
        # 检查一对
        if pairs:
            kickers = sorted(
                [rank.value for rank in rank_counts if rank != pairs[0]],
                reverse=True
            )
            return (HandRank.PAIR, [pairs[0].value] + kickers[:3])
            
        # 高牌
        high_cards = sorted([card.rank.value for card in cards], reverse=True)
        return (HandRank.HIGH_CARD, high_cards[:5])

    @staticmethod
    def compare_hands(hand1: List[Card], hand2: List[Card]) -> int:
        """
        比较两手牌的大小
        :return: 1 if hand1 wins, -1 if hand2 wins, 0 if tie
        """
        rank1, values1 = HandEvaluator.evaluate_hand_strength(hand1)
        rank2, values2 = HandEvaluator.evaluate_hand_strength(hand2)
        
        if rank1 > rank2:
            return 1
        if rank1 < rank2:
            return -1
            
        # 同等牌型，比较关键牌值
        for v1, v2 in zip(values1, values2):
            if v1 > v2:
                return 1
            if v1 < v2:
                return -1
                
        return 0

    @staticmethod
    def calculate_preflop_rank(hand: Hand) -> float:
        """
        计算前翻牌圈手牌等级
        返回0-1之间的值，1表示最强
        """
        if len(hand.cards) != 2:
            raise ValueError("Preflop hand must have exactly 2 cards")
            
        card1, card2 = hand.cards
        
        # 计算基础分值
        base_score = 0.0
        
        # 成对加分
        if hand.is_pair():
            base_score += 0.5
            # AA得到最高分
            if card1.rank.rank_value == 14:  # Ace
                base_score += 0.5
                
        # 同花加分
        if hand.is_suited():
            base_score += 0.2
            
        # 高牌分值
        high_card = max(card1.rank.rank_value, card2.rank.rank_value)
        low_card = min(card1.rank.rank_value, card2.rank.rank_value)
        
        # 将牌值转换为0-1分值
        high_score = (high_card - 2) / 12  # 2->0, A->1
        low_score = (low_card - 2) / 12
        
        # 综合计算
        score = base_score + 0.2 * high_score + 0.1 * low_score
        
        # 确保分值在0-1之间
        return min(1.0, max(0.0, score))

class EquityCalculator:
    """
    计算精确胜率
    """
    
    @staticmethod
    def _create_deck(excluded_cards: List[Card]) -> List[Card]:
        """创建一副排除了已知牌的牌组"""
        all_cards = []
        for rank in Rank:
            for suit in Suit:
                card = Card(rank, suit)
                if not any(c.rank == card.rank and c.suit == card.suit for c in excluded_cards):
                    all_cards.append(card)
        return all_cards

    @staticmethod
    def calculate_equity(
        hand: Hand,
        board: List[Card],
        num_opponents: int = 1,
        num_simulations: int = 1000
    ) -> float:
        """
        使用蒙特卡洛模拟计算胜率
        """
        wins = 0
        
        # 创建剩余牌组
        deck = EquityCalculator._create_deck(hand.cards + board)
        
        for _ in range(num_simulations):
            # 洗牌
            random.shuffle(deck)
            
            # 为对手发牌
            opponent_cards = []
            for _ in range(num_opponents):
                opponent_cards.extend(deck[:2])
                deck = deck[2:]
            
            # 补齐公共牌
            remaining_board = deck[:5-len(board)]
            full_board = board + remaining_board
            
            # 计算我们的最终牌力
            our_hand = hand.cards + full_board
            our_score = HandEvaluator.evaluate_hand_strength(our_hand)
            
            # 计算对手的牌力
            won_hand = True
            for i in range(0, len(opponent_cards), 2):
                opponent_hand = opponent_cards[i:i+2] + full_board
                opponent_score = HandEvaluator.evaluate_hand_strength(opponent_hand)
                
                if HandEvaluator.compare_hands(our_hand, opponent_hand) <= 0:
                    won_hand = False
                    break
            
            if won_hand:
                wins += 1
        
        return wins / num_simulations

class PotOddsCalculator:
    """
    底池赔率计算器
    """
    
    @staticmethod
    def calculate_pot_odds(to_call: int, pot_size: int) -> float:
        """
        计算底池赔率
        :return: 赔率的比例值(0-1)
        """
        if pot_size == 0 or to_call == 0:
            return 0.0
        return to_call / (pot_size + to_call)
    
    @staticmethod
    def calculate_implied_odds(
        to_call: int,
        pot_size: int,
        effective_stack: int
    ) -> float:
        """
        计算隐含赔率
        """
        return (pot_size + effective_stack) / to_call
    
    @staticmethod
    def should_continue(equity: float, pot_odds: float, implied_odds: float = 1.0) -> bool:
        """
        根据期望值和底池赔率判断是否应该继续
        """
        required_equity = pot_odds / implied_odds
        return equity > required_equity

class PositionEvaluator:
    """
    位置评估器
    """
    
    @staticmethod
    def get_position_value(
        position: Position,
        total_players: int = 6
    ) -> float:
        """
        获取位置价值
        """
        return POSITION_WEIGHTS_6MAX[position]
        
    @staticmethod
    def adjust_by_position(base_value: float, position: Position) -> float:
        """
        根据位置调整基础值
        """
        position_value = PositionEvaluator.get_position_value(position)
        return base_value * position_value

    @staticmethod
    def get_positions_to_act(current_position: Position, total_players: int = 6) -> List[Position]:
        """
        获取还要行动的位置列表
        """
        position_order = list(Position)
        current_index = position_order.index(current_position)
        return position_order[current_index+1:] + position_order[:current_index]