"""
Three-Layer Unity System - 三层统一系统

架构设计：
┌─────────────────────────────────────────────────────┐
│                    老天爷层                          │
│         (最终仲裁/主观评判/世界意志)                   │
├─────────────────────────────────────────────────────┤
│                    天道层                            │
│       (Y值系统/三大机制/规则/因果链源头)               │
├─────────────────────────────────────────────────────┤
│                  因果蝴蝶层                          │
│    (因果网/蝴蝶效应/变数传导/空间影响力)              │
└─────────────────────────────────────────────────────┘

核心原则：
1. 不存在单独的因果 - 所有因果都经过三层验证
2. 没有没来由的蝴蝶效应 - 所有效应都源于天道触发
3. 三层彼此互相影响/成就/调用 - 形成闭环
4. 变数产生更多变数 - 连锁反应

变数流转：
- 天道触发 → 产生变数 → 传给因果蝴蝶层
- 因果蝴蝶层传导 → 反馈给天道（触发或修正）
- 老天爷全程监控 → 对变数进行主观评判
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime

from .weight_network import WeightNetwork, CharacterClass, WeightChange
from .lao_tian_qi import LaoTianQi, LaoTianQiJudgment, ActionValue
from .butterfly_effect import ButterflyEffectSystem, InfluenceType, Position3D
from .spacetime_manager import SpacetimeManager, SpacetimeCoordinate, MovementType


class VariableType(Enum):
    """变数类型"""
    Y_VALUE_CHANGE = "y_value_change"       # Y值变化
    WEIGHT_ADJUSTMENT = "weight_adjustment"  # 权重调整
    PHYSICS_EFFECT = "physics_effect"         # 蝴蝶效应
    CAUSAL_CHAIN = "causal_chain"             # 因果链
    BREAKTHROUGH = "breakthrough"             # 击穿
    COMPENSATION = "compensation"             # 补偿


@dataclass
class VariableRecord:
    """变数记录"""
    id: str
    timestamp: str
    source_layer: str            # "tiandao" / "因果蝴蝶" / "lao_tian_qi"
    variable_type: VariableType
    source_character: str
    target_character: str
    intensity: float             # 变数强度
    description: str
    propagated: bool = False      # 是否已传导
    judgment: Optional[str] = None  # 老天爷评判


class ThreeLayerSystem:
    """
    三层统一系统

    老天爷 + 天道 + 因果蝴蝶 = 三位一体的世界运行机制
    """

    def __init__(self):
        # 老天爷层 - 最终仲裁
        self.lao_tian_qi = LaoTianQi()

        # 天道层 - Y值规则
        self.y_value_rules: Dict[str, Dict] = {}

        # 因果蝴蝶层
        self.weight_network = WeightNetwork()
        self.butterfly_effect = ButterflyEffectSystem()
        self.spacetime_manager = SpacetimeManager()

        # 变数记录
        self.variable_history: List[VariableRecord] = []
        self._variable_counter = 0

    def _generate_variable_id(self) -> str:
        """生成变数ID"""
        self._variable_counter += 1
        return f"VAR_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._variable_counter}"

    def register_character(
        self,
        name: str,
        y_value: int,
        position: Position3D,
        weight: int,
        mbti: str,
        character_class: CharacterClass = CharacterClass.MAIN
    ):
        """注册角色到三层系统"""
        # 因果蝴蝶层 - 权重网络
        self.weight_network.register_character(name, character_class, weight)

        # 因果蝴蝶层 - 蝴蝶效应
        self.butterfly_effect.register_character(name, y_value, position, weight, mbti)

        # 因果蝴蝶层 - 时空管理
        if position is not None:
            coord = SpacetimeCoordinate(
                x=position.x, y=position.y, z=position.z,
                timestamp=datetime.now().isoformat()
            )
            self.spacetime_manager.record_presence(name, coord, MovementType.NATURAL)
        else:
            coord = SpacetimeCoordinate(
                x=0.0, y=0.0, z=0.0,
                timestamp=datetime.now().isoformat()
            )
            self.spacetime_manager.record_presence(name, coord, MovementType.NATURAL)

        # 天道层 - 初始化Y值规则
        self.y_value_rules[name] = {
            "current_y": y_value,
            "baseline_y": y_value,
            "mbti": mbti,
            "pending_compensation": None,
            "pending_rebound": None
        }

    def trigger_y_value_change(
        self,
        character_name: str,
        delta: int,
        reason: str
    ) -> VariableRecord:
        """
        天道层触发Y值变化

        这是一个变数，会传导到因果蝴蝶层
        """
        var_id = self._generate_variable_id()

        # 更新天道层
        if character_name in self.y_value_rules:
            old_y = self.y_value_rules[character_name]["current_y"]
            new_y = max(1, min(100, old_y + delta))
            self.y_value_rules[character_name]["current_y"] = new_y

            # 更新蝴蝶效应系统
            self.butterfly_effect.update_character_state(character_name, y_value=new_y)

        # 创建变数记录
        var_record = VariableRecord(
            id=var_id,
            timestamp=datetime.now().isoformat(),
            source_layer="tiandao",
            variable_type=VariableType.Y_VALUE_CHANGE,
            source_character=character_name,
            target_character=character_name,
            intensity=abs(delta) / 100.0,
            description=f"Y值变化: {reason} ({delta:+d})"
        )

        self.variable_history.append(var_record)

        # 检查是否需要传导到因果蝴蝶层
        self._propagate_to_causal_layer(var_record)

        return var_record

    def trigger_weight_change(
        self,
        character_name: str,
        delta: int,
        reason: str
    ) -> VariableRecord:
        """
        因果蝴蝶层触发权重变化

        这会影响天道层的权重计算
        """
        var_id = self._generate_variable_id()

        # 更新权重网络
        change = self.weight_network.apply_weight_change(character_name, delta, reason)

        # 创建变数记录
        var_record = VariableRecord(
            id=var_id,
            timestamp=datetime.now().isoformat(),
            source_layer="因果蝴蝶",
            variable_type=VariableType.WEIGHT_ADJUSTMENT,
            source_character=character_name,
            target_character=character_name,
            intensity=abs(delta) / 100.0,
            description=f"权重变化: {reason} ({delta:+d})"
        )

        self.variable_history.append(var_record)

        # 反馈给天道层
        self._feedback_to_tiandao(var_record)

        return var_record

    def trigger_breakthrough(
        self,
        attacker_name: str,
        defender_name: str
    ) -> Tuple[VariableRecord, Optional[VariableRecord]]:
        """
        击穿事件 - 天道层核心机制

        触发过程：
        1. 天道层检测击穿条件（ΔY阈值）
        2. 产生变数，传导到因果蝴蝶层
        3. 老天爷评判击穿行为
        """
        var_id = self._generate_variable_id()

        # 获取攻击者和防御者Y值
        attacker_y = self.y_value_rules.get(attacker_name, {}).get("current_y", 50)
        defender_y = self.y_value_rules.get(defender_name, {}).get("current_y", 50)

        # 计算击穿后Y值
        delta_y = attacker_y - defender_y

        # 确定阈值
        if defender_y < 40:
            threshold = 30
        elif defender_y < 70:
            threshold = 20
        else:
            threshold = 15

        breakthrough_triggered = delta_y >= threshold

        # 应用击穿效应
        if breakthrough_triggered:
            # 计算防御者Y值变化
            y_change = -10  # 被击穿后Y值下降

            # 天道层更新
            if defender_name in self.y_value_rules:
                old_y = self.y_value_rules[defender_name]["current_y"]
                new_y = max(1, min(100, old_y + y_change))
                self.y_value_rules[defender_name]["current_y"] = new_y

            # 因果蝴蝶层更新
            self.butterfly_effect.update_character_state(defender_name, y_value=new_y)

            # 老天爷评判
            judgment = self.lao_tian_qi.evaluate_action(
                action=f"{attacker_name}击穿了{defender_name}",
                character_mbti=self.y_value_rules.get(attacker_name, {}).get("mbti", "INTJ"),
                character_y=attacker_y
            )

            # 创建变数记录
            var_record = VariableRecord(
                id=var_id,
                timestamp=datetime.now().isoformat(),
                source_layer="tiandao",
                variable_type=VariableType.BREAKTHROUGH,
                source_character=attacker_name,
                target_character=defender_name,
                intensity=abs(delta_y) / 100.0,
                description=f"击穿事件: {attacker_name}(Y={attacker_y}) → {defender_name}(Y={defender_y}) ΔY={delta_y}",
                judgment=f"老天爷评判: {judgment.message}"
            )

            self.variable_history.append(var_record)

            # 传导到因果蝴蝶层
            self._propagate_to_causal_layer(var_record)

            # 蝴蝶效应传导
            effect = self.butterfly_effect.apply_breakthrough_effect(attacker_name, defender_name)

            return var_record, breakthrough_triggered

        return None, breakthrough_triggered

    def _propagate_to_causal_layer(self, var_record: VariableRecord):
        """变数从天道层传导到因果蝴蝶层"""
        if var_record.variable_type == VariableType.Y_VALUE_CHANGE:
            # Y值变化可能触发蝴蝶效应
            if var_record.intensity > 0.3:  # 高强度变数
                self.butterfly_effect.propagate_effect(
                    source_name=var_record.source_character,
                    effect_type=InfluenceType.REBOUND,
                    intensity=var_record.intensity,
                    max_propagation=2
                )
                var_record.propagated = True

    def _feedback_to_tiandao(self, var_record: VariableRecord):
        """因果蝴蝶层反馈到天道层"""
        if var_record.variable_type == VariableType.WEIGHT_ADJUSTMENT:
            # 权重变化可能影响Y值基线
            # 简化处理：记录反馈
            pass

    def trigger_causal_chain(
        self,
        source_character: str,
        target_character: str,
        chain_type: str,
        intensity: float
    ) -> VariableRecord:
        """
        触发因果链

        因果链是因果蝴蝶层的核心机制
        """
        var_id = self._generate_variable_id()

        var_record = VariableRecord(
            id=var_id,
            timestamp=datetime.now().isoformat(),
            source_layer="因果蝴蝶",
            variable_type=VariableType.CAUSAL_CHAIN,
            source_character=source_character,
            target_character=target_character,
            intensity=intensity,
            description=f"因果链触发: {source_character} → {target_character} ({chain_type})"
        )

        self.variable_history.append(var_record)

        # 老天爷评判
        judgment = self.lao_tian_qi.evaluate_action(
            action=f"因果链: {chain_type}",
            character_mbti=self.y_value_rules.get(source_character, {}).get("mbti", "INTJ"),
            character_y=self.y_value_rules.get(source_character, {}).get("current_y", 50)
        )

        var_record.judgment = f"老天爷评判: {judgment.message}"

        # 反馈给天道层
        self._feedback_to_tiandao(var_record)

        return var_record

    def check_physics_theorems(self) -> List[VariableRecord]:
        """
        检查物理定理 - 因果蝴蝶层

        检测后反馈给天道层
        """
        physics_alerts = self.butterfly_effect.check_physics_theorems()
        triggered_vars = []

        for alert in physics_alerts:
            # 解析alert获取角色名
            parts = alert.split("(")
            if len(parts) >= 2:
                char_name = parts[0].split(": ")[-1].strip()

                var_id = self._generate_variable_id()
                var_record = VariableRecord(
                    id=var_id,
                    timestamp=datetime.now().isoformat(),
                    source_layer="因果蝴蝶",
                    variable_type=VariableType.PHYSICS_EFFECT,
                    source_character=char_name,
                    target_character=char_name,
                    intensity=0.5,
                    description=f"物理定理触发: {alert}"
                )

                self.variable_history.append(var_record)
                triggered_vars.append(var_record)

                # 反馈给天道层
                self._feedback_to_tiandao(var_record)

        return triggered_vars

    def lao_tian_qi_judgment(
        self,
        character_name: str,
        action: str
    ) -> Tuple[LaoTianQiJudgment, Optional[VariableRecord]]:
        """
        老天爷评判 - 最终仲裁

        所有变数最终都要经过老天爷的评判
        """
        # 获取角色信息
        y_value = self.y_value_rules.get(character_name, {}).get("current_y", 50)
        mbti = self.y_value_rules.get(character_name, {}).get("mbti", "INTJ")

        # 老天爷评判
        judgment = self.lao_tian_qi.evaluate_action(action, mbti, y_value)

        # 创建变数记录
        var_id = self._generate_variable_id()
        var_record = VariableRecord(
            id=var_id,
            timestamp=datetime.now().isoformat(),
            source_layer="lao_tian_qi",
            variable_type=VariableType.Y_VALUE_CHANGE,
            source_character=character_name,
            target_character=character_name,
            intensity=0.5,
            description=f"老天爷评判: {action}",
            judgment=f"{judgment.action_value.value}: {judgment.message}"
        )

        self.variable_history.append(var_record)

        # 如果权重建议非零，触发权重变化
        if judgment.weight_suggestion != 0:
            self.trigger_weight_change(
                character_name,
                judgment.weight_suggestion,
                judgment.message
            )

        return judgment, var_record

    def get_three_layer_summary(self) -> Dict:
        """获取三层系统完整摘要"""
        return {
            "lao_tian_qi": self.lao_tian_qi.get_judgment_summary(),
            "y_value_rules": {
                name: rules for name, rules in self.y_value_rules.items()
            },
            "weight_network": self.weight_network.get_network_summary(),
            "butterfly_effect": self.butterfly_effect.get_effect_summary(),
            "spacetime": self.spacetime_manager.get_spacetime_summary(),
            "variable_history_count": len(self.variable_history),
            "recent_variables": [
                {
                    "id": v.id,
                    "type": v.variable_type.value,
                    "source": v.source_layer,
                    "description": v.description
                }
                for v in self.variable_history[-5:]
            ]
        }

    def get_variables_by_layer(self, layer: str) -> List[VariableRecord]:
        """获取指定层的所有变数"""
        return [v for v in self.variable_history if v.source_layer == layer]


def create_three_layer_system() -> ThreeLayerSystem:
    """工厂函数：创建三层统一系统"""
    return ThreeLayerSystem()