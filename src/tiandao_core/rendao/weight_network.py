"""
Weight Network - 权重关系网

人物分类与初始权重:
- 主角团: 85-95
- 反派团: 80-90
- 主要人物: 60-80
- 次要人物: 40-60
- NPC: 0-30

权重升降规则:
- 有价值行为: +1~3点
- 关键行为: +3~5点
- 无价值行为（不符合风格/背景/老天爷价值）: -5~8点
- 负面行为: -5~10点
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class CharacterClass(Enum):
    """人物分类"""
    PROTAGONIST = "protagonist"       # 主角团
    ANTAGONIST = "antagonist"         # 反派团
    MAIN = "main"                     # 主要人物
    SECONDARY = "secondary"           # 次要人物
    NPC = "npc"                       # NPC


@dataclass
class WeightChange:
    """权重变化"""
    character_name: str
    old_weight: int
    new_weight: int
    delta: int
    reason: str


class WeightNetwork:
    """
    权重关系网 - 人道系统核心

    核心功能:
    1. 人物权重初始化
    2. 权重动态调整
    3. 权重等级晋升/降级
    4. 权重传导机制
    """

    # 人物分类初始权重范围
    CLASS_WEIGHT_RANGES: Dict[CharacterClass, Tuple[int, int]] = {
        CharacterClass.PROTAGONIST: (85, 95),
        CharacterClass.ANTAGONIST: (80, 90),
        CharacterClass.MAIN: (60, 80),
        CharacterClass.SECONDARY: (40, 60),
        CharacterClass.NPC: (0, 30),
    }

    # 权重阈值
    PROMOTION_THRESHOLD = 90  # 晋升阈值
    DEMOTION_THRESHOLD = 20   # 降级阈值

    def __init__(self):
        self.character_weights: Dict[str, int] = {}
        self.character_classes: Dict[str, CharacterClass] = {}
        self.weight_history: Dict[str, List[WeightChange]] = {}

    def register_character(
        self,
        name: str,
        character_class: CharacterClass,
        custom_weight: Optional[int] = None
    ) -> int:
        """
        注册角色到权重网络

        返回分配的初始权重
        """
        if custom_weight is not None:
            weight = custom_weight
        else:
            min_w, max_w = self.CLASS_WEIGHT_RANGES[character_class]
            weight = (min_w + max_w) // 2

        self.character_weights[name] = weight
        self.character_classes[name] = character_class
        self.weight_history[name] = []

        return weight

    def get_weight(self, name: str) -> Optional[int]:
        """获取角色权重"""
        return self.character_weights.get(name)

    def get_class(self, name: str) -> Optional[CharacterClass]:
        """获取角色分类"""
        return self.character_classes.get(name)

    def calculate_delta(
        self,
        actor_name: str,
        action_type: str,
        action_value: float = 0.5
    ) -> int:
        """
        计算权重变化值

        参数:
        - actor_name: 行动者名称
        - action_type: 行动类型
        - action_value: 行动价值 [0-1]
        """
        base_weight = self.character_weights.get(actor_name, 50)

        # 根据行动类型计算权重变化
        if action_type == "valuable":
            # 有价值行为: +1~3点
            delta = int(1 + action_value * 2)
        elif action_type == "key":
            # 关键行为: +3~5点
            delta = int(3 + action_value * 2)
        elif action_type == "worthless":
            # 无价值行为: -5~8点
            delta = -int(5 + action_value * 3)
        elif action_type == "negative":
            # 负面行为: -5~10点
            delta = -int(5 + action_value * 5)
        elif action_type == "trauma":
            # 创伤行为: -8~15点
            delta = -int(8 + action_value * 7)
        elif action_type == "redemption":
            # 救赎行为: +5~10点
            delta = int(5 + action_value * 5)
        elif action_type == "breakthrough":
            # 击穿行为: 根据被击穿者Y值计算
            delta = -10
        else:
            delta = 0

        return delta

    def apply_weight_change(
        self,
        character_name: str,
        delta: int,
        reason: str
    ) -> WeightChange:
        """
        应用权重变化

        返回权重变化记录
        """
        old_weight = self.character_weights.get(character_name, 50)
        new_weight = max(0, min(100, old_weight + delta))

        self.character_weights[character_name] = new_weight

        change = WeightChange(
            character_name=character_name,
            old_weight=old_weight,
            new_weight=new_weight,
            delta=delta,
            reason=reason
        )

        if character_name not in self.weight_history:
            self.weight_history[character_name] = []
        self.weight_history[character_name].append(change)

        return change

    def check_class_change(self, character_name: str) -> Optional[str]:
        """
        检查并执行分类变化

        返回变化描述，如果没有变化返回None
        """
        current_weight = self.character_weights.get(character_name)
        if current_weight is None:
            return None

        current_class = self.character_classes.get(character_name)
        if current_class is None:
            return None

        # 检查晋升
        if current_weight >= self.PROMOTION_THRESHOLD:
            if current_class == CharacterClass.SECONDARY:
                self.character_classes[character_name] = CharacterClass.MAIN
                return f"{character_name} 从次要人物晋升为主要人物"
            elif current_class == CharacterClass.MAIN:
                self.character_classes[character_name] = CharacterClass.PROTAGONIST
                return f"{character_name} 从主要人物晋升为主角团"

        # 检查降级
        if current_weight <= self.DEMOTION_THRESHOLD:
            if current_class == CharacterClass.PROTAGONIST:
                self.character_classes[character_name] = CharacterClass.MAIN
                return f"{character_name} 从主角团降级为主要人物"
            elif current_class == CharacterClass.MAIN:
                self.character_classes[character_name] = CharacterClass.SECONDARY
                return f"{character_name} 从主要人物降级为次要人物"
            elif current_class == CharacterClass.SECONDARY:
                self.character_classes[character_name] = CharacterClass.NPC
                return f"{character_name} 从次要人物降级为NPC"

        return None

    def get_weight_rankings(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        获取权重排行榜

        返回前N名角色及其权重
        """
        sorted_chars = sorted(
            self.character_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_chars[:limit]

    def get_influence_level(
        self,
        source_name: str,
        target_name: str
    ) -> str:
        """
        获取影响力等级

        基于权重差值计算影响力
        """
        source_weight = self.character_weights.get(source_name, 50)
        target_weight = self.character_weights.get(target_name, 50)

        delta = source_weight - target_weight

        if delta >= 30:
            return "压倒性"
        elif delta >= 20:
            return "强"
        elif delta >= 10:
            return "中等"
        elif delta >= 5:
            return "微弱"
        else:
            return "无影响"

    def get_network_summary(self) -> Dict:
        """获取网络摘要"""
        class_counts = {}
        for char_class in CharacterClass:
            class_counts[char_class.value] = sum(
                1 for c in self.character_classes.values() if c == char_class
            )

        return {
            "total_characters": len(self.character_weights),
            "class_distribution": class_counts,
            "average_weight": sum(self.character_weights.values()) / len(self.character_weights) if self.character_weights else 0,
            "top_characters": self.get_weight_rankings(5)
        }


def create_weight_network() -> WeightNetwork:
    """工厂函数：创建权重网络"""
    return WeightNetwork()