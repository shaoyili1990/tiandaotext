"""
World Book Adapter - 世界书格式适配器
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from datetime import datetime


@dataclass
class WorldBookAdapter:
    """
    世界书适配器
    """

    @staticmethod
    def to_standard(world_data: Dict) -> Dict:
        """
        转换为标准世界书格式

        标准格式字段:
        - name: 世界名称
        - type: 世界类型 (都市/玄幻/科幻/言情/悬疑/仙侠)
        - overview: 世界概述
        - geography: 地理与社会
        - factions: 势力与组织
        - rules: 规则与法则
        - keywords: 氛围关键词
        - suggested_characters: 推荐角色
        - initial_events: 初始事件
        """
        return {
            "name": world_data.get("name", "未命名世界"),
            "type": world_data.get("type", "都市"),
            "overview": world_data.get("overview", ""),
            "geography": world_data.get("geography", ""),
            "factions": world_data.get("factions", ""),
            "rules": world_data.get("rules", ""),
            "keywords": world_data.get("keywords", []),
            "suggested_characters": world_data.get("suggested_characters", []),
            "initial_events": world_data.get("initial_events", []),
            "created_at": world_data.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat()
        }

    @staticmethod
    def from_ai_response(response: Dict) -> Dict:
        """
        从AI响应创建世界书

        AI响应格式示例:
        {
            "name": "世界名称",
            "type": "都市",
            "overview": "概述...",
            ...
        }
        """
        return WorldBookAdapter.to_standard(response)

    @staticmethod
    def merge_edits(original: Dict, edits: Dict) -> Dict:
        """
        合并编辑到原始世界书

        只更新提供的字段
        """
        merged = original.copy()

        for key, value in edits.items():
            if key not in ["created_at"] and value is not None:
                merged[key] = value

        merged["updated_at"] = datetime.now().isoformat()

        return merged

    @staticmethod
    def validate(world_data: Dict) -> List[str]:
        """
        验证世界书数据

        返回错误列表，空列表表示验证通过
        """
        errors = []

        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in world_data or not world_data[field]:
                errors.append(f"缺少必需字段: {field}")

        valid_types = ["都市", "玄幻", "科幻", "言情", "悬疑", "仙侠", "自定义"]
        if world_data.get("type") not in valid_types:
            errors.append(f"无效的世界类型: {world_data.get('type')}")

        return errors


def load_world_book(file_path: str) -> Dict:
    """加载世界书文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_world_book(world_data: Dict, file_path: str):
    """保存世界书文件"""
    validated = WorldBookAdapter.to_standard(world_data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)