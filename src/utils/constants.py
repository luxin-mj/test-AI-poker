"""
Poker game constants and enums
包含扑克游戏中使用的所有常量和枚举定义
"""

from enum import Enum
from typing import Dict

class Position(Enum):
    """
    6-max德州扑克的位置枚举
    UTG: Under the Gun
    MP: Middle Position
    CO: Cut Off
    BTN: Button
    SB: Small Blind
    BB: Big Blind
    """
    UTG = "UTG"
    MP = "MP"
    CO = "CO"
    BTN = "BTN"  
    SB = "SB"
    BB = "BB"

class Stage(Enum):
    """
    游戏阶段枚举
    """
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"

class Action(Enum):
    """
    玩家可能的行动枚举
    """
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    RAISE = "RAISE"
    ALL_IN = "ALL_IN"

# 6人局位置权重（数值越大，玩牌范围越宽）
POSITION_WEIGHTS_6MAX: Dict[Position, float] = {
    Position.UTG: 1.0,  # 最紧
    Position.MP: 1.2,   
    Position.CO: 1.5,
    Position.BTN: 1.8,  # 最松
    Position.SB: 0.8,   # 盲注位置特殊处理
    Position.BB: 1.0
}

# 标准翻前加注尺度（以大盲为单位）
STANDARD_PREFLOP_RAISES = {
    "MIN": 2,        # 最小加注
    "STANDARD": 2.5, # 标准加注
    "LARGE": 3,      # 大加注
    "SQUEEZE": 4     # 挤压加注
}

# 标准翻后加注尺度（以底池为单位）
STANDARD_POSTFLOP_BETS = {
    "SMALL": 0.33,   # 小注
    "MEDIUM": 0.5,   # 中注
    "STANDARD": 0.75,# 标准注
    "LARGE": 1.0,    # 底池大小
    "OVERBET": 1.5   # 超底池
}