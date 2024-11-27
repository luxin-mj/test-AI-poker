"""
Poker actions and decision making
扑克行动和决策相关的类
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from ..utils.constants import Action, Stage, Position, STANDARD_PREFLOP_RAISES, STANDARD_POSTFLOP_BETS
from .game_state import GameState

@dataclass
class ActionOption:
    """
    表示一个可能的行动选项
    """
    action: Action
    min_amount: int = 0    # 最小金额（如果适用）
    max_amount: int = 0    # 最大金额（如果适用）
    
    def is_valid_amount(self, amount: int) -> bool:
        """检查金额是否在有效范围内"""
        if self.action in [Action.FOLD, Action.CHECK]:
            return amount == 0
        return self.min_amount <= amount <= self.max_amount

class ActionManager:
    """
    管理游戏中的行动
    """
    
    @staticmethod
    def get_valid_actions(game_state: GameState) -> List[ActionOption]:
        """
        获取当前状态下所有合法的行动
        """
        valid_actions = []
        to_call = game_state.to_call
        my_stack = game_state.my_stack
        
        # FOLD总是可选的
        valid_actions.append(ActionOption(Action.FOLD))
        
        # 检查是否可以CHECK
        if to_call == 0:
            valid_actions.append(ActionOption(Action.CHECK))
        
        # 检查是否可以CALL
        if to_call > 0 and to_call <= my_stack:
            valid_actions.append(ActionOption(Action.CALL, to_call, to_call))
        
        # 检查是否可以RAISE
        if my_stack > to_call:
            min_raise = max(to_call * 2, game_state.current_pot * 0.5)
            valid_actions.append(
                ActionOption(Action.RAISE, min_raise, my_stack)
            )
            
        return valid_actions
    
    @staticmethod
    def get_standard_bet_sizes(game_state: GameState) -> Dict[str, int]:
        """
        获取标准下注尺度
        """
        pot_size = game_state.current_pot
        
        if game_state.current_stage == Stage.PREFLOP:
            return {
                name: size * game_state.to_call 
                for name, size in STANDARD_PREFLOP_RAISES.items()
            }
        else:
            return {
                name: int(size * pot_size)
                for name, size in STANDARD_POSTFLOP_BETS.items()
            }
    
    @staticmethod
    def validate_action(game_state: GameState, action: Action, amount: int = 0) -> bool:
        """
        验证行动是否合法
        """
        valid_actions = ActionManager.get_valid_actions(game_state)
        
        # 找到匹配的行动选项
        matching_option = next(
            (opt for opt in valid_actions if opt.action == action),
            None
        )
        
        if not matching_option:
            return False
            
        return matching_option.is_valid_amount(amount)
    
    @staticmethod
    def execute_action(game_state: GameState, action: Action, amount: int = 0) -> None:
        """
        执行一个行动并更新游戏状态
        """
        if not ActionManager.validate_action(game_state, action, amount):
            raise ValueError("Invalid action or amount")
            
        # 记录行动
        game_state.record_action(game_state.my_position, action, amount)
        
        # 特殊处理
        if action == Action.RAISE:
            game_state.to_call = amount