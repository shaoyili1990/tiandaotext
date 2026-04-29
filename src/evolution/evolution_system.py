"""
Evolution System - 演化系统

演化规则：
1. 角色行为累积影响Y值
2. 记忆满额触发状态变化
3. 权重达到阈值触发类别晋升/降级
4. 异常记忆超限触发疯狂/脑死亡

演化类型：
- Y值演化：基于行为的Y值变化
- 记忆演化：记忆积累和遗忘
- 权重演化：角色重要性变化
- 状态演化：角色状态转变（如黑化、觉醒等）
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from tiandao_core.core.profile import CharacterProfile
from tiandao_core.core.y_value import YValueSystem, TriggerType
from tiandao_core.core.memory import MemorySystem, MemoryType
from tiandao_core.rendao.weight_network import WeightNetwork, CharacterClass
from tiandao_core.rendao.lao_tian_qi import LaoTianQi, ActionValue


class EvolutionType(Enum):
    """演化类型"""
    Y_VALUE_CHANGE = "y_value_change"
    MEMORY_ACCUMULATION = "memory_accumulation"
    WEIGHT_PROMOTION = "weight_promotion"
    WEIGHT_DEMOTION = "weight_demotion"
    TRAUMA_FORMATION = "trauma_formation"
    PTSD_TRIGGER = "ptsd_trigger"
    BREAKTHROUGH = "breakthrough"
    STATE_TRANSITION = "state_transition"


@dataclass
class EvolutionEvent:
    """演化事件"""
    evolution_type: EvolutionType
    character_name: str
    timestamp: str
    description: str
    old_value: any
    new_value: any
    trigger_event: str = ""


@dataclass
class CharacterEvolution:
    """角色演化状态"""
    character_name: str
    current_y: int
    baseline_y: int
    weight: int
    character_class: str
    memory_count: int
    trauma_level: float
    is_insane: bool = False
    is_brain_dead: bool = False
    evolution_history: List[EvolutionEvent] = field(default_factory=list)


class EvolutionSystem:
    """
    演化系统

    管理角色随时间的动态演化
    """

    # 记忆容量限制
    MAX_NORMAL_MEMORIES = 100
    MAX_SHORT_TERM_MEMORIES = 20
    MAX_ANOMALOUS_MEMORIES = 10

    # 演化阈值
    TRAUMA_THRESHOLD = 0.7
    INSANITY_THRESHOLD = 0.9
    BRAIN_DEATH_THRESHOLD = 0.95

    def __init__(self, api=None):
        self.api = api
        self.weight_network = WeightNetwork()
        self.lao_tian_qi = LaoTianQi()
        self.character_evolutions: Dict[str, CharacterEvolution] = {}
        self.evolution_log: List[EvolutionEvent] = []

    def register_character(
        self,
        character_profile: CharacterProfile,
        initial_weight: int = 50
    ):
        """注册角色到演化系统"""
        name = character_profile.info.name

        self.weight_network.register_character(
            name=name,
            character_class=self._infer_class_from_weight(initial_weight),
            custom_weight=initial_weight
        )

        self.character_evolutions[name] = CharacterEvolution(
            character_name=name,
            current_y=character_profile.y_system.Y if character_profile.y_system else 50,
            baseline_y=character_profile.y_system.state.baseline_y if character_profile.y_system else 50,
            weight=initial_weight,
            character_class=self._infer_class_from_weight(initial_weight).value,
            memory_count=0,
            trauma_level=character_profile.info.trauma_level
        )

    def _infer_class_from_weight(self, weight: int) -> CharacterClass:
        """从权重推断角色分类"""
        if weight >= 85:
            return CharacterClass.PROTAGONIST
        elif weight >= 60:
            return CharacterClass.MAIN
        elif weight >= 40:
            return CharacterClass.SECONDARY
        else:
            return CharacterClass.NPC

    def process_action(
        self,
        character_name: str,
        action: str,
        context: str = ""
    ) -> EvolutionEvent:
        """
        处理角色行为，触发演化

        返回演化事件
        """
        if character_name not in self.character_evolutions:
            raise ValueError(f"Character {character_name} not registered")

        evolution = self.character_evolutions[character_name]

        # 老天气评判
        judgment = self.lao_tian_qi.evaluate_action(
            action=action,
            character_mbti="INTJ",  # 需要从角色获取
            character_y=evolution.current_y
        )

        # 计算Y值变化
        y_change = 0
        if judgment.action_value == ActionValue.HIGHLY_VALUABLE:
            y_change = 3
        elif judgment.action_value == ActionValue.VALUABLE:
            y_change = 1
        elif judgment.action_value == ActionValue.WORTHLESS:
            y_change = -5
        elif judgment.action_value == ActionValue.HARMFUL:
            y_change = -8

        # 应用Y值变化
        old_y = evolution.current_y
        new_y = max(1, min(100, old_y + y_change))

        evolution_event = EvolutionEvent(
            evolution_type=EvolutionType.Y_VALUE_CHANGE,
            character_name=character_name,
            timestamp=datetime.now().isoformat(),
            description=f"Y值从{old_y}变为{new_y}",
            old_value=old_y,
            new_value=new_y,
            trigger_event=action[:100]
        )

        # 检查触发机制
        if new_y < 40 and old_y >= 40:
            # 击穿事件
            breakthrough_event = EvolutionEvent(
                evolution_type=EvolutionType.BREAKTHROUGH,
                character_name=character_name,
                timestamp=datetime.now().isoformat(),
                description=f"角色{character_name}被击穿，Y值从{old_y}降至{new_y}",
                old_value=old_y,
                new_value=new_y,
                trigger_event=action[:100]
            )
            self.evolution_log.append(breakthrough_event)
            evolution.evolution_history.append(breakthrough_event)

        elif y_change != 0:
            evolution.current_y = new_y
            self.evolution_log.append(evolution_event)
            evolution.evolution_history.append(evolution_event)

        # 更新权重
        weight_delta = judgment.weight_suggestion
        if weight_delta != 0:
            self.weight_network.apply_weight_change(
                character_name, weight_delta, judgment.message
            )

            # 检查分类变化
            class_change = self.weight_network.check_class_change(character_name)
            if class_change:
                evolution.character_class = class_change.split("从")[-1].split("降")[0].strip() if "降" in class_change else class_change

        return evolution_event

    def add_memory(
        self,
        character_name: str,
        memory_content: str,
        memory_type: MemoryType,
        is_traumatic: bool = False,
        trauma_level: float = 0.0
    ) -> EvolutionEvent:
        """
        添加记忆并检查演化

        返回演化事件
        """
        if character_name not in self.character_evolutions:
            raise ValueError(f"Character {character_name} not registered")

        evolution = self.character_evolutions[character_name]
        evolution.memory_count += 1

        event = EvolutionEvent(
            evolution_type=EvolutionType.MEMORY_ACCUMULATION,
            character_name=character_name,
            timestamp=datetime.now().isoformat(),
            description=f"添加新记忆: {memory_content[:50]}...",
            old_value=evolution.memory_count - 1,
            new_value=evolution.memory_count
        )

        # 检查记忆过载
        if is_traumatic and trauma_level > self.TRAUMA_THRESHOLD:
            evolution.trauma_level = max(evolution.trauma_level, trauma_level)

            trauma_event = EvolutionEvent(
                evolution_type=EvolutionType.TRAUMA_FORMATION,
                character_name=character_name,
                timestamp=datetime.now().isoformat(),
                description=f"形成创伤，创伤等级: {trauma_level}",
                old_value=evolution.trauma_level,
                new_value=trauma_level
            )
            self.evolution_log.append(trauma_event)
            evolution.evolution_history.append(trauma_event)

            # 检查疯狂状态
            if evolution.trauma_level >= self.INSANITY_THRESHOLD:
                evolution.is_insane = True
                insanity_event = EvolutionEvent(
                    evolution_type=EvolutionType.STATE_TRANSITION,
                    character_name=character_name,
                    timestamp=datetime.now().isoformat(),
                    description="角色进入疯狂状态",
                    old_value=False,
                    new_value=True
                )
                self.evolution_log.append(insanity_event)
                evolution.evolution_history.append(insanity_event)

        # 检查脑死亡
        if evolution.trauma_level >= self.BRAIN_DEATH_THRESHOLD:
            evolution.is_brain_dead = True
            brain_death_event = EvolutionEvent(
                evolution_type=EvolutionType.STATE_TRANSITION,
                character_name=character_name,
                timestamp=datetime.now().isoformat(),
                description="角色进入脑死亡状态",
                old_value=False,
                new_value=True
            )
            self.evolution_log.append(brain_death_event)
            evolution.evolution_history.append(brain_death_event)

        self.evolution_log.append(event)
        evolution.evolution_history.append(event)

        return event

    def trigger_ptsd(
        self,
        character_name: str,
        trigger_event: str
    ) -> EvolutionEvent:
        """
        触发PTSD
        """
        if character_name not in self.character_evolutions:
            raise ValueError(f"Character {character_name} not registered")

        evolution = self.character_evolutions[character_name]

        # PTSD触发使Y值冲向高位
        old_y = evolution.current_y
        new_y = min(100, old_y + 15)

        event = EvolutionEvent(
            evolution_type=EvolutionType.PTSD_TRIGGER,
            character_name=character_name,
            timestamp=datetime.now().isoformat(),
            description=f"PTSD触发: {trigger_event[:50]}",
            old_value=old_y,
            new_value=new_y,
            trigger_event=trigger_event
        )

        evolution.current_y = new_y
        evolution.trauma_level = min(1.0, evolution.trauma_level + 0.1)

        self.evolution_log.append(event)
        evolution.evolution_history.append(event)

        return event

    def evolve_character(
        self,
        character_name: str,
        action: str,
        context: str = "",
        memory_content: str = None,
        memory_type: MemoryType = MemoryType.EPISODIC,
        is_traumatic: bool = False,
        trauma_level: float = 0.0
    ) -> Dict:
        """
        综合演化处理

        返回演化结果
        """
        events = []

        # 处理行为
        action_event = self.process_action(character_name, action, context)
        events.append(action_event)

        # 处理记忆（如果有）
        if memory_content:
            memory_event = self.add_memory(
                character_name, memory_content, memory_type, is_traumatic, trauma_level
            )
            events.append(memory_event)

        # 获取当前状态
        evolution = self.character_evolutions.get(character_name)

        return {
            "character": character_name,
            "events": [
                {
                    "type": e.evolution_type.value,
                    "description": e.description,
                    "old_value": e.old_value,
                    "new_value": e.new_value
                }
                for e in events
            ],
            "current_state": {
                "y_value": evolution.current_y if evolution else 0,
                "weight": evolution.weight if evolution else 0,
                "character_class": evolution.character_class if evolution else "unknown",
                "trauma_level": evolution.trauma_level if evolution else 0.0,
                "is_insane": evolution.is_insane if evolution else False,
                "is_brain_dead": evolution.is_brain_dead if evolution else False
            }
        }

    def get_character_evolution(self, character_name: str) -> Optional[CharacterEvolution]:
        """获取角色演化状态"""
        return self.character_evolutions.get(character_name)

    def get_evolution_log(
        self,
        character_name: str = None,
        limit: int = 20
    ) -> List[EvolutionEvent]:
        """获取演化日志"""
        if character_name:
            evolution = self.character_evolutions.get(character_name)
            if evolution:
                return evolution.evolution_history[-limit:]
            return []
        return self.evolution_log[-limit:]

    def get_evolution_summary(self) -> Dict:
        """获取演化系统摘要"""
        total_events = len(self.evolution_log)
        insane_count = sum(1 for e in self.character_evolutions.values() if e.is_insane)
        brain_dead_count = sum(1 for e in self.character_evolutions.values() if e.is_brain_dead)

        return {
            "total_characters": len(self.character_evolutions),
            "total_evolution_events": total_events,
            "insane_characters": insane_count,
            "brain_dead_characters": brain_dead_count,
            "weight_network_summary": self.weight_network.get_network_summary()
        }


def create_evolution_system(api=None) -> EvolutionSystem:
    """工厂函数：创建演化系统"""
    return EvolutionSystem(api=api)