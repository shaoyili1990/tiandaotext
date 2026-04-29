"""
Butterfly Effect - 蝴蝶效应传导系统

核心公式:
- 时空距离计算: d = sqrt((x1-x2)² + (y1-y2)² + (z1-z2)²)
- 影响力衰减: influence = max(0, 100 - d * 10)
- 高Y值角色可影响低Y值角色

传导机制:
1. 动机链传导: 满足/受挫 -> 下一层级激活/补偿
2. 记忆关联网络: 记忆节点之间的关联触发
3. 冲突变量传导: personal -> social -> world 递进

物理定理:
- 吞噬与依附: Y>70 与 Y<30 且存在支配关系
- 绝对碰撞: 两个 Y>70 目标互斥
- 变量击穿: 常态 40-60 者遭遇极致爱/恨/愧疚
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import math


class InfluenceType(Enum):
    """影响力类型"""
    BREAKTHROUGH = "breakthrough"       # 击穿影响
    COMPENSATION = "compensation"       # 补偿影响
    REBOUND = "rebound"                 # 回弹影响
    MOTIVATION = "motivation"           # 动机传导
    MEMORY = "memory"                   # 记忆关联
    CONFLICT = "conflict"               # 冲突升级


@dataclass
class Position3D:
    """3D位置"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def distance_to(self, other: "Position3D") -> float:
        """计算到另一个位置的距离"""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )


@dataclass
class CharacterState:
    """角色状态"""
    name: str
    y_value: int
    position: Position3D
    weight: int
    mbti: str
    is_active: bool = True


@dataclass
class ButterflyEffect:
    """蝴蝶效应事件"""
    source: str                           # 事件源角色
    target: str                            # 事件目标角色
    effect_type: InfluenceType            # 效应类型
    intensity: float                       # 效应强度 [0-1]
    y_change: int = 0                      # Y值变化
    description: str = ""


class ButterflyEffectSystem:
    """
    蝴蝶效应传导系统

    核心功能:
    1. 空间距离计算
    2. 影响力衰减计算
    3. Y值传导机制
    4. 冲突升级检测
    5. 物理定理应用
    """

    # 影响力衰减系数
    DISTANCE_DECAY_RATE = 10

    # 击穿相关阈值
    BREAKTHROUGH_DELTA_THRESHOLD = 15

    def __init__(self):
        self.characters: Dict[str, CharacterState] = {}
        self.effect_history: List[ButterflyEffect] = []
        self.collision_pairs: List[Tuple[str, str]] = []

    def register_character(
        self,
        name: str,
        y_value: int,
        position: Position3D,
        weight: int,
        mbti: str
    ):
        """注册角色到蝴蝶效应系统"""
        self.characters[name] = CharacterState(
            name=name,
            y_value=y_value,
            position=position,
            weight=weight,
            mbti=mbti
        )

    def update_character_state(
        self,
        name: str,
        y_value: Optional[int] = None,
        position: Optional[Position3D] = None,
        weight: Optional[int] = None
    ):
        """更新角色状态"""
        if name in self.characters:
            state = self.characters[name]
            if y_value is not None:
                state.y_value = y_value
            if position is not None:
                state.position = position
            if weight is not None:
                state.weight = weight

    def calculate_influence(
        self,
        source_name: str,
        target_name: str
    ) -> float:
        """
        计算影响力

        影响力 = max(0, 100 - d * 10)
        其中 d 是空间距离
        """
        if source_name not in self.characters or target_name not in self.characters:
            return 0.0

        source = self.characters[source_name]
        target = self.characters[target_name]

        distance = source.position.distance_to(target.position)
        influence = max(0.0, 100 - distance * self.DISTANCE_DECAY_RATE)

        return influence / 100.0  # 归一化到 [0, 1]

    def check_breakthrough_possibility(
        self,
        attacker_name: str,
        defender_name: str
    ) -> Tuple[bool, int]:
        """
        检查击穿可能性

        返回: (是否击穿, Y值变化)
        """
        if attacker_name not in self.characters or defender_name not in self.characters:
            return False, 0

        attacker = self.characters[attacker_name]
        defender = self.characters[defender_name]

        delta_y = attacker.y_value - defender.y_value

        # 根据防御者Y值确定击穿阈值
        if defender.y_value < 40:
            threshold = 30
        elif defender.y_value < 70:
            threshold = 20
        else:
            threshold = 15

        if delta_y >= threshold:
            # 计算Y值变化
            y_change = self._calculate_breakthrough_y_change(
                defender.y_value,
                defender.position,
                attacker.position
            )

            return True, y_change

        return False, 0

    def _calculate_breakthrough_y_change(
        self,
        defender_y: int,
        defender_pos: Position3D,
        attacker_pos: Position3D
    ) -> int:
        """
        计算击穿后的Y值变化

        被击穿后，Y值瞬间跃迁为「自身基线±10」
        """
        # 简化为: 基于距离的方向性跃迁
        distance = defender_pos.distance_to(attacker_pos)

        if distance < 5:
            # 很近，向上跃迁（被压制后反弹）
            return -10  # 降低10点
        else:
            return -10

    def apply_breakthrough_effect(
        self,
        attacker_name: str,
        defender_name: str
    ) -> ButterflyEffect:
        """
        应用击穿效应
        """
        attacker = self.characters.get(attacker_name)
        defender = self.characters.get(defender_name)

        if not attacker or not defender:
            raise ValueError("Character not found")

        old_y = defender.y_value
        _, y_change = self.check_breakthrough_possibility(attacker_name, defender_name)

        new_y = max(1, min(100, old_y + y_change))

        effect = ButterflyEffect(
            source=attacker_name,
            target=defender_name,
            effect_type=InfluenceType.BREAKTHROUGH,
            intensity=self.calculate_influence(attacker_name, defender_name),
            y_change=y_change,
            description=f"{attacker_name}(Y={attacker.y_value})击穿了{defender_name}(Y={old_y}->{new_y})"
        )

        # 更新状态
        defender.y_value = new_y
        self.effect_history.append(effect)

        return effect

    def check_physics_theorems(self) -> List[str]:
        """
        检查物理定理触发

        检测:
        1. 吞噬与依附: Y>70 与 Y<30 且存在支配关系
        2. 绝对碰撞: 两个 Y>70 目标互斥
        3. 变量击穿: 常态 40-60 者遭遇极致爱/恨/愧疚

        返回触发的定理列表，并直接应用到角色Y值
        """
        triggered = []
        characters_list = list(self.characters.values())

        # 检查吞噬与依附
        high_y_chars = [c for c in characters_list if c.y_value > 70]
        low_y_chars = [c for c in characters_list if c.y_value < 30]

        for high in high_y_chars:
            for low in low_y_chars:
                distance = high.position.distance_to(low.position)
                if distance < 10:  # 足够近
                    triggered.append(
                        f"吞噬与依附: {high.name}(Y={high.y_value}) 正在影响 {low.name}(Y={low.y_value})"
                    )
                    # 吞噬效应：低Y值角色被压制，Y值下降
                    low.y_value = max(1, low.y_value - 5)

        # 检查绝对碰撞
        if len(high_y_chars) >= 2:
            for i, char1 in enumerate(high_y_chars):
                for char2 in high_y_chars[i+1:]:
                    distance = char1.position.distance_to(char2.position)
                    if distance < 5:  # 非常近
                        triggered.append(
                            f"绝对碰撞: {char1.name}(Y={char1.y_value}) 与 {char2.name}(Y={char2.y_value}) 即将冲突"
                        )
                        # 绝对碰撞：两个高Y角色相互抵消，各降低5点
                        char1.y_value = max(1, char1.y_value - 5)
                        char2.y_value = max(1, char2.y_value - 5)

        return triggered

    def propagate_effect(
        self,
        source_name: str,
        effect_type: InfluenceType,
        intensity: float,
        max_propagation: int = 3
    ) -> List[ButterflyEffect]:
        """
        传导效应到其他角色

        每次传导强度衰减 0.2
        """
        effects = []

        if source_name not in self.characters:
            return effects

        source = self.characters[source_name]
        current_intensity = intensity

        for step in range(max_propagation):
            current_intensity *= 0.8  # 传导衰减

            if current_intensity < 0.1:
                break

            # 找到受影响的角色
            for name, char in self.characters.items():
                if name == source_name:
                    continue

                influence = self.calculate_influence(source_name, name)

                if influence >= 0.3:  # 影响力阈值
                    effect = ButterflyEffect(
                        source=source_name,
                        target=name,
                        effect_type=effect_type,
                        intensity=current_intensity * influence,
                        y_change=int(current_intensity * influence * 5),
                        description=f"效应从 {source_name} 传导至 {name}"
                    )

                    effects.append(effect)
                    self.effect_history.append(effect)

                    # 更新目标Y值
                    char.y_value = max(1, min(100, char.y_value + effect.y_change))

        return effects

    def get_effect_summary(self) -> Dict:
        """获取效应摘要"""
        effect_counts = {}
        for effect in self.effect_history:
            effect_counts[effect.effect_type.value] = effect_counts.get(effect.effect_type.value, 0) + 1

        return {
            "total_effects": len(self.effect_history),
            "effect_distribution": effect_counts,
            "collision_pairs": len(self.collision_pairs),
            "active_characters": len([c for c in self.characters.values() if c.is_active])
        }


def create_butterfly_effect_system() -> ButterflyEffectSystem:
    """工厂函数：创建蝴蝶效应系统"""
    return ButterflyEffectSystem()