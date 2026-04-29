"""
MBTI System - 人格类型权重系统

MBTI定义:
- MBTI = 人物「人格骨架」(固定不变)
- 由SillyTavern人物卡的性格标签自动映射生成

MBTI决定:
1. 人物的基础心理模式(如INTJ的理性、内耗, INFP的敏感、共情)
2. Y值跃迁后的回弹基线(不同MBTI有固定的"健康稳定区间")
3. 对事件的反应倾向(如创伤者的防御模式、常人的应对逻辑)

Big Five映射:
- Openness -> 开放性
- Conscientiousness -> 尽责性
- Extraversion -> 外向性
- Agreeableness -> 宜人性
- Neuroticism -> 神经质(情绪稳定性)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class MBTIType(Enum):
    """16种MBTI人格类型"""
    INTJ = "INTJ"   # 建筑师
    INTP = "INTP"   # 逻辑学家
    ENTJ = "ENTJ"   # 指挥官
    ENTP = "ENTP"   # 辩论家
    INFJ = "INFJ"   # 倡导者
    INFP = "INFP"   # 调停者
    ENFJ = "ENFJ"   # 主人公
    ENFP = "ENFP"   # 竞选者
    ISTJ = "ISTJ"   # 物流师
    ISFJ = "ISFJ"   # 守护者
    ESTJ = "ESTJ"   # 总经理
    ESFJ = "ESFJ"   # 执政官
    ISTP = "ISTP"   # 鉴赏家
    ISFP = "ISFP"   # 探险家
    ESTP = "ESTP"   # 企业家
    ESFP = "ESFP"   # 表演者


@dataclass
class BigFiveTraits:
    """Big Five大五人格特质"""
    openness: float = 0.5           # 开放性 [0-1]
    conscientiousness: float = 0.5  # 尽责性 [0-1]
    extraversion: float = 0.5        # 外向性 [0-1]
    agreeableness: float = 0.5      # 宜人性 [0-1]
    neuroticism: float = 0.5        # 神经质/情绪不稳定性 [0-1]

    def to_dict(self) -> Dict[str, float]:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism
        }


@dataclass
class MBTIWeights:
    """MBTI权重配置"""
    primary_dimension: str           # E/I
    sensing_intuition: str           # S/N
    thinking_feeling: str            # T/F
    judging_perceiving: str          # J/P
    base_y_offset: int = 0           # Y值基线偏移
    emotional_stability: float = 0.5 # 情绪稳定性
    response_tendency: Dict[str, float] = field(default_factory=dict)


class MBTISystem:
    """
    MBTI系统 - 人格类型权重核心

    核心功能:
    1. 16种人格类型的权重定义
    2. Big Five特质映射
    3. Y值回弹基线计算
    4. 心理模式与反应倾向
    """

    # 16种MBTI类型的完整权重配置
    MBTI_CONFIGS: Dict[str, MBTIWeights] = {
        "INTJ": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="N",
            thinking_feeling="T",
            judging_perceiving="J",
            base_y_offset=5,
            emotional_stability=0.7,
            response_tendency={
                "rational_analysis": 0.9,
                "emotional_suppression": 0.7,
                "independence": 0.95,
                "perfectionism": 0.85
            }
        ),
        "INTP": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="N",
            thinking_feeling="T",
            judging_perceiving="P",
            base_y_offset=3,
            emotional_stability=0.6,
            response_tendency={
                "logical_analysis": 0.95,
                "emotional_detachment": 0.8,
                "curiosity": 0.9,
                "introversion": 0.9
            }
        ),
        "ENTJ": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="N",
            thinking_feeling="T",
            judging_perceiving="J",
            base_y_offset=8,
            emotional_stability=0.65,
            response_tendency={
                "leadership": 0.95,
                "decisiveness": 0.9,
                "assertiveness": 0.9,
                "confidence": 0.85
            }
        ),
        "ENTP": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="N",
            thinking_feeling="T",
            judging_perceiving="P",
            base_y_offset=6,
            emotional_stability=0.55,
            response_tendency={
                "creativity": 0.95,
                "debate": 0.85,
                "adaptability": 0.9,
                "enthusiasm": 0.8
            }
        ),
        "INFJ": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="N",
            thinking_feeling="F",
            judging_perceiving="J",
            base_y_offset=4,
            emotional_stability=0.45,
            response_tendency={
                "empathy": 0.95,
                "idealism": 0.9,
                "sensitivity": 0.85,
                "insight": 0.9
            }
        ),
        "INFP": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="N",
            thinking_feeling="F",
            judging_perceiving="P",
            base_y_offset=2,
            emotional_stability=0.4,
            response_tendency={
                "values_alignment": 0.95,
                "sensitivity": 0.9,
                "introversion": 0.85,
                "idealism": 0.85
            }
        ),
        "ENFJ": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="N",
            thinking_feeling="F",
            judging_perceiving="J",
            base_y_offset=5,
            emotional_stability=0.5,
            response_tendency={
                "charisma": 0.95,
                "harmony": 0.9,
                "responsibility": 0.85,
                "inspiration": 0.9
            }
        ),
        "ENFP": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="N",
            thinking_feeling="F",
            judging_perceiving="P",
            base_y_offset=3,
            emotional_stability=0.45,
            response_tendency={
                "enthusiasm": 0.95,
                "creativity": 0.9,
                "social_energy": 0.85,
                "spontaneity": 0.85
            }
        ),
        "ISTJ": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="S",
            thinking_feeling="T",
            judging_perceiving="J",
            base_y_offset=4,
            emotional_stability=0.75,
            response_tendency={
                "reliability": 0.95,
                "practicality": 0.9,
                "tradition": 0.85,
                "stability": 0.9
            }
        ),
        "ISFJ": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="S",
            thinking_feeling="F",
            judging_perceiving="J",
            base_y_offset=3,
            emotional_stability=0.65,
            response_tendency={
                "loyalty": 0.95,
                "care": 0.9,
                "practicality": 0.85,
                "responsibility": 0.9
            }
        ),
        "ESTJ": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="S",
            thinking_feeling="T",
            judging_perceiving="J",
            base_y_offset=6,
            emotional_stability=0.7,
            response_tendency={
                "organization": 0.95,
                "leadership": 0.9,
                "dependability": 0.9,
                "tradition": 0.85
            }
        ),
        "ESFJ": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="S",
            thinking_feeling="F",
            judging_perceiving="J",
            base_y_offset=4,
            emotional_stability=0.6,
            response_tendency={
                "harmony": 0.95,
                "social_responsibility": 0.9,
                "generosity": 0.85,
                "popularity": 0.85
            }
        ),
        "ISTP": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="S",
            thinking_feeling="T",
            judging_perceiving="P",
            base_y_offset=3,
            emotional_stability=0.7,
            response_tendency={
                "practicality": 0.95,
                "problem_solving": 0.9,
                "independence": 0.85,
                "spontaneity": 0.8
            }
        ),
        "ISFP": MBTIWeights(
            primary_dimension="I",
            sensing_intuition="S",
            thinking_feeling="F",
            judging_perceiving="P",
            base_y_offset=2,
            emotional_stability=0.5,
            response_tendency={
                "aesthetics": 0.95,
                "sensitivity": 0.9,
                "flexibility": 0.85,
                "loyalty": 0.85
            }
        ),
        "ESTP": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="S",
            thinking_feeling="T",
            judging_perceiving="P",
            base_y_offset=4,
            emotional_stability=0.6,
            response_tendency={
                "action_oriented": 0.95,
                "social_skills": 0.9,
                "pragmatism": 0.9,
                "adaptability": 0.85
            }
        ),
        "ESFP": MBTIWeights(
            primary_dimension="E",
            sensing_intuition="S",
            thinking_feeling="F",
            judging_perceiving="P",
            base_y_offset=3,
            emotional_stability=0.5,
            response_tendency={
                "spontaneity": 0.95,
                "social_energy": 0.9,
                "optimism": 0.9,
                "aesthetics": 0.8
            }
        ),
    }

    # Big Five特质到MBTI维度的映射
    BIG_FIVE_TO_MBTI: Dict[str, Tuple[str, float]] = {
        # Openness
        "creative": ("N", 0.8),
        "curious": ("N", 0.7),
        "conventional": ("S", 0.6),
        "practical": ("S", 0.5),
        # Conscientiousness
        "organized": ("J", 0.8),
        "disciplined": ("J", 0.7),
        "spontaneous": ("P", 0.6),
        "flexible": ("P", 0.5),
        # Extraversion
        "outgoing": ("E", 0.9),
        "energetic": ("E", 0.7),
        "reserved": ("I", 0.8),
        "solitary": ("I", 0.7),
        # Agreeableness
        "cooperative": ("F", 0.8),
        "empathetic": ("F", 0.7),
        "competitive": ("T", 0.6),
        "challenging": ("T", 0.5),
        # Neuroticism (inverse)
        "stable": ("stable", 0.7),
        "anxious": ("neurotic", 0.6),
    }

    def __init__(self, mbti_type: Optional[str] = None):
        self.mbti_type = mbti_type or "INTJ"
        self.weights = self.MBTI_CONFIGS.get(self.mbti_type)
        self.big_five = self._derive_big_five()

    def _derive_big_five(self) -> BigFiveTraits:
        """从MBTI派生Big Five特质"""
        weights = self.weights

        # E/I -> Extraversion
        extraversion = 0.8 if weights.primary_dimension == "E" else 0.2

        # S/N -> Openness (反向)
        openness = 0.3 if weights.sensing_intuition == "S" else 0.8

        # T/F -> Agreeableness (与情感正相关)
        agreeableness = 0.7 if weights.thinking_feeling == "F" else 0.4

        # J/P -> Conscientiousness
        conscientiousness = 0.75 if weights.judging_perceiving == "J" else 0.35

        # 情绪稳定性由MBTI类型决定
        neuroticism = 1.0 - weights.emotional_stability

        return BigFiveTraits(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=extraversion,
            agreeableness=agreeableness,
            neuroticism=neuroticism
        )

    def get_baseline_y(self, base_y: int = 50) -> int:
        """
        获取该人格类型的Y值基线
        不同MBTI有固定的"健康稳定区间"
        """
        return base_y + self.weights.base_y_offset

    def get_rebound_range(self) -> Tuple[int, int]:
        """
        获取回弹区间
        Y值跃迁后的回弹基线范围
        """
        base = 50 + self.weights.base_y_offset
        return (base - 10, base + 10)

    def calculate_emotional_weight(self, emotion: str) -> float:
        """
        计算情绪权重
        用于MBTI权重计算时的情绪强度参考
        """
        base = 1.0

        # 根据神经质调整
        if emotion in ["fear", "anxiety", "worry"]:
            base *= (1 + self.big_five.neuroticism * 0.5)
        elif emotion in ["joy", "happiness", "excitement"]:
            base *= (1 + self.big_five.extraversion * 0.3)

        return min(base, 2.0)

    def get_response_tendency(self, tendency_key: str) -> float:
        """获取特定反应倾向的权重"""
        return self.weights.response_tendency.get(tendency_key, 0.5)

    def get_reaction_style(self) -> str:
        """
        获取反应风格描述

        根据MBTI维度返回反应风格:
        - I: 内向型,需要独处时间消化
        - E: 外向型,通过社交获得能量
        - S: 务实型,关注具体细节
        - N: 直觉型,关注可能性和模式
        - T: 理性型,基于逻辑做决定
        - F: 情感型,基于价值观做决定
        - J: 判断型,喜欢计划和结构
        - P: 知觉型,喜欢灵活和开放
        """
        styles = []

        if self.weights.primary_dimension == "I":
            styles.append("内向型(需要独处时间)")
        else:
            styles.append("外向型(通过社交获得能量)")

        if self.weights.sensing_intuition == "S":
            styles.append("务实型(关注具体细节)")
        else:
            styles.append("直觉型(关注可能性和模式)")

        if self.weights.thinking_feeling == "T":
            styles.append("理性型(基于逻辑决策)")
        else:
            styles.append("情感型(基于价值观决策)")

        if self.weights.judging_perceiving == "J":
            styles.append("判断型(喜欢计划结构)")
        else:
            styles.append("知觉型(喜欢灵活开放)")

        return ", ".join(styles)

    @classmethod
    def from_tags(cls, tags: List[str]) -> "MBTISystem":
        """
        从SillyTavern标签自动映射MBTI

        标签格式: ["理性", "内耗", "独立", "完美主义"] -> INTJ
        """
        # 简化的标签映射
        tag_patterns = {
            "INTJ": ["理性", "内耗", "独立", "完美主义", "战略"],
            "INTP": ["逻辑", "分析", "好奇", "抽象", "冷淡"],
            "ENTJ": ["领导", "果断", "自信", "指挥", "强势"],
            "ENTP": ["创意", "辩论", "机智", "多变", "挑战"],
            "INFJ": ["共情", "理想", "敏感", "洞察", "神秘"],
            "INFP": ["敏感", "共情", "理想", "浪漫", "内敛"],
            "ENFJ": ["魅力", "领导", "热情", "关怀", "说服"],
            "ENFP": ["热情", "创意", "自由", "激励", "多变"],
            "ISTJ": ["可靠", "务实", "传统", "负责", "稳定"],
            "ISFJ": ["忠诚", "关怀", "务实", "责任", "守护"],
            "ESTJ": ["组织", "传统", "负责", "管理", "务实"],
            "ESFJ": ["和谐", "社交", "关怀", "热情", "传统"],
            "ISTP": ["务实", "灵活", "动手", "冷静", "分析"],
            "ISFP": ["敏感", "艺术", "灵活", "温柔", "审美"],
            "ESTP": ["行动", "社交", "务实", "适应", "活力"],
            "ESFP": ["活力", "社交", "自发", "乐观", "表演"],
        }

        max_score = 0
        best_type = "UNKNOWN"

        for mbti_type, patterns in tag_patterns.items():
            score = sum(1 for tag in tags for pattern in patterns if pattern in tag)
            if score > max_score:
                max_score = score
                best_type = mbti_type

        return cls(mbti_type=best_type)

    def get_full_profile(self) -> Dict:
        """获取完整的人格档案"""
        return {
            "mbti_type": self.mbti_type,
            "type_name": self._get_type_name(),
            "dimensions": {
                "primary": self.weights.primary_dimension,
                "sensing_intuition": self.weights.sensing_intuition,
                "thinking_feeling": self.weights.thinking_feeling,
                "judging_perceiving": self.weights.judging_perceiving
            },
            "big_five": self.big_five.to_dict(),
            "baseline_y": self.get_baseline_y(),
            "rebound_range": self.get_rebound_range(),
            "reaction_style": self.get_reaction_style(),
            "response_tendencies": self.weights.response_tendency
        }

    def _get_type_name(self) -> str:
        """获取MBTI类型名称"""
        names = {
            "INTJ": "建筑师", "INTP": "逻辑学家", "ENTJ": "指挥官", "ENTP": "辩论家",
            "INFJ": "倡导者", "INFP": "调停者", "ENFJ": "主人公", "ENFP": "竞选者",
            "ISTJ": "物流师", "ISFJ": "守护者", "ESTJ": "总经理", "ESFJ": "执政官",
            "ISTP": "鉴赏家", "ISFP": "探险家", "ESTP": "企业家", "ESFP": "表演者"
        }
        return names.get(self.mbti_type, "未知")


def create_mbti_system(mbti_type: str) -> MBTISystem:
    """工厂函数：创建MBTI系统"""
    return MBTISystem(mbti_type=mbti_type)