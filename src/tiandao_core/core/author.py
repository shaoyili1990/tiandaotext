"""
Author Constraint System - 作者约束系统

作者哲学核心原则:
1. AI思维限制器
   - 禁止AI扮演上帝角色
   - 禁止全注意力机制
   - 角色动态认知

2. 群像创作思维
   - 角色去神性化
   - 角色去工具化
   - 群像暴走化

3. 冲突变量库
   - 个人与命运
   - 真实与虚构
   - 情感与责任
   - 过去与现在

4. 中医开方思维
   - 扶正固本
   - 调和阴阳
   - 脾肾同调
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum


class ConstraintType(Enum):
    """约束类型"""
    FORBIDDEN = "forbidden"           # 绝对禁止
    LIMITED = "limited"              # 有限制
    ENCOURAGED = "encouraged"        # 鼓励
    REQUIRED = "required"            # 必须


class ConflictType(Enum):
    """冲突类型"""
    PERSONAL_FATE = "personal_fate"       # 个人与命运
    REALITY_FICTION = "reality_fiction"   # 真实与虚构
    EMOTION_DUTY = "emotion_duty"        # 情感与责任
    PAST_PRESENT = "past_present"        # 过去与现在


@dataclass
class AuthorConstraint:
    """作者约束"""
    id: str
    type: ConstraintType
    description: str
    priority: int = 5                    # 优先级 [1-10]
    rationale: str = ""
    examples: List[str] = field(default_factory=list)


@dataclass
class ConflictVariable:
    """冲突变量"""
    conflict_type: ConflictType
    description: str
    activation_threshold: float = 0.5   # 激活阈值
    escalation_potential: float = 0.7   # 升级潜力
    resolution_hints: List[str] = field(default_factory=list)


@dataclass
class RoleConstraint:
    """角色约束配置"""
    can_fail: bool = True              # 允许失败
    can_be_wrong: bool = True           # 允许犯错
    can_not_know: bool = True           # 允许不知道
    allow_blanks: bool = True           # 允许有空白
    no_definition: bool = True          # 严禁下定义
    no_explanation: bool = True         # 禁止解说


@dataclass
class NarrativeMode(Enum):
    """叙事模式"""
    FIRST_PERSON = "first_person"       # 第一人称
    THIRD_PERSON = "third_person"        # 第三人称
    OMNISCIENT = "omniscient"            # 全知视角
    LIMITED = "limited"                  # 限制视角


class AuthorConstraintSystem:
    """
    作者约束系统 - 创作方法论核心

    核心功能:
    1. AI思维限制器管理
    2. 群像创作规则
    3. 冲突变量库
    4. 叙事模式控制
    5. 约束检查与验证
    """

    # 默认AI思维限制器
    DEFAULT_LIMITATIONS: List[AuthorConstraint] = [
        AuthorConstraint(
            id="no_god_role",
            type=ConstraintType.FORBIDDEN,
            description="禁止AI扮演上帝角色",
            priority=10,
            rationale="角色需要真实性和自主性",
            examples=["不允许角色无所不知", "不允许角色完美无缺"]
        ),
        AuthorConstraint(
            id="no_full_attention",
            type=ConstraintType.FORBIDDEN,
            description="禁止全注意力机制",
            priority=9,
            rationale="保持叙事节奏和真实感",
            examples=["不允许无意义的解说", "不允许暴露无关信息"]
        ),
        AuthorConstraint(
            id="allow_failure",
            type=ConstraintType.REQUIRED,
            description="必须允许角色存在失败的可能性",
            priority=8,
            rationale="真实的人物需要有缺点",
            examples=["允许角色能力不足", "允许角色认知偏差"]
        ),
        AuthorConstraint(
            id="no_definition",
            type=ConstraintType.FORBIDDEN,
            description="严禁下定义",
            priority=7,
            rationale="展示而非说明",
            examples=["不直接说明角色性格", "通过行为展现而非标签"]
        ),
        AuthorConstraint(
            id="allow_blanks",
            type=ConstraintType.ENCOURAGED,
            description="允许角色有空白的地方",
            priority=5,
            rationale="留白是艺术的一部分",
            examples=["不强行解释每个行为", "保持神秘感"]
        ),
    ]

    # 冲突变量库
    CONFLICT_VARIABLES: Dict[ConflictType, ConflictVariable] = {
        ConflictType.PERSONAL_FATE: ConflictVariable(
            conflict_type=ConflictType.PERSONAL_FATE,
            description="自由意志 vs 宿命/规则",
            activation_threshold=0.4,
            escalation_potential=0.8,
            resolution_hints=["预言的解读空间", "规则的可突破性", "个人选择的意义"]
        ),
        ConflictType.REALITY_FICTION: ConflictVariable(
            conflict_type=ConflictType.REALITY_FICTION,
            description="身份/现实感崩塌",
            activation_threshold=0.5,
            escalation_potential=0.9,
            resolution_hints=["记忆篡改的线索", "虚拟与真实的边界模糊", "身份认同危机"]
        ),
        ConflictType.EMOTION_DUTY: ConflictVariable(
            conflict_type=ConflictType.EMOTION_DUTY,
            description="个人幸福 vs 集体/使命",
            activation_threshold=0.3,
            escalation_potential=0.85,
            resolution_hints=["忠诚与爱情的冲突", "大义的代价", "牺牲对象的选择"]
        ),
        ConflictType.PAST_PRESENT: ConflictVariable(
            conflict_type=ConflictType.PAST_PRESENT,
            description="创伤/秘密影响当下",
            activation_threshold=0.4,
            escalation_potential=0.75,
            resolution_hints=["旧怨的浮现", "未解心结的爆发", "历史真相揭露"]
        ),
    }

    # 冲突升级层次
    CONFLICT_ESCALATION = {
        "personal": {
            "range": "内心、单关系、能力与目标差距",
            "variables": ["价值观冲突", "单人对决", "能力不足"]
        },
        "social": {
            "range": "规则、权力、理念",
            "variables": ["违律", "站队", "派系斗争", "舆论"]
        },
        "world": {
            "range": "存在、秩序、意义",
            "variables": ["生存威胁", "规则重写", "存在意义追问"]
        }
    }

    def __init__(self):
        self.limitations: Dict[str, AuthorConstraint] = {}
        self.role_constraints = RoleConstraint()
        self.active_conflicts: Set[ConflictType] = set()
        self.narrative_mode = NarrativeMode.LIMITED

        # 初始化限制器
        for constraint in self.DEFAULT_LIMITATIONS:
            self.limitations[constraint.id] = constraint

    def check_constraint(self, action: str) -> Tuple[bool, Optional[str]]:
        """
        检查行为是否违反约束

        返回: (是否合规, 违规信息)
        """
        action_lower = action.lower()

        for constraint in self.limitations.values():
            if constraint.type == ConstraintType.FORBIDDEN:
                # 检查是否违反
                for example in constraint.examples:
                    if example in action_lower:
                        return False, f"违反约束 [{constraint.id}]: {constraint.description}"

        return True, None

    def validate_behavior(
        self,
        behavior: str,
        character_traits: Optional[Dict] = None
    ) -> Dict:
        """
        验证角色行为的合理性

        检查:
        1. 是否符合角色内在逻辑
        2. 是否复合角色诉求的目的性
        3. 是否保持角色去神性化
        """
        validation = {
            "valid": True,
            "violations": [],
            "warnings": [],
            "suggestions": []
        }

        # 检查基本约束
        is_valid, violation_msg = self.check_constraint(behavior)
        if not is_valid:
            validation["valid"] = False
            validation["violations"].append(violation_msg)

        # 检查角色约束
        if not self.role_constraints.can_fail:
            if "成功" in behavior or "胜利" in behavior:
                validation["warnings"].append("角色可能过于顺利")

        # 检查去神性化
        if character_traits:
            mbti = character_traits.get("mbti", "")

            # 某些MBTI类型不应该有完美表现
            if "INFJ" in mbti or "INFP" in mbti:
                if "立即理解" in behavior or "完美共情" in behavior:
                    validation["warnings"].append(f"{mbti}类型角色可能过度理想化")

        return validation

    def activate_conflict(self, conflict_type: ConflictType, intensity: float = 0.5) -> bool:
        """激活冲突变量"""
        if intensity >= self.CONFLICT_VARIABLES[conflict_type].activation_threshold:
            self.active_conflicts.add(conflict_type)
            return True
        return False

    def get_conflict_escalation(
        self,
        conflict_type: ConflictType,
        current_level: str = "personal"
    ) -> List[str]:
        """
        获取冲突升级路径

        层次: personal -> social -> world
        """
        levels = list(self.CONFLICT_ESCALATION.keys())

        if current_level not in levels:
            return []

        current_idx = levels.index(current_level)

        # 获取当前及更高层次的变量
        escalation = []
        for level in levels[current_idx:]:
            escalation.extend(self.CONFLICT_ESCALATION[level]["variables"])

        return escalation

    def apply_tcm_thinking(
        self,
        problem: str,
        diagnosis: Dict
    ) -> Dict:
        """
        应用中医开方思维解决问题

        核心:
        - 扶正固本: 增强正气,提升免疫力
        - 调和阴阳: 平衡各方因素
        - 脾肾同调: 兼顾表里/根本
        """
        solution = {
            "core_approach": [],
            "balance_considerations": [],
            "comprehensive_treatment": []
        }

        # 扶正固本
        if "weakness" in diagnosis or "vulnerability" in diagnosis:
            solution["core_approach"].append({
                "method": "扶正固本",
                "action": "增强角色内在力量和稳定性"
            })

        # 调和阴阳
        if "conflict" in problem or "imbalance" in problem:
            solution["balance_considerations"].append({
                "method": "调和阴阳",
                "action": "平衡各方利益和情感"
            })

        # 脾肾同调
        solution["comprehensive_treatment"].append({
            "method": "脾肾同调",
            "action": "兼顾表面问题和根本原因"
        })

        return solution

    def generate_character_constraint(
        self,
        mbti: Optional[str] = None,
        trauma_level: float = 0.0
    ) -> RoleConstraint:
        """
        根据角色特征生成约束配置

        创伤越深，约束越严格
        """
        constraint = RoleConstraint()

        # MBTI类型影响约束
        if mbti:
            if "J" in mbti:
                # 判断型更需要有空白
                constraint.allow_blanks = True

            if "F" in mbti:
                # 情感型更容易被影响
                constraint.can_fail = True
                constraint.can_not_know = True

        # 创伤程度影响
        if trauma_level > 0.7:
            # 重度创伤者需要更严格的约束
            constraint.no_definition = True
            constraint.no_explanation = True

        self.role_constraints = constraint
        return constraint

    def get_narrative_mode(self) -> NarrativeMode:
        """获取当前叙事模式"""
        return self.narrative_mode

    def set_narrative_mode(self, mode: NarrativeMode):
        """设置叙事模式"""
        self.narrative_mode = mode

    def get_system_report(self) -> Dict:
        """获取系统报告"""
        return {
            "active_constraints": len([c for c in self.limitations.values() if c.type == ConstraintType.FORBIDDEN]),
            "active_conflicts": [c.value for c in self.active_conflicts],
            "narrative_mode": self.narrative_mode.value,
            "role_constraints": {
                "can_fail": self.role_constraints.can_fail,
                "can_be_wrong": self.role_constraints.can_be_wrong,
                "can_not_know": self.role_constraints.can_not_know,
                "allow_blanks": self.role_constraints.allow_blanks,
                "no_definition": self.role_constraints.no_definition,
                "no_explanation": self.role_constraints.no_explanation
            },
            "conflict_variables": {
                c.value: {
                    "description": v.description,
                    "active": c in self.active_conflicts
                }
                for c, v in self.CONFLICT_VARIABLES.items()
            }
        }


def create_author_system() -> AuthorConstraintSystem:
    """工厂函数：创建作者约束系统"""
    return AuthorConstraintSystem()