"""
Y-Value System - 主观意识凝练强度系统

核心公式:
- Y = 人物「主观意识凝练强度」
- 系统模拟"水"的动态流转
- 风浪来袭时，所有处于浪尖的波峰共同承受双倍冲击力

机制:
- 触发机制 (Trigger): Y值瞬间跃迁的唯一条件
- 补偿机制 (Compensation): Y值被触发跃迁后的防御性调整
- 回弹机制 (Rebound): 补偿机制结束后，Y值自动回归人物自身基线
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import math


class TriggerType(Enum):
    """Y值触发类型枚举"""
    BREAKTHROUGH = "breakthrough"           # 击穿触发
    PTSD = "ptsd"                           # PTSD扳机
    MAJOR_EVENT = "major_event"             # 重大人生事件
    EMOTIONAL_EXTREME = "emotional_extreme"  # 情绪极限


class CompensationType(Enum):
    """补偿类型枚举 - 4种补偿机制"""
    BREAKTHROUGH_COMP = "breakthrough_comp"     # 被击穿后补偿
    GUILT_EXPLOSION = "guilt_explosion"         # 愧疚爆发补偿
    SELF_NARCOTIZATION = "self_narcotization"  # 自我麻痹补偿
    ATTACHMENT_FILLING = "attachment_filling"   # 依恋填补补偿


@dataclass
class YValueConfig:
    """Y值系统配置"""
    base_y: int = 50                        # 基础Y值 (1-100)
    min_y: int = 1
    max_y: int = 100
    compensation_duration: int = 3          # 补偿机制持续时间(剧情节点)
    rebound_rate: float = 0.3               # 回弹速率


@dataclass
class YValueState:
    """Y值当前状态"""
    current_y: int
    baseline_y: int                          # 自身基线 (MBTI+创伤决定)
    is_compensating: bool = False            # 是否处于补偿状态
    compensation_type: Optional[CompensationType] = None  # 补偿类型
    compensation_remaining: int = 0          # 补偿剩余时间
    trigger_history: List[Dict] = field(default_factory=list)


@dataclass
class TriggerResult:
    """触发结果"""
    triggered: bool
    trigger_type: Optional[TriggerType] = None
    old_y: int = 0
    new_y: int = 0
    delta_y: int = 0
    message: str = ""


class YValueSystem:
    """
    Y值系统 - 主观意识凝练强度核心

    Y值代表人物「主观意识凝练强度」，是人物精神内核的稳定指数
    不代表: 情绪、血量、好感度

    Y值体现:
    1. 执行力: Y越高，主观意识越坚定，执行力越强
    2. 影响力: Y越高，气场越强，越能带动、碾压Y值更低的人
    3. 被影响力: Y越低，意识越涣散，越容易被诱骗、洗脑、操控、击穿
    """

    # 击穿阈值规则表
    BREAKTHROUGH_THRESHOLDS = {
        "extreme_fragile": (0, 40, 30),      # (min, max, threshold)
        "normal": (40, 70, 20),
        "strong": (70, 100, 15)
    }

    def __init__(self, config: Optional[YValueConfig] = None):
        self.config = config or YValueConfig()
        self.state = YValueState(
            current_y=self.config.base_y,
            baseline_y=self.config.base_y
        )

    @property
    def Y(self) -> int:
        """获取当前Y值"""
        return self.state.current_y

    def get_threshold(self, y: Optional[int] = None) -> int:
        """
        获取指定Y值的击穿阈值

        规则表:
        - Y < 40 (极度脆弱): ΔY ≥ 30
        - 40 ≤ Y < 70 (普通人~偏强): ΔY ≥ 20
        - Y ≥ 70 (意志极强/创伤者): ΔY ≥ 15
        """
        y = y or self.state.current_y

        if y < 40:
            return 30
        elif y < 70:
            return 20
        else:
            return 15

    def calculate_delta(self, other_y: int) -> int:
        """
        计算与对方的Y值差
        ΔY = 对方Y - 自身Y (仅用于判断击穿)
        """
        return other_y - self.state.current_y

    def check_breakthrough(
        self,
        attacker_y: int,
        defender_y: Optional[int] = None
    ) -> bool:
        """
        检查是否发生击穿

        触发条件: ΔY ≥ 对应击穿阈值

        击穿跃迁规则:
        被击穿后，Y值瞬间跃迁为「自身基线±10」
        """
        if defender_y is None:
            defender_y = self.state.current_y

        delta = attacker_y - defender_y

        if defender_y < 40:
            threshold = 30
        elif defender_y < 70:
            threshold = 20
        else:
            threshold = 15

        return delta >= threshold

    def trigger_breakthrough(
        self,
        attacker_y: int,
        defender_y: Optional[int] = None
    ) -> TriggerResult:
        """
        触发击穿机制

        被击穿后，Y值瞬间跃迁为「自身基线±10」，并启动被击穿后补偿
        """
        if defender_y is None:
            defender_y = self.state.current_y

        old_y = defender_y
        delta = attacker_y - defender_y
        threshold = self.get_threshold(defender_y)

        if delta >= threshold:
            # 跃迁为自身基线±10
            new_y = self.state.baseline_y + 10 if old_y > self.state.baseline_y else self.state.baseline_y - 10
            new_y = max(self.config.min_y, min(self.config.max_y, new_y))

            self._apply_transition(new_y, TriggerType.BREAKTHROUGH, {
                "attacker_y": attacker_y,
                "defender_y": defender_y,
                "delta": delta,
                "threshold": threshold
            }, CompensationType.BREAKTHROUGH_COMP)

            return TriggerResult(
                triggered=True,
                trigger_type=TriggerType.BREAKTHROUGH,
                old_y=old_y,
                new_y=new_y,
                delta_y=new_y - old_y,
                message=f"击穿发生: Y值从{old_y}跃迁至{new_y}"
            )

        return TriggerResult(
            triggered=False,
            old_y=old_y,
            new_y=old_y,
            message=f"未达到击穿阈值 (ΔY={delta}, 需要≥{threshold})"
        )

    def trigger_ptsd(self, trauma_y: int, guilt_explosion: bool = False) -> TriggerResult:
        """
        PTSD扳机触发

        触发条件: 发生与过往创伤高度相似的事件
        特性: Y值瞬间跃迁（无规律，贴合创伤者心理）
        示例: 枫看到战友牺牲相关场景，Y值从70瞬间冲高至85

        参数:
        - trauma_y: 创伤Y值
        - guilt_explosion: 是否为愧疚爆发补偿类型
        """
        old_y = self.state.current_y

        # PTSD触发，Y值冲向高位（防御性跃迁）
        new_y = min(self.config.max_y, trauma_y)

        comp_type = CompensationType.GUILT_EXPLOSION if guilt_explosion else CompensationType.BREAKTHROUGH_COMP

        self._apply_transition(new_y, TriggerType.PTSD, {
            "trauma_level": abs(trauma_y - self.state.baseline_y)
        }, comp_type)

        return TriggerResult(
            triggered=True,
            trigger_type=TriggerType.PTSD,
            old_y=old_y,
            new_y=new_y,
            delta_y=new_y - old_y,
            message=f"PTSD触发: Y值从{old_y}瞬间跃迁至{new_y}"
        )

    def trigger_major_event(self, event_type: str, intensity: int = 1, compensation_type: Optional[CompensationType] = None) -> TriggerResult:
        """
        重大人生事件触发

        触发条件: 足以重构人物人生认知、改变心理结构的事件
        典型场景:
        1. 顶级创伤（全家死亡、战友全灭）: Y值瞬间抬高
        2. 重大救赎（获得唯一希望、被深度接纳）: Y值瞬间回落至健康基线
        3. 底线触碰（珍视之人被伤害）: Y值瞬间冲高
        """
        old_y = self.state.current_y

        if event_type == "trauma":
            # 顶级创伤 - Y值冲高
            new_y = min(self.config.max_y, self.state.baseline_y + 15 * intensity)
        elif event_type == "redemption":
            # 重大救赎 - Y值回落至健康基线
            new_y = max(self.config.min_y, self.state.baseline_y - 10)
        elif event_type == "bottom_line":
            # 底线触碰 - Y值冲高
            new_y = min(self.config.max_y, self.state.baseline_y + 20 * intensity)
        else:
            new_y = old_y

        self._apply_transition(new_y, TriggerType.MAJOR_EVENT, {
            "event_type": event_type,
            "intensity": intensity
        }, compensation_type)

        return TriggerResult(
            triggered=True,
            trigger_type=TriggerType.MAJOR_EVENT,
            old_y=old_y,
            new_y=new_y,
            delta_y=new_y - old_y,
            message=f"重大事件触发 [{event_type}]: Y值从{old_y}跃迁至{new_y}"
        )

    def trigger_emotional_extreme(self, emotion_type: str, compensation_type: Optional[CompensationType] = None) -> TriggerResult:
        """
        情绪极限触发

        触发条件: 极致愧疚、极致愤怒、极致逆反
        特性: 突破自身意识控制，Y值瞬间冲高

        参数:
        - emotion_type: 情绪类型
        - compensation_type: 补偿类型（自我麻痹或依恋填补等）
        """
        old_y = self.state.current_y

        # 情绪极限触发，Y值冲向极高
        new_y = min(self.config.max_y, 95)

        # 根据情绪类型确定补偿类型
        if compensation_type is None:
            if emotion_type in ["guilt", "shame", "remorse"]:
                compensation_type = CompensationType.GUILT_EXPLOSION
            elif emotion_type in ["numb", "denial", "escape"]:
                compensation_type = CompensationType.SELF_NARCOTIZATION
            elif emotion_type in ["attachment", "longing", "dependence"]:
                compensation_type = CompensationType.ATTACHMENT_FILLING

        self._apply_transition(new_y, TriggerType.EMOTIONAL_EXTREME, {
            "emotion_type": emotion_type
        }, compensation_type)

        return TriggerResult(
            triggered=True,
            trigger_type=TriggerType.EMOTIONAL_EXTREME,
            old_y=old_y,
            new_y=new_y,
            delta_y=new_y - old_y,
            message=f"情绪极限触发 [{emotion_type}]: Y值从{old_y}跃迁至{new_y}"
        )

    def _apply_transition(self, new_y: int, trigger_type: TriggerType, context: Dict, compensation_type: Optional[CompensationType] = None):
        """应用Y值跃迁"""
        old_y = self.state.current_y
        self.state.current_y = max(self.config.min_y, min(self.config.max_y, new_y))
        self.state.is_compensating = True
        self.state.compensation_type = compensation_type
        self.state.compensation_remaining = self.config.compensation_duration

        self.state.trigger_history.append({
            "type": trigger_type.value,
            "old_y": old_y,
            "new_y": new_y,
            "context": context,
            "compensation_type": compensation_type.value if compensation_type else None
        })

    def process_compensation(self) -> bool:
        """
        处理补偿机制
        补偿机制: 不是恢复，是心理缓冲，持续时间短（1~3个剧情节点）

        4种补偿类型:
        1. 被击穿后补偿(BREAKTHROUGH_COMP): Y值临时下降后回升
        2. 愧疚爆发补偿(GUILT_EXPLOSION): Y值冲高后缓慢回落
        3. 自我麻痹补偿(SELF_NARCOTIZATION): Y值被压制到低位
        4. 依恋填补补偿(ATTACHMENT_FILLING): Y值围绕基线波动
        """
        if self.state.is_compensating and self.state.compensation_remaining > 0:
            # 根据补偿类型应用不同的处理
            if self.state.compensation_type == CompensationType.BREAKTHROUGH_COMP:
                # 被击穿后: Y值暂时降低，结束时回弹
                pass  # 由回弹机制处理
            elif self.state.compensation_type == CompensationType.GUILT_EXPLOSION:
                # 愧疚爆发: Y值保持高位，缓慢下降
                if self.state.compensation_remaining > 1:
                    self.state.current_y = max(self.state.baseline_y, self.state.current_y - 2)
            elif self.state.compensation_type == CompensationType.SELF_NARCOTIZATION:
                # 自我麻痹: Y值被压制到低位
                self.state.current_y = max(1, self.state.current_y - 1)
            elif self.state.compensation_type == CompensationType.ATTACHMENT_FILLING:
                # 依恋填补: Y值围绕基线波动
                diff = self.state.baseline_y - self.state.current_y
                self.state.current_y += int(diff * 0.1)

            self.state.compensation_remaining -= 1

            if self.state.compensation_remaining == 0:
                self.state.is_compensating = False
                self.state.compensation_type = None
                return True  # 补偿结束，触发回弹

        return False

    def process_rebound(self) -> int:
        """
        处理回弹机制
        回弹机制: 确保Y值不会长期偏离人格本质，回归自身基线
        """
        if not self.state.is_compensating:
            # 逐步向基线回归
            diff = self.state.baseline_y - self.state.current_y
            if abs(diff) > 1:
                step = int(diff * self.config.rebound_rate)
                self.state.current_y += step if step != 0 else (1 if diff > 0 else -1)

        return self.state.current_y

    def set_baseline(self, baseline: int):
        """设置人物基线Y值"""
        self.state.baseline_y = max(self.config.min_y, min(self.config.max_y, baseline))

    def get_influence_level(self, target_y: int) -> str:
        """
        获取对目标的影响力等级

        返回:
        - "压倒性": ΔY ≥ 30
        - "强": 20 ≤ ΔY < 30
        - "中等": 10 ≤ ΔY < 20
        - "微弱": 5 ≤ ΔY < 10
        - "无影响": ΔY < 5
        """
        delta = self.state.current_y - target_y

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

    def get_state_report(self) -> Dict:
        """获取Y值状态报告"""
        return {
            "current_y": self.state.current_y,
            "baseline_y": self.state.baseline_y,
            "is_compensating": self.state.is_compensating,
            "compensation_type": self.state.compensation_type.value if self.state.compensation_type else None,
            "compensation_remaining": self.state.compensation_remaining,
            "threshold": self.get_threshold(),
            "trigger_count": len(self.state.trigger_history),
            "recent_triggers": self.state.trigger_history[-3:] if self.state.trigger_history else []
        }


def create_y_value_system(base_y: int = 50) -> YValueSystem:
    """工厂函数：创建Y值系统"""
    config = YValueConfig(base_y=base_y)
    return YValueSystem(config)