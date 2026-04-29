"""
Character Profile - 角色画像聚合器

整合Y值系统、MBTI系统、记忆系统、动机系统、作者约束系统
提供统一的角色画像管理接口

核心功能:
1. 角色信息聚合
2. 系统状态同步
3. 角色创建与序列化
4. 画像生成与导出
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import json

from .y_value import YValueSystem, YValueConfig, YValueState
from .mbti import MBTISystem, BigFiveTraits
from .memory import MemorySystem, MemoryType, MemoryNode
from .motivation import MotivationSystem, InstinctType, MotivationLayer
from .author import AuthorConstraintSystem, RoleConstraint
from .psychology import PsychologyEngine, EmotionalState, SevenEmotions


@dataclass
class CharacterInfo:
    """角色基本信息"""
    id: str
    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    avatar_url: Optional[str] = None

    # 外部设定
    base_y: int = 50              # 基础Y值
    mbti_type: str = "INTJ"       # MBTI类型
    trauma_level: float = 0.0     # 创伤等级 [0-1]

    # 元数据
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class CharacterProfile:
    """
    角色画像 - 统一聚合器

    整合所有子系统，提供完整的角色画像
    """
    info: CharacterInfo

    # 核心子系统
    y_system: Optional[YValueSystem] = None
    mbti_system: Optional[MBTISystem] = None
    memory_system: Optional[MemorySystem] = None
    motivation_system: Optional[MotivationSystem] = None
    author_system: Optional[AuthorConstraintSystem] = None

    # 心理学引擎
    psychology: Optional[PsychologyEngine] = None

    # 状态标记
    is_initialized: bool = False

    @classmethod
    def create(
        cls,
        character_id: str,
        name: str,
        base_y: int = 50,
        mbti_type: str = "INTJ",
        tags: Optional[List[str]] = None,
        description: str = ""
    ) -> "CharacterProfile":
        """
        创建新角色画像

        参数:
        - character_id: 角色ID
        - name: 角色名称
        - base_y: 基础Y值 [1-100]
        - mbti_type: MBTI类型
        - tags: 标签列表
        - description: 角色描述
        """
        info = CharacterInfo(
            id=character_id,
            name=name,
            tags=tags or [],
            description=description,
            base_y=base_y,
            mbti_type=mbti_type
        )

        profile = cls(info=info)
        profile.initialize()

        return profile

    def initialize(self):
        """初始化所有子系统"""
        # Y值系统
        self.y_system = YValueSystem(YValueConfig(base_y=self.info.base_y))
        self.y_system.set_baseline(
            self.mbti_system.weights.base_y_offset + self.info.base_y if self.mbti_system else self.info.base_y
        )

        # MBTI系统
        self.mbti_system = MBTISystem(self.info.mbti_type)
        self.y_system.set_baseline(self.mbti_system.get_baseline_y(self.info.base_y))

        # 记忆系统
        self.memory_system = MemorySystem()

        # 动机系统
        self.motivation_system = MotivationSystem(self.info.id)

        # 作者约束系统
        self.author_system = AuthorConstraintSystem()
        self.author_system.generate_character_constraint(
            self.info.mbti_type, self.info.trauma_level
        )

        # 心理学引擎
        self.psychology = PsychologyEngine(
            base_y=self.info.base_y,
            mbti_type=self.info.mbti_type,
            character_id=self.info.id
        )

        self.is_initialized = True

    def calculate_response(
        self,
        situation: str,
        context: Optional[Dict] = None,
        interaction_y: Optional[int] = None
    ) -> Dict:
        """
        计算角色对情境的反应

        整合所有子系统，计算综合输出
        """
        if not self.is_initialized:
            self.initialize()

        # 使用心理学引擎计算
        result = self.psychology.calculate(
            situation=situation,
            context=context,
            interaction_y=interaction_y
        )

        return {
            "y_value": result.y_value,
            "emotional_state": asdict(result.emotional_state),
            "active_motivations": result.active_motivations,
            "triggered_memories": result.triggered_memories,
            "behavioral_tendency": result.behavioral_tendency,
            "moral_adjustment": result.moral_adjustment,
            "overflow_warning": result.overflow_warning,
            "messages": result.messages
        }

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        emotional_intensity: float = 0.5,
        importance: float = 0.5,
        is_traumatic: bool = False,
        trauma_level: float = 0.0,
        triggers: Optional[List[str]] = None
    ) -> MemoryNode:
        """添加记忆"""
        if not self.is_initialized:
            self.initialize()

        return self.memory_system.add_memory(
            content=content,
            memory_type=memory_type,
            emotional_intensity=emotional_intensity,
            importance=importance,
            is_traumatic=is_traumatic,
            trauma_level=trauma_level,
            triggers=triggers
        )

    def retrieve_memories(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """检索相关记忆"""
        if not self.is_initialized:
            self.initialize()

        results = self.memory_system.retrieve(
            query=query,
            memory_types=memory_types,
            limit=limit
        )

        return [
            {
                "id": r.memory.id,
                "content": r.memory.content,
                "type": r.memory.memory_type.value,
                "relevance": r.relevance,
                "strength": r.memory.strength,
                "is_traumatic": r.memory.is_traumatic
            }
            for r in results
        ]

    def check_ptsd(self, event: str) -> Dict:
        """检查PTSD触发"""
        if not self.is_initialized:
            self.initialize()

        triggered, memories, strength = self.memory_system.check_ptsd_triggers(
            event, self.y_system.Y
        )

        return {
            "triggered": triggered,
            "strength": strength,
            "triggered_memories": [
                {
                    "id": m.memory.id,
                    "content": m.memory.content,
                    "trauma_level": m.memory.trauma_level
                }
                for m in memories
            ]
        }

    def activate_instinct(
        self,
        instinct_type: InstinctType,
        intensity_modifier: float = 1.0
    ) -> Dict:
        """激活本能"""
        if not self.is_initialized:
            self.initialize()

        motivation = self.motivation_system.activate_instinct(
            instinct_type, intensity_modifier
        )

        return {
            "instinct": instinct_type.value,
            "intensity": motivation.intensity,
            "active": motivation.is_active,
            "layer": motivation.layer.value
        }

    def validate_behavior(self, behavior: str) -> Dict:
        """验证行为是否符合作者约束"""
        if not self.is_initialized:
            self.initialize()

        character_traits = {
            "mbti": self.info.mbti_type,
            "trauma_level": self.info.trauma_level
        }

        return self.author_system.validate_behavior(behavior, character_traits)

    def get_full_profile(self) -> Dict:
        """获取完整角色画像"""
        if not self.is_initialized:
            self.initialize()

        return {
            "info": asdict(self.info),
            "y_value": self.y_system.get_state_report(),
            "mbti": self.mbti_system.get_full_profile(),
            "memory": self.memory_system.get_memory_summary(),
            "motivation": self.motivation_system.get_motivation_profile(),
            "author": self.author_system.get_system_report(),
            "psychology": self.psychology.get_full_report()
        }

    def to_dict(self) -> Dict:
        """序列化为字典"""
        return self.get_full_profile()

    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict) -> "CharacterProfile":
        """从字典反序列化"""
        info_data = data.get("info", {})
        info = CharacterInfo(
            id=info_data.get("id", ""),
            name=info_data.get("name", ""),
            description=info_data.get("description", ""),
            tags=info_data.get("tags", []),
            avatar_url=info_data.get("avatar_url"),
            base_y=info_data.get("base_y", 50),
            mbti_type=info_data.get("mbti_type", "INTJ"),
            trauma_level=info_data.get("trauma_level", 0.0)
        )

        profile = cls(info=info)
        profile.is_initialized = True

        return profile

    @classmethod
    def from_json(cls, json_str: str) -> "CharacterProfile":
        """从JSON反序列化"""
        data = json.loads(json_str)
        return cls.from_dict(data)


def create_character(
    name: str,
    base_y: int = 50,
    mbti_type: str = "INTJ",
    tags: Optional[List[str]] = None,
    description: str = ""
) -> CharacterProfile:
    """工厂函数：创建角色"""
    import uuid
    character_id = str(uuid.uuid4())[:8]
    return CharacterProfile.create(
        character_id=character_id,
        name=name,
        base_y=base_y,
        mbti_type=mbti_type,
        tags=tags,
        description=description
    )