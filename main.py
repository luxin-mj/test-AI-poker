"""
Poker Advisor主程序
提供交互式的德州扑克策略建议
"""

from src.core.card import Card, Hand
from src.core.game_state import GameState
from src.engine.advisor import PokerAdvisor
from src.utils.constants import Position, Stage, Action
from typing import List, Optional

class PokerAdvisorApp:
    """
    扑克顾问应用程序
    """
    
    def __init__(self):
        self.advisor = PokerAdvisor()
        self.game_state: Optional[GameState] = None
    
    def _parse_cards(self, cards_str: str) -> List[Card]:
        """解析牌的字符串表示"""
        if not cards_str:
            return []
            
        cards = []
        # 每两个字符代表一张牌
        for i in range(0, len(cards_str), 2):
            card_str = cards_str[i:i+2]
            cards.append(Card.from_string(card_str))
        return cards
    
    def _get_valid_input(self, prompt: str, valid_values: List[str]) -> str:
        """获取有效输入"""
        while True:
            value = input(prompt).strip().upper()
            if value in valid_values:
                return value
            print(f"无效输入，请选择: {', '.join(valid_values)}")
    
    def _print_decision(self, decision):
        """打印决策建议"""
        print("\n=== 策略建议 ===")
        print(f"建议行动: {decision.action.value}")
        if decision.amount > 0:
            print(f"建议金额: {decision.amount}")
        print(f"建议确信度: {decision.confidence:.2f}")
        print("\n决策理由:")
        for reason in decision.reasoning:
            print(f"- {reason}")
        print("==============\n")
    
    def start_new_hand(self):
        """开始新的一手牌"""
        print("\n=== 开始新一手牌 ===")
        
        # 获取手牌
        while True:
            try:
                hand_str = input("输入你的手牌 (例如: AhKh 表示红心AK): ").strip()
                hand = Hand.from_string(hand_str)
                break
            except ValueError:
                print("无效的手牌格式，请重试")
        
        # 获取位置
        position_str = self._get_valid_input(
            "选择你的位置 (UTG/MP/CO/BTN/SB/BB): ",
            [pos.value for pos in Position]
        )
        position = Position(position_str)
        
        # 获取玩家筹码
        while True:
            try:
                stack = int(input("输入你的筹码数量: "))
                if stack > 0:
                    break
                print("筹码数量必须大于0")
            except ValueError:
                print("请输入有效的数字")
        
        # 创建游戏状态
        self.game_state = GameState(
            my_hand=hand,
            my_position=position,
            my_stack=stack
        )
        
        print("\n=== 初始状态已设置 ===")
    
    def update_street(self):
        """更新当前街道状态"""
        if not self.game_state:
            print("请先开始新的一手牌")
            return
            
        # 获取当前阶段
        current_stage = self.game_state.current_stage
        
        # 如果不是翻前，需要输入公共牌
        if current_stage != Stage.PREFLOP:
            while True:
                try:
                    board_str = input("输入公共牌 (例如: AhKhQh): ").strip()
                    board_cards = self._parse_cards(board_str)
                    if len(board_cards) == (3 if current_stage == Stage.FLOP else 4 if current_stage == Stage.TURN else 5):
                        self.game_state.add_community_cards(board_cards)
                        break
                    print(f"需要输入{'3张' if current_stage == Stage.FLOP else '4张' if current_stage == Stage.TURN else '5张'}牌")
                except ValueError:
                    print("无效的牌格式，请重试")
        
        # 获取需要跟注的金额
        while True:
            try:
                to_call = int(input("需要跟注的金额（0表示没有人下注）: "))
                if to_call >= 0:
                    self.game_state.to_call = to_call
                    break
                print("跟注金额不能为负数")
            except ValueError:
                print("请输入有效的数字")
        
        # 获取当前底池大小
        while True:
            try:
                pot_size = int(input("当前底池大小: "))
                if pot_size >= 0:
                    self.game_state.current_pot = pot_size
                    break
                print("底池大小不能为负数")
            except ValueError:
                print("请输入有效的数字")
    
    def get_advice(self):
        """获取策略建议"""
        if not self.game_state:
            print("请先开始新的一手牌")
            return
            
        decision = self.advisor.get_advice(self.game_state)
        self._print_decision(decision)
    
    def advance_stage(self):
        """推进到下一个阶段"""
        if not self.game_state:
            print("请先开始新的一手牌")
            return
            
        self.game_state.advance_stage()
        print(f"进入{self.game_state.current_stage.value}阶段")
    
    def run(self):
        """运行主程序"""
        print("欢迎使用Poker Advisor!")
        
        while True:
            print("\n可用命令:")
            print("1. new - 开始新的一手牌")
            print("2. update - 更新当前状态")
            print("3. advice - 获取策略建议")
            print("4. next - 进入下一阶段")
            print("5. quit - 退出程序")
            
            command = input("\n请输入命令: ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'new':
                self.start_new_hand()
            elif command == 'update':
                self.update_street()
            elif command == 'advice':
                self.get_advice()
            elif command == 'next':
                self.advance_stage()
            else:
                print("无效的命令")
        
        print("感谢使用Poker Advisor!")

if __name__ == "__main__":
    app = PokerAdvisorApp()
    app.run()