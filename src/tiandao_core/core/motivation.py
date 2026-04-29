"""
Motivation System - 动机链系统

七本能 (7 Basic Instincts):
1. 生存本能 (Survival)
2. 群体本能 (Belonging)
3. 权力本能 (Power)
4. 意义本能 (Meaning)
5. 愉悦本能 (Pleasure)
6. 安全本能 (Safety)
7. 成长本能 (Growth)

四层级 (4 Layers):
1. 表层动机: 即时需求、当前目标
2. 心理动机: 深层需求、价值取向
3. 本能动机: 先天驱动、无意识需求
4. 核心动机: 人生使命、终极价值

公式:
- 动机强度 = 基础强度 × 环境激活 × 角色特质
- 动机冲突 = Σ(动机优先级 × 动机强度差异)
- 动机链传导 = 满足/受挫 → 下一层级激活/补偿
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import math


class InstinctType(Enum):
    """七本能类型"""
    SURVIVAL = "survival"           # 生存本能
    BELONGING = "belonging"         # 群体本能
    POWER = "power"                 # 权力本能
    MEANING = "meaning"             # 意义本能
    PLEASURE = "pleasure"           # 愉悦本能
    SAFETY = "safety"               # 安全本能
    GROWTH = "growth"               # 成长本能


class MotivationLayer(Enum):
    """动机层级"""
    SURFACE = "surface"             # 表层动机
    PSYCHOLOGICAL = "psychological"  # 心理动机
    INSTINCTUAL = "instinctual"     # 本能动机
    CORE = "core"                   # 核心动机


@dataclass
class InstinctConfig:
    """本能配置"""
    instinct_type: InstinctType
    base_intensity: float            # 基础强度 [0-1]
    threshold: float = 0.3           # 激活阈值
    priority: int = 5                # 优先级 [1-10]
    description: str = ""


@dataclass
class Motivation:
    """动机"""
    id: str
    instinct_type: InstinctType
    layer: MotivationLayer
    description: str
    intensity: float                 # 当前强度 [0-1]
    base_intensity: float            # 基础强度
    is_active: bool = False
    is_conflicting: bool = False
    conflicting_with: List[str] = field(default_factory=list)
    history: List[Dict] = field(default_factory=list)

    @property
    def activation_level(self) -> float:
        """激活水平 = 强度 × 优先级"""
        return self.intensity * (self.base_intensity / 5.0)


@dataclass
class MotivationChain:
    """动机链"""
    trigger: Motivation              # 触发动机
    propagation_chain: List[str] = field(default_factory=list)  # 传导路径
    intensity_decay: float = 0.2      # 每层强度衰减
    max_propagation: int = 3         # 最大传导层级


@dataclass
class MotivationConflict:
    """动机冲突"""
    motivation_1: str
    motivation_2: str
    conflict_type: str               # "competing", "complementary", "neutral"
    resolution_tendency: str         # "first", "balance", "sacrifice", "integration"


class MotivationSystem:
    """
    动机系统 - 七本能四层级核心

    核心功能:
    1. 七本能的建模与激活
    2. 四层动机的动态管理
    3. 动机链的传导机制
    4. 动机冲突的检测与解决
    5. 动机驱动的行为预测
    """

    # 七本能默认配置
    DEFAULT_INSTINCTS: Dict[InstinctType, InstinctConfig] = {
        InstinctType.SURVIVAL: InstinctConfig(
            instinct_type=InstinctType.SURVIVAL,
            base_intensity=0.9,
            threshold=0.2,
            priority=10,
            description="追求生存、避免死亡"
        ),
        InstinctType.BELONGING: InstinctConfig(
            instinct_type=InstinctType.BELONGING,
            base_intensity=0.7,
            threshold=0.3,
            priority=8,
            description="追求归属、避免排斥"
        ),
        InstinctType.POWER: InstinctConfig(
            instinct_type=InstinctType.POWER,
            base_intensity=0.6,
            threshold=0.4,
            priority=6,
            description="追求控制、避免无力"
        ),
        InstinctType.MEANING: InstinctConfig(
            instinct_type=InstinctType.MEANING,
            base_intensity=0.5,
            threshold=0.5,
            priority=4,
            description="追求意义、避免虚无"
        ),
        InstinctType.PLEASURE: InstinctConfig(
            instinct_type=InstinctType.PLEASURE,
            base_intensity=0.6,
            threshold=0.4,
            priority=5,
            description="追求愉悦、避免痛苦"
        ),
        InstinctType.SAFETY: InstinctConfig(
            instinct_type=InstinctType.SAFETY,
            base_intensity=0.7,
            threshold=0.3,
            priority=7,
            description="追求安全、避免危险"
        ),
        InstinctType.GROWTH: InstinctConfig(
            instinct_type=InstinctType.GROWTH,
            base_intensity=0.5,
            threshold=0.4,
            priority=5,
            description="追求成长、避免停滞"
        ),
    }

    # 层级到本能的映射关系
    LAYER_INSTINCT_MAP: Dict[MotivationLayer, List[InstinctType]] = {
        MotivationLayer.SURFACE: [InstinctType.SURVIVAL, InstinctType.PLEASURE],
        MotivationLayer.PSYCHOLOGICAL: [InstinctType.BELONGING, InstinctType.SAFETY],
        MotivationLayer.INSTINCTUAL: [InstinctType.POWER, InstinctType.MEANING],
        MotivationLayer.CORE: [InstinctType.GROWTH],
    }

    def __init__(self, character_id: Optional[str] = None):
        self.character_id = character_id
        self.instincts: Dict[InstinctType, InstinctConfig] = {}
        self.motivations: Dict[str, Motivation] = {}
        self.active_motivation_ids: Set[str] = set()
        self.motivation_chains: List[MotivationChain] = []

        # 初始化本能配置
        for instinct_type, config in self.DEFAULT_INSTINCTS.items():
            self.instincts[instinct_type] = config

        # 初始化四层动机
        self._init_motivations()

    def _init_motivations(self):
        """初始化四层动机"""
        layer_names = {
            MotivationLayer.SURFACE: "表层动机",
            MotivationLayer.PSYCHOLOGICAL: "心理动机",
            MotivationLayer.INSTINCTUAL: "本能动机",
            MotivationLayer.CORE: "核心动机"
        }

        # 为每个本能找到对应的层级
        instinct_to_layer = {}
        for layer, instincts in self.LAYER_INSTINCT_MAP.items():
            for instinct in instincts:
                instinct_to_layer[instinct] = layer

        # 根据层级创建动机
        for instinct, config in self.DEFAULT_INSTINCTS.items():
            layer = instinct_to_layer.get(instinct, MotivationLayer.INSTINCTUAL)
            motivation_id = f"{layer.value}_{instinct.value}"

            motivation = Motivation(
                id=motivation_id,
                instinct_type=instinct,
                layer=layer,
                description=layer_names[layer],
                intensity=config.base_intensity,
                base_intensity=config.base_intensity,
                is_active=False
            )
            self.motivations[motivation_id] = motivation

    def activate_instinct(
        self,
        instinct_type: InstinctType,
        intensity_modifier: float = 1.0,
        context: Optional[str] = None
    ) -> Motivation:
        """
        激活特定本能

        参数:
        - instinct_type: 本能类型
        - intensity_modifier: 强度修正 [0-2]
        - context: 激活上下文
        """
        config = self.instincts.get(instinct_type)
        if not config:
            raise ValueError(f"Unknown instinct type: {instinct_type}")

        # 计算新强度
        new_intensity = min(1.0, config.base_intensity * intensity_modifier)

        # 更新相关动机
        for motivation in self.motivations.values():
            if motivation.instinct_type == instinct_type:
                motivation.intensity = new_intensity
                motivation.is_active = new_intensity >= config.threshold
                motivation.history.append({
                    "event": "activated",
                    "intensity": new_intensity,
                    "modifier": intensity_modifier,
                    "context": context
                })

        # 触发动机链传导
        if new_intensity >= config.threshold:
            self._propagate_motivation(instinct_type, new_intensity)

        # 返回正确层级的动机
        for motivation in self.motivations.values():
            if motivation.instinct_type == instinct_type:
                return motivation
        raise ValueError(f"No motivation found for instinct {instinct_type}")

    def _propagate_motivation(self, instinct: InstinctType, intensity: float):
        """
        动机链传导
        满足/受挫 → 下一层级激活/补偿
        """
        # 找到本能对应的实际层级
        trigger_key = None
        for layer, instincts in self.LAYER_INSTINCT_MAP.items():
            if instinct in instincts:
                trigger_key = f"{layer.value}_{instinct.value}"
                break
        if not trigger_key:
            trigger_key = f"{MotivationLayer.INSTINCTUAL.value}_{instinct.value}"

        chain = MotivationChain(
            trigger=self.motivations.get(trigger_key),
            propagation_chain=[],
            intensity_decay=0.2,
            max_propagation=3
        )
        current_intensity = intensity
        current_layer = MotivationLayer.INSTINCTUAL

        for _ in range(chain.max_propagation):
            # 计算下层强度
            next_intensity = current_intensity * (1 - chain.intensity_decay)

            if next_intensity < 0.2:
                break

            # 查找下层相关本能
            layers = list(MotivationLayer)
            next_layer_idx = layers.index(current_layer) + 1

            if next_layer_idx >= len(layers):
                break

            next_layer = layers[next_layer_idx]
            related_instincts = self.LAYER_INSTINCT_MAP.get(next_layer, [])

            for related in related_instincts:
                motivation_id = f"{next_layer.value}_{related.value}"
                if motivation_id in self.motivations:
                    motivation = self.motivations[motivation_id]
                    motivation.intensity = max(motivation.intensity, next_intensity)
                    motivation.is_active = True
                    chain.propagation_chain.append(motivation_id)

            current_intensity = next_intensity
            current_layer = next_layer

        self.motivation_chains.append(chain)

    def check_conflicts(self) -> List[MotivationConflict]:
        """
        检测动机冲突

        动机冲突类型:
        - competing: 竞争关系
        - complementary: 互补关系
        - neutral: 中性关系
        """
        conflicts = []
        active_motivations = [m for m in self.motivations.values() if m.is_active]

        for i, m1 in enumerate(active_motivations):
            for m2 in active_motivations[i+1:]:
                conflict = self._analyze_conflict(m1, m2)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    def _analyze_conflict(self, m1: Motivation, m2: Motivation) -> Optional[MotivationConflict]:
        """分析两个动机的冲突关系"""
        # 定义冲突矩阵
        conflicting_pairs = {
            (InstinctType.PLEASURE, InstinctType.GROWTH): "competing",
            (InstinctType.SAFETY, InstinctType.GROWTH): "competing",
            (InstinctType.BELONGING, InstinctType.POWER): "competing",
            (InstinctType.SURVIVAL, InstinctType.MEANING): "neutral",
            (InstinctType.BELONGING, InstinctType.MEANING): "complementary",
            (InstinctType.POWER, InstinctType.GROWTH): "complementary",
        }

        pair = (m1.instinct_type, m2.instinct_type)
        reverse_pair = (m2.instinct_type, m1.instinct_type)

        conflict_type = conflicting_pairs.get(pair) or conflicting_pairs.get(reverse_pair)

        if conflict_type:
            # 确定解决倾向
            if m1.layer.value < m2.layer.value:
                resolution = "first"
            elif m1.layer == m2.layer:
                resolution = "balance"
            else:
                resolution = "sacrifice"

            return MotivationConflict(
                motivation_1=m1.id,
                motivation_2=m2.id,
                conflict_type=conflict_type,
                resolution_tendency=resolution
            )

        return None

    def resolve_conflict(self, conflict: MotivationConflict) -> str:
        """
        解决动机冲突

        返回被抑制的动机ID
        """
        m1 = self.motivations.get(conflict.motivation_1)
        m2 = self.motivations.get(conflict.motivation_2)

        if not m1 or not m2:
            return ""

        # 根据解决倾向决定
        if conflict.resolution_tendency == "sacrifice":
            # 低层级动机被牺牲
            if m1.layer.value < m2.layer.value:
                m1.intensity *= 0.5
                return m1.id
            else:
                m2.intensity *= 0.5
                return m2.id

        elif conflict.resolution_tendency == "balance":
            # 平衡处理
            avg = (m1.intensity + m2.intensity) / 2
            m1.intensity = avg
            m2.intensity = avg
            return ""

        else:  # "first" or default
            # 先激活的优先
            return ""

    def get_dominant_motivation(self) -> Optional[Motivation]:
        """获取主导动机"""
        active = [m for m in self.motivations.values() if m.is_active]
        if not active:
            return None

        return max(active, key=lambda m: m.activation_level)

    def get_motivation_profile(self) -> Dict:
        """获取动机配置档案"""
        profile = {
            "active_count": sum(1 for m in self.motivations.values() if m.is_active),
            "total_count": len(self.motivations),
            "layers": {},
            "instincts": {},
            "conflicts": [],
            "dominant": None
        }

        for layer in MotivationLayer:
            layer_motives = [m for m in self.motivations.values() if m.layer == layer]
            profile["layers"][layer.value] = {
                "count": len(layer_motives),
                "active": sum(1 for m in layer_motives if m.is_active),
                "avg_intensity": sum(m.intensity for m in layer_motives) / len(layer_motives) if layer_motives else 0
            }

        for instinct in InstinctType:
            motive = self.motivations.get(f"{MotivationLayer.INSTINCTUAL.value}_{instinct.value}")
            if motive:
                profile["instincts"][instinct.value] = {
                    "intensity": motive.intensity,
                    "active": motive.is_active,
                    "activation_level": motive.activation_level
                }

        conflicts = self.check_conflicts()
        profile["conflicts"] = [
            {"m1": c.motivation_1, "m2": c.motivation_2, "type": c.conflict_type}
            for c in conflicts
        ]

        dominant = self.get_dominant_motivation()
        if dominant:
            profile["dominant"] = {
                "id": dominant.id,
                "instinct": dominant.instinct_type.value,
                "intensity": dominant.intensity,
                "layer": dominant.layer.value
            }

        return profile

    def modify_intensity(self, motivation_id: str, delta: float) -> bool:
        """修改动机强度"""
        if motivation_id in self.motivations:
            motivation = self.motivations[motivation_id]
            motivation.intensity = max(0.0, min(1.0, motivation.intensity + delta))

            # 检查激活状态
            config = self.instincts.get(motivation.instinct_type)
            if config:
                motivation.is_active = motivation.intensity >= config.threshold

            return True
        return False


def create_motivation_system(character_id: Optional[str] = None) -> MotivationSystem:
    """工厂函数：创建动机系统"""
    return MotivationSystem(character_id=character_id)