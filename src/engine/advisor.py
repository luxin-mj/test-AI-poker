"""
Poker strategy advisor
策略建议系统
"""

from typing import Dict, List, Tuple, Optional
from ..core.game_state import GameState
from ..core.action import Action, ActionManager
from ..utils.constants import Stage, Position, STANDARD_PREFLOP_RAISES, STANDARD_POSTFLOP_BETS
from .evaluator import HandEvaluator, EquityCalculator, PotOddsCalculator, PositionEvaluator

class Decision:
    """
    决策结果类
    """
    def __init__(
        self,
        action: Action,
        amount: int = 0,
        confidence: float = 0.0,
        reasoning: List[str] = None
    ):
        self.action = action
        self.amount = amount
        self.confidence = confidence
        self.reasoning = reasoning or []

class PokerAdvisor:
    """
    扑克策略顾问
    """
    
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
        self.equity_calculator = EquityCalculator()
        self.pot_odds_calculator = PotOddsCalculator()
        self.position_evaluator = PositionEvaluator()
    
    def get_preflop_advice(self, game_state: GameState) -> Decision:
        """
        获取前翻牌圈建议
        """
        # 计算手牌强度
        hand_strength = self.hand_evaluator.calculate_preflop_rank(game_state.my_hand)
        
        # 根据位置调整
        position_adjusted_strength = self.position_evaluator.adjust_by_position(
            hand_strength,
            game_state.my_position
        )
        
        # 获取可能的行动
        valid_actions = ActionManager.get_valid_actions(game_state)
        
        # 决策逻辑
        reasoning = [
            f"手牌强度: {hand_strength:.2f}",
            f"位置调整后强度: {position_adjusted_strength:.2f}"
        ]
        
        # 如果没有人加注（开池情况）
        if game_state.to_call == 0:
            if position_adjusted_strength > 0.7:
                # 强牌大加注
                amount = STANDARD_PREFLOP_RAISES["LARGE"] * game_state.to_call or 3
                return Decision(Action.RAISE, amount, 0.9, reasoning + ["强势手牌，主动加注"])
            elif position_adjusted_strength > 0.5:
                # 中等牌标准加注
                amount = STANDARD_PREFLOP_RAISES["STANDARD"] * game_state.to_call or 2.5
                return Decision(Action.RAISE, amount, 0.8, reasoning + ["中等强度，标准加注"])
            elif position_adjusted_strength > 0.3:
                # 弱牌但位置好可以偷池
                if game_state.my_position in [Position.BTN, Position.CO]:
                    amount = STANDARD_PREFLOP_RAISES["MIN"] * game_state.to_call or 2
                    return Decision(Action.RAISE, amount, 0.6, reasoning + ["利用位置偷池"])
            
            return Decision(Action.FOLD, 0, 0.7, reasoning + ["手牌太弱，放弃"])
            
        # 面对加注
        else:
            # 计算底池赔率
            pot_odds = self.pot_odds_calculator.calculate_pot_odds(
                game_state.to_call,
                game_state.current_pot
            )
            reasoning.append(f"底池赔率: {pot_odds:.2f}")
            
            if position_adjusted_strength > 0.8:
                # 重加注
                amount = game_state.to_call * 3
                return Decision(Action.RAISE, amount, 0.9, reasoning + ["强牌重加注"])
            elif position_adjusted_strength > pot_odds * 1.5:
                return Decision(Action.CALL, game_state.to_call, 0.8, reasoning + ["手牌强度足够跟注"])
            else:
                return Decision(Action.FOLD, 0, 0.7, reasoning + ["赔率不够，放弃"])
    
    def get_postflop_advice(self, game_state: GameState) -> Decision:
        """
        获取翻牌后建议
        """
        # 计算当前胜率
        equity = self.equity_calculator.calculate_equity(
            game_state.my_hand,
            game_state.get_current_street_state().community_cards
        )
        
        # 计算底池赔率
        pot_odds = self.pot_odds_calculator.calculate_pot_odds(
            game_state.to_call,
            game_state.current_pot
        )
        
        reasoning = [
            f"当前胜率: {equity:.2f}",
            f"底池赔率: {pot_odds:.2f}"
        ]
        
        # 如果没人下注
        if game_state.to_call == 0:
            if equity > 0.7:
                # 强牌大注
                amount = int(game_state.current_pot * STANDARD_POSTFLOP_BETS["LARGE"])
                return Decision(Action.RAISE, amount, 0.9, reasoning + ["强牌下大注"])
            elif equity > 0.5:
                # 中等牌中注
                amount = int(game_state.current_pot * STANDARD_POSTFLOP_BETS["MEDIUM"])
                return Decision(Action.RAISE, amount, 0.8, reasoning + ["中等强度，价值下注"])
            else:
                return Decision(Action.CHECK, 0, 0.7, reasoning + ["手牌较弱，过牌观望"])
                
        # 面对下注
        else:
            # 计算隐含赔率
            implied_odds = self.pot_odds_calculator.calculate_implied_odds(
                game_state.to_call,
                game_state.current_pot,
                game_state.my_stack
            )
            reasoning.append(f"隐含赔率: {implied_odds:.2f}")
            
            if equity > 0.8:
                # 重注
                amount = game_state.to_call * 3
                return Decision(Action.RAISE, amount, 0.9, reasoning + ["强牌重注"])
            elif equity > pot_odds:
                return Decision(Action.CALL, game_state.to_call, 0.8, reasoning + ["赔率合适，跟注"])
            elif equity * implied_odds > pot_odds:
                return Decision(Action.CALL, game_state.to_call, 0.6, reasoning + ["基于隐含赔率跟注"])
            else:
                return Decision(Action.FOLD, 0, 0.7, reasoning + ["赔率不够，放弃"])
    
    def get_advice(self, game_state: GameState) -> Decision:
        """
        获取完整的行动建议
        """
        if game_state.current_stage == Stage.PREFLOP:
            return self.get_preflop_advice(game_state)
        else:
            return self.get_postflop_advice(game_state)