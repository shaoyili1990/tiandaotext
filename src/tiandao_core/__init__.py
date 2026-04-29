"""
Tiandao Core - 天道系统 Python 核心包

一个完整的角色心理系统模拟包，包含:
- Y值系统 (主观意识凝练强度)
- MBTI人格权重系统
- 记忆系统 (5型记忆 + PTSD机制)
- 动机链系统 (7本能4层级)
- 作者约束系统
- 角色画像聚合器

Author: Tiandao System
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Tiandao System"

from .core.y_value import YValueSystem
from .core.mbti import MBTISystem
from .core.memory import MemorySystem
from .core.motivation import MotivationSystem
from .core.author import AuthorConstraintSystem
from .core.profile import CharacterProfile, CharacterInfo
from .core.psychology import PsychologyEngine

__all__ = [
    "YValueSystem",
    "MBTISystem",
    "MemorySystem",
    "MotivationSystem",
    "AuthorConstraintSystem",
    "CharacterProfile",
    "CharacterInfo",
    "PsychologyEngine",
    "create_profile",
]


def create_profile(
    name: str,
    mbti_type: str = "INFP",
    base_y: float = 70.0,
    character_id: str = None
):
    """
    创建角色画像的便捷工厂函数

    Args:
        name: 角色名称
        mbti_type: MBTI类型 (16种之一)
        base_y: 基础Y值 (0-100)
        character_id: 可选的字符ID

    Returns:
        CharacterProfile: 完整的角色画像实例
    """
    profile = CharacterProfile.create(
        character_id=character_id or name,
        name=name,
        base_y=base_y,
        mbti_type=mbti_type
    )
    return profile