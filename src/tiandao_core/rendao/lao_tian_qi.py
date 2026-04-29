"""
LaoTianQi - 老天气变量系统

老天气是"老天爷"对人物行为的主观倾向评判系统

核心功能:
1. 主观倾向评判
2. 行为价值评估
3. 权重调整建议
4. 冲突检测

老天气原则:
- 天道损有余而补不足
- 老天气监控"人道"的运行
- 不直接干预，但会通过"暗示"影响角色
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum


class ActionValue(Enum):
    """行为价值等级"""
    HIGHLY_VALUABLE = "highly_valuable"     # 非常有价值
    VALUABLE = "valuable"                   # 有价值
    NEUTRAL = "neutral"                     # 中性
    WORTHLESS = "worthless"                 # 无价值
    HARMFUL = "harmful"                     # 有害


class ConflictVariable(Enum):
    """冲突变量类型"""
    PERSONAL_FATE = "personal_fate"         # 个人与命运
    REALITY_FICTION = "reality_fiction"     # 真实与虚构
    EMOTION_DUTY = "emotion_duty"           # 情感与责任
    PAST_PRESENT = "past_present"           # 过去与现在


@dataclass
class LaoTianQiJudgment:
    """老天气评判结果"""
    action_value: ActionValue
    weight_suggestion: int                  # 权重变化建议
    message: str
    conflict_hints: List[str] = field(default_factory=list)
    is_breaking_point: bool = False         # 是否是突破点


class LaoTianQi:
    """
    老天气变量 - 天道对人事的主观评判

    核心功能:
    1. 评判人物行为是否符合"天道"
    2. 提供权重调整建议
    3. 检测冲突升级潜力
    4. 生成老天爷的"暗示"
    """

    # 行为价值阈值
    VALUE_THRESHOLDS = {
        ActionValue.HIGHLY_VALUABLE: 0.8,
        ActionValue.VALUABLE: 0.5,
        ActionValue.NEUTRAL: 0.2,
        ActionValue.WORTHLESS: -0.3,
        ActionValue.HARMFUL: -0.6,
    }

    # 冲突变量配置
    CONFLICT_VARIABLES: Dict[ConflictVariable, Dict] = {
        ConflictVariable.PERSONAL_FATE: {
            "keywords": ["命运", "预言", "注定", "无法改变", "宿命"],
            "weight": 0.7,
        },
        ConflictVariable.REALITY_FICTION: {
            "keywords": ["真实", "虚假", "记忆", "身份", "存在"],
            "weight": 0.6,
        },
        ConflictVariable.EMOTION_DUTY: {
            "keywords": ["责任", "牺牲", "大义", "爱情", "忠诚"],
            "weight": 0.8,
        },
        ConflictVariable.PAST_PRESENT: {
            "keywords": ["过去", "创伤", "回忆", "秘密", "真相"],
            "weight": 0.65,
        },
    }

    def __init__(self):
        self.judgment_history: List[LaoTianQiJudgment] = []
        self.active_conflicts: Set[ConflictVariable] = set()
        self.breaking_points: List[str] = []

    def evaluate_action(
        self,
        action: str,
        character_mbti: str,
        character_y: int,
        context: Optional[Dict] = None
    ) -> LaoTianQiJudgment:
        """
        评估行为价值

        参数:
        - action: 行为描述
        - character_mbti: 角色MBTI
        - character_y: 角色Y值
        - context: 额外上下文
        """
        action_lower = action.lower()

        # 计算基础价值
        value_score = self._calculate_value_score(action_lower, character_mbti, character_y)

        # 确定价值等级
        action_value = self._get_value_level(value_score)

        # 计算权重建议
        weight_suggestion = self._calculate_weight_suggestion(action_value, value_score)

        # 检测冲突
        conflict_hints = self._detect_conflicts(action_lower)

        # 检查是否是突破点
        is_breaking_point = self._check_breaking_point(action_value, character_y, conflict_hints)

        # 生成老天气消息
        message = self._generate_message(action_value, action, character_mbti, conflict_hints)

        judgment = LaoTianQiJudgment(
            action_value=action_value,
            weight_suggestion=weight_suggestion,
            conflict_hints=conflict_hints,
            message=message,
            is_breaking_point=is_breaking_point
        )

        self.judgment_history.append(judgment)

        if is_breaking_point:
            self.breaking_points.append(action[:50])

        return judgment

    def _calculate_value_score(
        self,
        action: str,
        mbti: str,
        y_value: int
    ) -> float:
        """
        计算行为价值分数 [-1, 1]

        正值: 符合天道
        负值: 违背天道
        """
        score = 0.0

        # 高价值关键词
        valuable_keywords = [
            "帮助", "保护", "拯救", "牺牲", "奉献", "正直", "诚实",
            "勇敢", "担当", "成长", "突破", "觉悟", "觉醒"
        ]

        # 低价值关键词
        worthless_keywords = [
            "背叛", "欺骗", "伤害", "自私", "懦弱", "逃避",
            "放弃", "沉沦", "堕落", "疯狂", "毁灭"
        ]

        for keyword in valuable_keywords:
            if keyword in action:
                score += 0.15

        for keyword in worthless_keywords:
            if keyword in action:
                score -= 0.2

        # MBTI适配调整
        if mbti in ["INTJ", "ENTJ", "INFJ", "ENFJ"]:
            # 理性/理想型角色，更看重原则
            if "原则" in action or "底线" in action:
                score += 0.1
        elif mbti in ["INFP", "ENFP", "ISFP", "ESFP"]:
            # 情感型角色，更看重情感
            if "情感" in action or "爱" in action:
                score += 0.1

        # Y值影响
        if y_value >= 70:
            # 高Y值角色更倾向于承担重要行为
            if "责任" in action or "担当" in action:
                score += 0.1
        elif y_value < 40:
            # 低Y值角色更容易被判定为消极
            if "逃避" in action or "放弃" in action:
                score -= 0.1

        return max(-1.0, min(1.0, score))

    def _get_value_level(self, score: float) -> ActionValue:
        """根据分数确定价值等级"""
        if score >= self.VALUE_THRESHOLDS[ActionValue.HIGHLY_VALUABLE]:
            return ActionValue.HIGHLY_VALUABLE
        elif score >= self.VALUE_THRESHOLDS[ActionValue.VALUABLE]:
            return ActionValue.VALUABLE
        elif score >= self.VALUE_THRESHOLDS[ActionValue.NEUTRAL]:
            return ActionValue.NEUTRAL
        elif score >= self.VALUE_THRESHOLDS[ActionValue.WORTHLESS]:
            return ActionValue.WORTHLESS
        else:
            return ActionValue.HARMFUL

    def _calculate_weight_suggestion(
        self,
        action_value: ActionValue,
        value_score: float
    ) -> int:
        """计算权重变化建议"""
        base_changes = {
            ActionValue.HIGHLY_VALUABLE: 8,
            ActionValue.VALUABLE: 3,
            ActionValue.NEUTRAL: 0,
            ActionValue.WORTHLESS: -6,
            ActionValue.HARMFUL: -10,
        }

        base = base_changes[action_value]

        # 根据精确分数调整
        fine_tune = int(value_score * 2)

        return base + fine_tune

    def _detect_conflicts(self, action: str) -> List[str]:
        """检测冲突变量"""
        detected = []

        for conflict_type, config in self.CONFLICT_VARIABLES.items():
            for keyword in config["keywords"]:
                if keyword in action:
                    detected.append(f"{conflict_type.value}: 触发{keyword}")
                    self.active_conflicts.add(conflict_type)
                    break

        return detected

    def _check_breaking_point(
        self,
        action_value: ActionValue,
        y_value: int,
        conflict_hints: List[str]
    ) -> bool:
        """
        检查是否是突破点

        突破点条件:
        - 高价值行为且Y值在合适区间
        - 触发多个冲突变量
        """
        breaking_conditions = 0

        if action_value == ActionValue.HIGHLY_VALUABLE and y_value >= 50:
            breaking_conditions += 1

        if len(conflict_hints) >= 2:
            breaking_conditions += 1

        if action_value == ActionValue.HARMFUL and y_value < 40:
            breaking_conditions += 1

        return breaking_conditions >= 2

    def _generate_message(
        self,
        action_value: ActionValue,
        action: str,
        mbti: str,
        conflict_hints: List[str]
    ) -> str:
        """生成老天气评判消息"""
        messages = {
            ActionValue.HIGHLY_VALUABLE: [
                "此子有大气运加身",
                "天道酬勤，此人得之",
                "天命所归，势不可挡",
            ],
            ActionValue.VALUABLE: [
                "不错，符合天道",
                "善，有可取之处",
                "顺势而为，明智之举",
            ],
            ActionValue.NEUTRAL: [
                "平常之事，无功无过",
                "不过不失",
                "静观其变",
            ],
            ActionValue.WORTHLESS: [
                "此为下策，损有余而补不足",
                "背道而驰，自取其辱",
                "逆天而行，难以为继",
            ],
            ActionValue.HARMFUL: [
                "大凶之兆，自取灭亡",
                "天理不容，必遭天谴",
                "此路不通，回头是岸",
            ],
        }

        base_messages = messages[action_value]
        # 天道不允许随机，所有选择基于字符特征码确定性选择
        # 确保同一条件始终产生同一结果
        char_seed = sum(ord(c) for c in mbti) if mbti else 0
        index = char_seed % len(base_messages)
        selected = base_messages[index]

        if conflict_hints:
            selected += f" (检测到冲突: {len(conflict_hints)})"

        return selected

    def get_active_conflicts(self) -> List[str]:
        """获取当前活跃的冲突变量"""
        return [c.value for c in self.active_conflicts]

    def get_judgment_summary(self) -> Dict:
        """获取评判摘要"""
        if not self.judgment_history:
            return {"total_judgments": 0}

        value_counts = {}
        for j in self.judgment_history:
            value_counts[j.action_value.value] = value_counts.get(j.action_value.value, 0) + 1

        return {
            "total_judgments": len(self.judgment_history),
            "value_distribution": value_counts,
            "active_conflicts": self.get_active_conflicts(),
            "breaking_points_count": len(self.breaking_points),
            "recent_breaking_points": self.breaking_points[-3:] if self.breaking_points else []
        }


def create_lao_tian_qi() -> LaoTianQi:
    """工厂函数：创建老天气系统"""
    return LaoTianQi()