"""
Event Card Adapter - 事件卡格式适配器
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from datetime import datetime


@dataclass
class EventCardAdapter:
    """
    事件卡适配器
    """

    # 事件类型
    EVENT_TYPES = ["剧情", "支线", "随机", "高潮", "结局"]

    @staticmethod
    def to_standard(event_data: Dict) -> Dict:
        """
        转换为标准事件卡格式

        标准格式字段:
        - id: 事件ID (格式: v{卷号}_ch{章号}_e{事件号})
        - title: 事件标题
        - world: 所属世界
        - type: 事件类型 (剧情/支线/随机/高潮/结局)
        - cause: 起因
        - process: 经过
        - result: 结果
        - characters: 涉及角色
        - y_value_changes: Y值变化记录
        """
        return {
            "id": event_data.get("id", f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "title": event_data.get("title", "未命名事件"),
            "world": event_data.get("world", "通用"),
            "type": event_data.get("type", "剧情"),
            "cause": event_data.get("cause", ""),
            "process": event_data.get("process", ""),
            "result": event_data.get("result", ""),
            "characters": event_data.get("characters", {
                "main": [],
                "secondary": [],
                "background": []
            }),
            "y_value_changes": event_data.get("y_value_changes", {}),
            "created_at": event_data.get("created_at", datetime.now().isoformat())
        }

    @staticmethod
    def from_ai_response(response: Dict, world: str = "通用") -> Dict:
        """
        从AI响应创建事件卡
        """
        return EventCardAdapter.to_standard({
            "title": response.get("title", "未命名事件"),
            "world": world,
            "type": response.get("type", "剧情"),
            "cause": response.get("cause", ""),
            "process": response.get("process", ""),
            "result": response.get("result", ""),
            "characters": response.get("characters", {
                "main": response.get("main_characters", []),
                "secondary": response.get("secondary_characters", []),
                "background": response.get("background_characters", [])
            })
        })

    @staticmethod
    def generate_id(volume: int, chapter: int, event_num: int) -> str:
        """
        生成标准事件ID

        格式: v{volume:02d}_ch{chapter:02d}_e{event_num:03d}
        """
        return f"v{volume:02d}_ch{chapter:02d}_e{event_num:03d}"

    @staticmethod
    def validate(event_data: Dict) -> List[str]:
        """
        验证事件卡数据

        返回错误列表，空列表表示验证通过
        """
        errors = []

        required_fields = ["title", "type"]
        for field in required_fields:
            if field not in event_data or not event_data[field]:
                errors.append(f"缺少必需字段: {field}")

        if event_data.get("type") not in EventCardAdapter.EVENT_TYPES:
            errors.append(f"无效的事件类型: {event_data.get('type')}")

        return errors

    @staticmethod
    def add_y_value_change(
        event_data: Dict,
        character_name: str,
        old_y: int,
        new_y: int,
        reason: str
    ) -> Dict:
        """
        添加Y值变化记录
        """
        if "y_value_changes" not in event_data:
            event_data["y_value_changes"] = {}

        event_data["y_value_changes"][character_name] = {
            "old_y": old_y,
            "new_y": new_y,
            "reason": reason
        }

        return event_data


def load_event_card(file_path: str) -> Dict:
    """加载事件卡文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_event_card(event_data: Dict, file_path: str):
    """保存事件卡文件"""
    validated = EventCardAdapter.to_standard(event_data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)