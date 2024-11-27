"""
Game state management classes
管理游戏状态的相关类
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from ..utils.constants import Position, Stage, Action
from .card import Card, Hand

@dataclass
class ActionRecord:
    """记录一个动作的详细信息"""
    player_position: Position  # 玩家位置
    action: Action           # 动作类型
    amount: int = 0         # 动作金额（如果适用）
    
@dataclass
class StreetState:
    """一条街的状态"""
    community_cards: List[Card] = field(default_factory=list)  # 公共牌
    pot_size: int = 0                                         # 底池大小
    actions: List[ActionRecord] = field(default_factory=list)  # 动作记录
    
@dataclass
class GameState:
    """
    跟踪完整的游戏状态
    """
    # 基础信息
    my_hand: Hand                       # 我的手牌
    my_position: Position               # 我的位置
    my_stack: int                       # 我的筹码
    total_players: int = 6              # 总玩家数（默认6人局）
    
    # 当前状态
    current_stage: Stage = Stage.PREFLOP  # 当前阶段
    to_call: int = 0                      # 需要跟注的金额
    current_pot: int = 0                  # 当前底池大小
    
    # 每个阶段的详细信息
    preflop_state: StreetState = field(default_factory=StreetState)
    flop_state: StreetState = field(default_factory=StreetState)
    turn_state: StreetState = field(default_factory=StreetState)
    river_state: StreetState = field(default_factory=StreetState)
    
    # 位置到筹码的映射
    stacks: Dict[Position, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后的处理"""
        # 确保stacks包含所有位置
        if not self.stacks:
            self.stacks = {pos: 0 for pos in Position}
            self.stacks[self.my_position] = self.my_stack
    
    def get_current_street_state(self) -> StreetState:
        """获取当前阶段的状态"""
        if self.current_stage == Stage.PREFLOP:
            return self.preflop_state
        elif self.current_stage == Stage.FLOP:
            return self.flop_state
        elif self.current_stage == Stage.TURN:
            return self.turn_state
        else:  # RIVER
            return self.river_state
    
    def record_action(self, position: Position, action: Action, amount: int = 0):
        """
        记录一个动作
        :param position: 执行动作的位置
        :param action: 动作类型
        :param amount: 动作金额（如果适用）
        """
        street_state = self.get_current_street_state()
        record = ActionRecord(position, action, amount)
        street_state.actions.append(record)
        
        # 更新底池大小
        if action in [Action.CALL, Action.RAISE, Action.ALL_IN]:
            street_state.pot_size += amount
            self.current_pot = street_state.pot_size
            
            # 更新玩家筹码
            if position in self.stacks:
                self.stacks[position] -= amount
    
    def advance_stage(self):
        """推进到下一个阶段"""
        if self.current_stage == Stage.PREFLOP:
            self.current_stage = Stage.FLOP
        elif self.current_stage == Stage.FLOP:
            self.current_stage = Stage.TURN
        elif self.current_stage == Stage.TURN:
            self.current_stage = Stage.RIVER
            
    def add_community_cards(self, cards: List[Card]):
        """
        添加公共牌
        :param cards: 要添加的公共牌列表
        """
        street_state = self.get_current_street_state()
        street_state.community_cards.extend(cards)