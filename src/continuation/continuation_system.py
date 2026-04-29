"""
Continuation System - 续写系统

核心原则：
1. 基于角色画像生成行为（MBTI/Y值/欲望/情绪）
2. 基于蝴蝶效应传导影响
3. 老天爷变量作为主观评判
4. 不允许AI自由发挥

续写流程：
1. 加载当前章节角色状态
2. 构建续写提示词（含天道原则约束）
3. AI生成下一章
4. 自检一致性
5. 应用蝴蝶效应
6. 更新角色状态
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from tiandao_core.core.profile import CharacterProfile
from tiandao_core.core.y_value import YValueSystem, TriggerType
from tiandao_core.rendao.weight_network import WeightNetwork, CharacterClass
from tiandao_core.rendao.lao_tian_qi import LaoTianQi, ActionValue
from tiandao_core.rendao.butterfly_effect import ButterflyEffectSystem, Position3D


@dataclass
class ContinuationContext:
    """续写上下文"""
    world_name: str
    world_description: str
    current_chapter: str
    chapter_summary: str
    characters: List[CharacterProfile] = field(default_factory=list)
    recent_events: List[Dict] = field(default_factory=list)


@dataclass
class ContinuationResult:
    """续写结果"""
    content: str
    character_states: Dict[str, Dict] = field(default_factory=dict)
    y_value_changes: Dict[str, Tuple[int, int]] = field(default_factory=dict)  # name -> (old, new)
    triggered_events: List[str] = field(default_factory=list)
    lao_tian_qi_judgments: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=datetime.now().isoformat)


class ContinuationSystem:
    """
    续写系统

    基于天道/人道系统的智能续写
    """

    def __init__(self, api=None):
        self.api = api
        self.weight_network = WeightNetwork()
        self.lao_tian_qi = LaoTianQi()
        self.butterfly_effect = ButterflyEffectSystem()
        self.continuation_history: List[ContinuationResult] = []

    def prepare_context(
        self,
        world_data: Dict,
        character_profiles: List[Dict],
        current_chapter: str,
        recent_events: List[Dict] = None
    ) -> ContinuationContext:
        """
        准备续写上下文
        """
        # 注册角色到权重网络
        for char_data in character_profiles:
            char_class = self._infer_character_class(char_data)
            self.weight_network.register_character(
                name=char_data.get("name", "未知"),
                character_class=char_class,
                custom_weight=char_data.get("weight", 50)
            )

            # 注册到蝴蝶效应系统
            position = char_data.get("position", [0, 0, 0])
            self.butterfly_effect.register_character(
                name=char_data.get("name", "未知"),
                y_value=char_data.get("current_y", 50),
                position=Position3D(x=position[0], y=position[1], z=position[2]),
                weight=char_data.get("weight", 50),
                mbti=char_data.get("mbti", "INTJ")
            )

        return ContinuationContext(
            world_name=world_data.get("name", "通用"),
            world_description=json.dumps(world_data, ensure_ascii=False),
            current_chapter=current_chapter,
            chapter_summary="",
            characters=[self._dict_to_profile(c) for c in character_profiles],
            recent_events=recent_events or []
        )

    def _infer_character_class(self, char_data: Dict) -> CharacterClass:
        """从角色数据推断分类"""
        weight = char_data.get("weight", 50)
        if weight >= 85:
            return CharacterClass.PROTAGONIST
        elif weight >= 60:
            return CharacterClass.MAIN
        elif weight >= 40:
            return CharacterClass.SECONDARY
        else:
            return CharacterClass.NPC

    def _dict_to_profile(self, char_data: Dict) -> CharacterProfile:
        """将字典转换为CharacterProfile"""
        from tiandao_core.adapters.character_card import CharacterCardAdapter
        return CharacterCardAdapter.from_tiandao_format(char_data)

    def generate_continuation(
        self,
        context: ContinuationContext,
        user_input: str = "",
        max_length: int = 2000
    ) -> ContinuationResult:
        """
        生成续写
        """
        if self.api is None:
            return ContinuationResult(
                content="【错误】未配置AI API",
                character_states={},
                y_value_changes={},
                triggered_events=[],
                lao_tian_qi_judgments=[]
            )

        # 构建角色画像字符串
        character_profiles_str = self._build_character_profiles(context.characters)

        # 调用AI续写
        content = self.api.write_continue(
            context=user_input or context.current_chapter,
            world_info=context.world_description,
            character_profiles=character_profiles_str,
            genre=context.world_name
        )

        # 评估续写内容
        result = ContinuationResult(content=content)

        # 应用天道系统评估
        for profile in context.characters:
            # 老天气评判
            judgment = self.lao_tian_qi.evaluate_action(
                action=content[:500],
                character_mbti=profile.info.mbti_type,
                character_y=profile.y_system.Y if profile.y_system else 50
            )

            result.lao_tian_qi_judgments.append({
                "character": profile.info.name,
                "action_value": judgment.action_value.value,
                "weight_suggestion": judgment.weight_suggestion,
                "message": judgment.message
            })

            # 权重调整
            if judgment.action_value in [ActionValue.HIGHLY_VALUABLE, ActionValue.VALUABLE]:
                delta = self.weight_network.calculate_delta(
                    profile.info.name, "valuable", 0.7
                )
            elif judgment.action_value == ActionValue.WORTHLESS:
                delta = self.weight_network.calculate_delta(
                    profile.info.name, "worthless", 0.7
                )
            elif judgment.action_value == ActionValue.HARMFUL:
                delta = self.weight_network.calculate_delta(
                    profile.info.name, "negative", 0.7
                )
            else:
                delta = 0

            if delta != 0:
                change = self.weight_network.apply_weight_change(
                    profile.info.name, delta, judgment.message
                )
                result.y_value_changes[profile.info.name] = (
                    change.old_weight, change.new_weight
                )

        # 蝴蝶效应检测
        physics_alerts = self.butterfly_effect.check_physics_theorems()
        result.triggered_events.extend(physics_alerts)

        # 保存历史
        self.continuation_history.append(result)

        return result

    def _build_character_profiles(self, profiles: List[CharacterProfile]) -> str:
        """构建角色画像描述字符串"""
        lines = []

        for profile in profiles:
            y_system = profile.y_system
            mbti_system = profile.mbti_system

            current_y = y_system.Y if y_system else profile.info.base_y
            baseline_y = y_system.state.baseline_y if y_system else profile.info.base_y

            mbti_info = mbti_system.get_full_profile() if mbti_system else {}

            # 情绪信息
            emotions = {}
            if profile.psychology:
                emotions = {
                    "joy": profile.psychology.seven_emotions.joy,
                    "anger": profile.psychology.seven_emotions.anger,
                    "worry": profile.psychology.seven_emotions.worry,
                    "sadness": profile.psychology.seven_emotions.sadness,
                    "fear": profile.psychology.seven_emotions.fear,
                }

            profile_str = f"""
【{profile.info.name}】
MBTI: {profile.info.mbti_type}
基础Y值: {profile.info.base_y}
当前Y值: {current_y}
Y值基线: {baseline_y}
性格: {mbti_info.get('reaction_style', '')}
情绪: {emotions}
当前状态: {profile.psychology.behavioral_tendency if profile.psychology else ''}
""".strip()

            lines.append(profile_str)

        return "\n\n".join(lines)

    def self_consistency_check(self, content: str, context: ContinuationContext) -> Dict:
        """
        自检一致性

        检查续写内容是否符合角色设定
        """
        issues = []

        for profile in context.characters:
            # 检查Y值一致性
            if profile.y_system and profile.y_system.Y < 40:
                # 低Y值角色不应该表现得太强势
                dominant_keywords = ["必须", "一定", "绝对", "命令", "指挥"]
                for keyword in dominant_keywords:
                    if keyword in content and profile.info.name in content:
                        issues.append(
                            f"{profile.info.name}(Y={profile.y_system.Y})表现过于强势"
                        )

            # 检查MBTI一致性
            if profile.mbti_system:
                mbti = profile.info.mbti_type
                if mbti in ["ISFJ", "ESFJ", "ISTJ", "ESTJ"]:
                    # 传统型角色不应该表现得太出格
                    pass

        return {
            "consistent": len(issues) == 0,
            "issues": issues
        }

    def get_continuation_history(self) -> List[ContinuationResult]:
        """获取续写历史"""
        return self.continuation_history

    def get_tiandao_summary(self) -> Dict:
        """获取天道系统摘要"""
        return {
            "weight_network": self.weight_network.get_network_summary(),
            "lao_tian_qi": self.lao_tian_qi.get_judgment_summary(),
            "butterfly_effect": self.butterfly_effect.get_effect_summary(),
            "continuation_count": len(self.continuation_history)
        }


def create_continuation_system(api=None) -> ContinuationSystem:
    """工厂函数：创建续写系统"""
    return ContinuationSystem(api=api)