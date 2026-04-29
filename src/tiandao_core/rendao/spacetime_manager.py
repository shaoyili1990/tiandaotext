"""
Spacetime Manager - 时空绝对位置管控系统

核心原则：
1. 同一角色在同一时间点只能处于唯一位置
2. 时间线不可逆，过去发生的事不可更改
3. 除非明确声明的超自然能力，否则角色不能同时出现在两处
4. 位置记录包含：时间戳、场景/章节、空间坐标

这确保了故事的"绝对质感"——真实的基础约束
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import math


class MovementType(Enum):
    """移动类型"""
    NATURAL = "natural"           # 自然移动（步行、乘车等日常移动）
    TELEPORT = "teleport"        # 瞬间移动（超自然能力）
    SUMMONED = "summoned"         # 被召唤（外力作用）
    PROJECTION = "projection"     # 投影/分身
    TIME_SKIP = "time_skip"       # 时间跳跃
    UNKNOWN = "unknown"           # 未知


@dataclass
class SpacetimeCoordinate:
    """时空坐标"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    chapter: str = ""           # 章节标识
    scene: str = ""             # 场景描述
    timestamp: str = ""        # 时间戳（ISO格式或剧情时间）
    is_supernatural: bool = False  # 是否涉及超自然能力


@dataclass
class CharacterPresence:
    """角色在某时某地的存在记录"""
    character_name: str
    coordinate: SpacetimeCoordinate
    movement_type: MovementType = MovementType.NATURAL
    note: str = ""  # 备注（如"分身术"、"瞬间移动"等特殊说明）


@dataclass
class SpacetimeViolation:
    """时空违规记录"""
    character_name: str
    time_a: str
    time_b: str
    location_a: str
    location_b: str
    severity: str  # "impossible" / "supernatural_explained" / "minor"
    explanation: str = ""


class SpacetimeManager:
    """
    时空绝对位置管控系统

    确保每个角色在任意时间点有且仅有一个物理位置
    除非该角色明确拥有超自然能力（如分身、瞬移等）

    核心功能：
    1. 记录角色位置历史（时间线）
    2. 验证新位置是否与已有记录冲突
    3. 检测时空矛盾
    4. 支持超自然能力声明
    5. 与蝴蝶效应系统的Position3D集成
    """

    def __init__(self):
        # 角色位置历史：character_name -> [Presence记录，按时间排序]
        self.presence_history: Dict[str, List[CharacterPresence]] = {}

        # 角色超自然能力声明：character_name -> [能力列表]
        self.supernatural_abilities: Dict[str, List[str]] = {}

        # 时空违规记录
        self.violations: List[SpacetimeViolation] = []

    def register_supernatural_ability(
        self,
        character_name: str,
        ability: str,
        description: str = ""
    ):
        """
        注册角色的超自然能力

        例如：
        - "瞬移" - 可以瞬间移动到任意位置
        - "分身术" - 可以同时出现在多处
        - "时间倒流" - 可以回到过去
        """
        if character_name not in self.supernatural_abilities:
            self.supernatural_abilities[character_name] = []

        self.supernatural_abilities[character_name].append(ability)

    def has_supernatural_ability(self, character_name: str, ability: str = "") -> bool:
        """检查角色是否拥有特定超自然能力"""
        if character_name not in self.supernatural_abilities:
            return False

        if not ability:
            # 没有指定能力名，只要有任一超自然能力即可
            return len(self.supernatural_abilities[character_name]) > 0

        return ability in self.supernatural_abilities[character_name]

    def record_presence(
        self,
        character_name: str,
        coordinate: SpacetimeCoordinate,
        movement_type: MovementType = MovementType.NATURAL,
        note: str = ""
    ):
        """
        记录角色的存在位置

        如果是新位置，会自动检查与历史记录的时间冲突
        """
        presence = CharacterPresence(
            character_name=character_name,
            coordinate=coordinate,
            movement_type=movement_type,
            note=note
        )

        if character_name not in self.presence_history:
            self.presence_history[character_name] = []

        self.presence_history[character_name].append(presence)

        # 检查是否有时空矛盾
        self._check_violation(presence)

    def _check_violation(self, new_presence: CharacterPresence):
        """
        检查新位置是否与历史记录矛盾
        """
        if new_presence.movement_type in [
            MovementType.TELEPORT,
            MovementType.SUMMONED,
            MovementType.PROJECTION
        ]:
            # 瞬间移动类型，跳过同时间检查
            return

        if new_presence.character_name not in self.presence_history:
            return

        # 检查是否在相近时间出现在不同位置
        history = self.presence_history[new_presence.character_name]

        for past in history:
            if past.character_name != new_presence.character_name:
                continue

            # 如果时间相同但位置不同
            if self._is_same_time(past.coordinate.timestamp, new_presence.coordinate.timestamp):
                if not self._is_same_location(past.coordinate, new_presence.coordinate):
                    # 不是超自然能力，但位置不同 -> 违规
                    violation = SpacetimeViolation(
                        character_name=new_presence.character_name,
                        time_a=past.coordinate.timestamp,
                        time_b=new_presence.coordinate.timestamp,
                        location_a=f"{past.coordinate.scene} ({past.coordinate.x},{past.coordinate.y},{past.coordinate.z})",
                        location_b=f"{new_presence.coordinate.scene} ({new_presence.coordinate.x},{new_presence.coordinate.y},{new_presence.coordinate.z})",
                        severity="impossible",
                        explanation="同一时间点出现不同位置，且无超自然能力解释"
                    )
                    self.violations.append(violation)

    def _is_same_time(self, time_a: str, time_b: str) -> bool:
        """判断两个时间是否相同/相近"""
        if time_a == time_b:
            return True

        # 可以扩展更复杂的时间比较逻辑
        # 目前简化为字符串相等
        return False

    def _is_same_location(self, coord_a: SpacetimeCoordinate, coord_b: SpacetimeCoordinate) -> bool:
        """判断两个位置是否相同（允许小范围误差）"""
        distance = math.sqrt(
            (coord_a.x - coord_b.x) ** 2 +
            (coord_a.y - coord_b.y) ** 2 +
            (coord_a.z - coord_b.z) ** 2
        )
        # 距离小于1视为同一位置
        return distance < 1.0

    def get_presence_at(
        self,
        character_name: str,
        chapter: str
    ) -> Optional[CharacterPresence]:
        """获取角色在特定章节的位置"""
        if character_name not in self.presence_history:
            return None

        for presence in reversed(self.presence_history[character_name]):
            if presence.coordinate.chapter == chapter:
                return presence

        return None

    def get_location_at_time(
        self,
        character_name: str,
        timestamp: str
    ) -> Optional[SpacetimeCoordinate]:
        """获取角色在特定时间点的位置"""
        if character_name not in self.presence_history:
            return None

        for presence in reversed(self.presence_history[character_name]):
            if presence.coordinate.timestamp == timestamp:
                return presence.coordinate

        return None

    def get_timeline(self, character_name: str) -> List[CharacterPresence]:
        """获取角色的完整时间线"""
        return self.presence_history.get(character_name, [])

    def verify_no_temporal_conflict(
        self,
        character_name: str,
        new_chapter: str,
        new_timestamp: str
    ) -> Tuple[bool, Optional[str]]:
        """
        验证新位置是否与时间线冲突

        返回：(是否合法, 冲突描述)
        """
        if character_name not in self.presence_history:
            return True, None

        # 检查同一时间是否有多个位置记录
        for presence in self.presence_history[character_name]:
            if presence.coordinate.timestamp == new_timestamp:
                if presence.coordinate.chapter != new_chapter:
                    # 同一时间不同章节/场景
                    if self.has_supernatural_ability(character_name, "瞬移"):
                        return True, None
                    return False, f"时间冲突: {new_timestamp} 已在 {presence.coordinate.chapter} 出现"

        return True, None

    def get_violations(self) -> List[SpacetimeViolation]:
        """获取所有时空违规记录"""
        return self.violations

    def get_spacetime_summary(self) -> Dict:
        """获取时空系统摘要"""
        return {
            "total_characters": len(self.presence_history),
            "total_presence_records": sum(len(v) for v in self.presence_history.values()),
            "violations_count": len(self.violations),
            "supernatural_characters": len(self.supernatural_abilities)
        }


def create_spacetime_manager() -> SpacetimeManager:
    """工厂函数：创建时空管理器"""
    return SpacetimeManager()