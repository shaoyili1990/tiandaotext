"""
Psychology Engine - 心理学引擎

整合Y值系统、MBTI系统、记忆系统、动机系统的综合心理学计算引擎

核心公式流程:
第一步: 基础Y有效计算
第二步: 道德敏感度修正（盈满则亏）
第三步: 全域情绪波动计算
第四步: 盈满而溃（过犹不及）
第五步: 动态重排（自动补位）

天道原则:
- 损有余而补不足
- 盈满则亏
- 过犹不及
- 动态流转
- 并列共担
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import math

from tiandao_core.core.y_value import (
    YValueSystem, YValueConfig, YValueState, TriggerType, TriggerResult
)
from tiandao_core.core.mbti import MBTISystem, MBTIType, BigFiveTraits
from tiandao_core.core.memory import (
    MemorySystem, MemoryType, MemoryNode, MemoryRetrieval
)
from tiandao_core.core.motivation import (
    MotivationSystem, InstinctType, MotivationLayer, Motivation
)
from tiandao_core.core.author import AuthorConstraintSystem, NarrativeMode


class MoralSensitivity(Enum):
    """道德敏感度"""
    LOW = "low"          # 低敏感
    NORMAL = "normal"    # 正常
    HIGH = "high"        # 高敏感


@dataclass
class EmotionalState:
    """情绪状态"""
    valence: float = 0.0        # 效价 [-1, 1], 负面到正面
    arousal: float = 0.5        # 唤醒度 [0, 1]
    dominance: float = 0.5     # 控制感 [0, 1]
    intensity: float = 0.5     # 强度 [0, 1]


@dataclass
class PsychologyOutput:
    """心理学计算输出"""
    y_value: int
    emotional_state: EmotionalState
    active_motivations: List[str]
    triggered_memories: List[str]
    behavioral_tendency: str
    moral_adjustment: float = 0.0
    overflow_warning: bool = False
    messages: List[str] = field(default_factory=list)


@dataclass
class SevenEmotions:
    """七情"""
    joy: float = 0.5           # 喜
    anger: float = 0.0          # 怒
    worry: float = 0.0          # 忧
    thought: float = 0.0        # 思
    sadness: float = 0.0        # 悲
    fear: float = 0.0           # 恐
    shock: float = 0.0          # 惊


class PsychologyEngine:
    """
    心理学引擎 - 综合心理系统

    整合所有子系统，提供统一的心理计算接口

    核心功能:
    1. 五步输出公式执行
    2. 道德敏感度修正
    3. 盈满而溃检测
    4. 情绪七情计算
    5. 系统联动计算
    """

    # 七情范围 [0-10]
    SEVEN_EMOTIONS_RANGE = (0, 10)

    # 道德敏感度阈值
    MORAL_THRESHOLD_HIGH = 0.7
    MORAL_THRESHOLD_LOW = 0.3

    def __init__(
        self,
        base_y: int = 50,
        mbti_type: Optional[str] = None,
        character_id: Optional[str] = None
    ):
        # 初始化各子系统
        self.y_system = YValueSystem(YValueConfig(base_y=base_y))
        self.mbti_system = MBTISystem(mbti_type=mbti_type)
        self.memory_system = MemorySystem()
        self.motivation_system = MotivationSystem(character_id=character_id)
        self.author_system = AuthorConstraintSystem()

        # 初始化情绪状态
        self.emotional_state = EmotionalState()
        self.seven_emotions = SevenEmotions()
        self.moral_sensitivity = MoralSensitivity.NORMAL

        # 动态状态
        self.overflow_count = 0  # 盈满计数
        self.last_output: Optional[PsychologyOutput] = None

    # ========== 五步输出公式 ==========

    def calculate(
        self,
        situation: str,
        context: Optional[Dict] = None,
        interaction_y: Optional[int] = None
    ) -> PsychologyOutput:
        """
        执行五步输出公式

        第一步: 基础Y有效计算
        第二步: 道德敏感度修正（盈满则亏）
        第三步: 全域情绪波动计算
        第四步: 盈满而溃（过犹不及）
        第五步: 动态重排（自动补位）
        """
        messages = []

        # 第一步: 基础Y有效计算
        base_y = self.y_system.Y
        effective_y = base_y

        # 第二步: 道德敏感度修正
        moral_adjustment, moral_msg = self._calculate_moral_adjustment(situation)
        effective_y += moral_adjustment
        messages.append(moral_msg)

        # 第三步: 全域情绪波动计算
        self._calculate_emotional_wave(situation, context)

        # 第四步: 盈满而溃检测
        overflow, overflow_msg = self._check_overflow()
        if overflow:
            self.overflow_count += 1
            messages.append(overflow_msg)

        # 检查击穿
        if interaction_y:
            breakthrough_result = self.y_system.trigger_breakthrough(interaction_y)
            if breakthrough_result.triggered:
                effective_y = breakthrough_result.new_y
                messages.append(breakthrough_result.message)

        # 第五步: 动态重排
        self._dynamic_rearrangement()

        # 检查PTSD触发
        triggered, memories, _ = self.memory_system.check_ptsd_triggers(
            situation, self.y_system.Y
        )
        triggered_memory_ids = [m.memory.id for m in memories]

        # 获取活跃动机
        active_motivations = [
            m.id for m in self.motivation_system.motivations.values()
            if m.is_active
        ]

        # 生成行为倾向
        tendency = self._generate_behavioral_tendency()

        # 构建输出
        output = PsychologyOutput(
            y_value=effective_y,
            emotional_state=self.emotional_state,
            active_motivations=active_motivations,
            triggered_memories=triggered_memory_ids,
            behavioral_tendency=tendency,
            moral_adjustment=moral_adjustment,
            overflow_warning=overflow,
            messages=messages
        )

        self.last_output = output
        return output

    def _calculate_moral_adjustment(self, situation: str) -> Tuple[float, str]:
        """
        第二步: 道德敏感度修正

        天道原则: 损有余而补不足

        道德敏感度影响:
        - 高敏感: 对道德问题更在意
        - 低敏感: 对道德问题较迟钝
        """
        situation_lower = situation.lower()

        # 道德关键词
        moral_keywords = {
            "positive": ["帮助", "保护", "拯救", "诚实", "正直", "善良", "牺牲"],
            "negative": ["欺骗", "伤害", "背叛", "残忍", "自私", "贪婪"]
        }

        positive_count = sum(1 for k in moral_keywords["positive"] if k in situation_lower)
        negative_count = sum(1 for k in moral_keywords["negative"] if k in situation_lower)

        moral_delta = (positive_count - negative_count) * 0.5

        # 根据敏感度调整
        if self.moral_sensitivity == MoralSensitivity.HIGH:
            moral_delta *= 1.5
        elif self.moral_sensitivity == MoralSensitivity.LOW:
            moral_delta *= 0.5

        # 天道: 盈满则亏
        current_y = self.y_system.Y
        if current_y > 70:
            # Y值过高，做修正
            adjustment = -0.1 * (current_y - 70)
            moral_delta += adjustment

        msg = f"道德修正: {moral_delta:+.1f} (敏感度: {self.moral_sensitivity.value})"
        return moral_delta, msg

    def _calculate_emotional_wave(
        self,
        situation: str,
        context: Optional[Dict] = None
    ):
        """
        第三步: 全域情绪波动计算

        计算七情和情绪状态
        """
        situation_lower = situation.lower()

        # 七情计算
        emotion_changes = {
            "joy": 0.0, "anger": 0.0, "worry": 0.0, "thought": 0.0,
            "sadness": 0.0, "fear": 0.0, "shock": 0.0
        }

        # 情绪关键词映射
        emotion_keywords = {
            "joy": ["高兴", "开心", "快乐", "喜悦", "欢"],
            "anger": ["生气", "愤怒", "恼火", "怒"],
            "worry": ["担心", "忧虑", "担忧", "忧"],
            "thought": ["思考", "想", "考虑", "思"],
            "sadness": ["悲伤", "难过", "伤心", "悲哀"],
            "fear": ["害怕", "恐惧", "畏惧", "怕"],
            "shock": ["震惊", "惊讶", "吃惊", "惊"]
        }

        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for k in keywords if k in situation_lower)
            emotion_changes[emotion] = count * 0.5

        # 应用变化
        for emotion, delta in emotion_changes.items():
            current = getattr(self.seven_emotions, emotion)
            setattr(self.seven_emotions, emotion, max(0, min(10, current + delta)))

        # 更新情绪状态
        self._update_emotional_state()

    def _update_emotional_state(self):
        """更新基础情绪状态"""
        # 效价: 基于七情计算
        positive_emotions = self.seven_emotions.joy
        negative_emotions = (
            self.seven_emotions.anger +
            self.seven_emotions.sadness +
            self.seven_emotions.fear +
            self.seven_emotions.shock
        )

        total = positive_emotions + negative_emotions
        if total > 0:
            self.emotional_state.valence = (positive_emotions - negative_emotions) / total
        else:
            self.emotional_state.valence = 0.0

        # 唤醒度: 基于情绪强度
        total_intensity = sum([
            self.seven_emotions.anger,
            self.seven_emotions.shock,
            self.seven_emotions.fear
        ])
        self.emotional_state.arousal = min(1.0, total_intensity / 15)

        # 控制感: 基于Y值和MBTI
        y_factor = self.y_system.Y / 100
        emotional_factor = 1 - self.mbti_system.big_five.neuroticism
        self.emotional_state.dominance = (y_factor + emotional_factor) / 2

    def _check_overflow(self) -> Tuple[bool, str]:
        """
        第四步: 盈满而溃检测

        天道原则: 盈满则亏，过犹不及

        当某个情绪或Y值达到极值时，可能崩溃
        """
        overflow = False
        message = ""

        # 检查Y值溢满
        if self.y_system.Y >= 95:
            overflow = True
            message = "警告: Y值接近极值，触发'盈满而溃'"
            # 强制降低Y值
            self.y_system.state.current_y = 85

        # 检查情绪溢满
        for emotion_name in ["anger", "fear", "shock"]:
            emotion_value = getattr(self.seven_emotions, emotion_name)
            if emotion_value >= 9:
                overflow = True
                message = f"警告: {emotion_name}情绪极值，触发'盈满而溃'"
                # 降低情绪
                setattr(self.seven_emotions, emotion_name, 7)

        return overflow, message

    def _dynamic_rearrangement(self):
        """
        第五步: 动态重排

        自动补位，保持系统平衡
        天道原则: 动态流转，并列共担
        """
        # 处理补偿机制
        if self.y_system.process_compensation():
            # 补偿结束，触发回弹
            self.y_system.process_rebound()

        # 检查动机冲突并解决
        conflicts = self.motivation_system.check_conflicts()
        for conflict in conflicts:
            self.motivation_system.resolve_conflict(conflict)

    def _generate_behavioral_tendency(self) -> str:
        """生成行为倾向描述"""
        # 基于Y值和情绪状态生成倾向
        y = self.y_system.Y
        dominance = self.emotional_state.dominance

        if y >= 80:
            if dominance >= 0.7:
                return "主导型: 主动出击，掌控局面"
            else:
                return "压制型: 强势压制，情绪外显"
        elif y >= 60:
            return "稳定型: 理性应对，保持平衡"
        elif y >= 40:
            return "被动型: 观望等待，被动应对"
        else:
            return "脆弱型: 防御退缩，易受影响"

    # ========== 辅助方法 ==========

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        emotional_intensity: float = 0.5,
        **kwargs
    ) -> MemoryNode:
        """添加记忆到记忆系统"""
        return self.memory_system.add_memory(
            content=content,
            memory_type=memory_type,
            emotional_intensity=emotional_intensity,
            **kwargs
        )

    def trigger_ptsd(self, event: str) -> TriggerResult:
        """触发PTSD"""
        trauma_level = 0.8  # 默认创伤等级
        trauma_y = int(70 + trauma_level * 20)
        return self.y_system.trigger_ptsd(trauma_y)

    def set_moral_sensitivity(self, sensitivity: MoralSensitivity):
        """设置道德敏感度"""
        self.moral_sensitivity = sensitivity

    def get_full_report(self) -> Dict:
        """获取完整心理报告"""
        return {
            "y_value": self.y_system.get_state_report(),
            "mbti": self.mbti_system.get_full_profile(),
            "memory_summary": self.memory_system.get_memory_summary(),
            "motivation_profile": self.motivation_system.get_motivation_profile(),
            "author_system": self.author_system.get_system_report(),
            "emotional_state": {
                "valence": self.emotional_state.valence,
                "arousal": self.emotional_state.arousal,
                "dominance": self.emotional_state.dominance,
                "intensity": self.emotional_state.intensity
            },
            "seven_emotions": {
                "joy": self.seven_emotions.joy,
                "anger": self.seven_emotions.anger,
                "worry": self.seven_emotions.worry,
                "thought": self.seven_emotions.thought,
                "sadness": self.seven_emotions.sadness,
                "fear": self.seven_emotions.fear,
                "shock": self.seven_emotions.shock
            },
            "moral_sensitivity": self.moral_sensitivity.value,
            "overflow_count": self.overflow_count
        }


def create_psychology_engine(
    base_y: int = 50,
    mbti_type: str = "INTJ"
) -> PsychologyEngine:
    """工厂函数：创建心理学引擎"""
    return PsychologyEngine(base_y=base_y, mbti_type=mbti_type)