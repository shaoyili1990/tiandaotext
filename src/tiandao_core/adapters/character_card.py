"""
Character Card Adapter - 角色卡格式适配器

支持SillyTavern V2角色卡格式
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import json

from ..core.profile import CharacterProfile, CharacterInfo
from ..core.mbti import MBTISystem


@dataclass
class CharacterCardAdapter:
    """
    角色卡适配器

    支持格式:
    - SillyTavern V2 JSON格式
    - 自定义JSON格式
    """

    @staticmethod
    def from_sillytavern(data: Dict) -> CharacterProfile:
        """
        从SillyTavern格式转换为CharacterProfile

        SillyTavern格式字段:
        - name: 角色名
        - description: 描述
        - personality: 性格 (用于MBTI推断)
        - tags: 标签列表 (用于MBTI推断)
        - first_message: 第一条消息
        - avatar: 头像URL
        """
        name = data.get("name", "未命名角色")
        description = data.get("description", "")
        tags = data.get("tags", [])
        personality = data.get("personality", "")

        # 从标签和性格推断MBTI
        mbti_system = MBTISystem.from_tags(tags + [personality])
        mbti_type = mbti_system.mbti_type

        # 从MBTI获取基线Y值
        base_y = 50 + mbti_system.weights.base_y_offset

        # 创建角色画像
        character_id = name.replace(" ", "_")
        profile = CharacterProfile.create(
            character_id=character_id,
            name=name,
            base_y=base_y,
            mbti_type=mbti_type,
            tags=tags,
            description=description
        )

        # 如果有额外数据，设置创伤等级
        if "Creator" in data:
            profile.info.created_at = data.get("Creator")

        return profile

    @staticmethod
    def to_sillytavern(profile: CharacterProfile) -> Dict:
        """
        从CharacterProfile转换为SillyTavern格式
        """
        data = {
            "name": profile.info.name,
            "description": profile.info.description,
            "personality": profile.mbti_system.get_reaction_style() if profile.mbti_system else "",
            "tags": profile.info.tags,
            "first_message": "",
            "avatar": profile.info.avatar_url or "",
            "chat_history": [],
            "author": "Tiandao System",
            "version": "2.0"
        }

        # 附加天道系统数据
        if profile.y_system:
            data["tiandao"] = {
                "base_y": profile.y_system.state.baseline_y,
                "current_y": profile.y_system.Y,
                "mbti": profile.info.mbti_type
            }

        return data

    @staticmethod
    def to_tiandao_format(profile: CharacterProfile) -> Dict:
        """
        转换为标准天道格式
        """
        return {
            "name": profile.info.name,
            "world": profile.info.description.split("\n")[0] if profile.info.description else "通用",
            "mbti": profile.info.mbti_type,
            "base_y": profile.info.base_y,
            "current_y": profile.y_system.Y if profile.y_system else profile.info.base_y,
            "baseline_range": profile.mbti_system.get_rebound_range() if profile.mbti_system else (50, 70),
            "character_class": "main",
            "weight": 80,
            "position": [0, 0, 0],
            "appearance": "",
            "personality": profile.mbti_system.get_reaction_style() if profile.mbti_system else "",
            "background": profile.info.description,
            "desires": profile.motivation_system.get_motivation_profile() if profile.motivation_system else {},
            "emotions": profile.psychology.seven_emotions if profile.psychology else {},
            "current_thoughts": "",
            "current_wants": "",
            "long_term_memories": [],
            "short_term_memories": [],
            "anomalous_memories": []
        }

    @staticmethod
    def from_tiandao_format(data: Dict) -> CharacterProfile:
        """
        从天道格式创建CharacterProfile
        """
        name = data.get("name", "未命名角色")
        mbti_type = data.get("mbti", "INTJ")
        base_y = data.get("base_y", 50)

        profile = CharacterProfile.create(
            character_id=name.replace(" ", "_"),
            name=name,
            base_y=base_y,
            mbti_type=mbti_type,
            description=data.get("background", "")
        )

        # 恢复当前Y值
        if profile.y_system and "current_y" in data:
            profile.y_system.state.current_y = data["current_y"]

        return profile


def load_character_card(file_path: str) -> CharacterProfile:
    """加载角色卡文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return CharacterCardAdapter.from_sillytavern(data)


def save_character_card(profile: CharacterProfile, file_path: str):
    """保存角色卡文件"""
    data = CharacterCardAdapter.to_sillytavern(profile)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)