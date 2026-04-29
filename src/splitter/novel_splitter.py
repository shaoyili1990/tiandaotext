"""
Novel Splitter - 小说拆书系统

功能：
1. 拆解小说文本为卷/章/角色快照/事件卡
2. 使用AI提取角色快照和事件
3. 生成结构化的拆解结果

输出结构：
data/novel_split/
└── {小说名}/
    ├── overview.json              # 小说概述
    └── volumes/
        └── v01_{卷名}/
            ├── volume_overview.json
            └── chapters/
                └── ch01_{章名}/
                    ├── chapter_content.txt    # 章节原文
                    ├── chapter_summary.json   # 章节概述
                    ├── characters/             # 出场人物快照
                    │   ├── 张三.json          # CharacterSnapshot
                    │   └── 李四.json
                    └── events/               # 事件卡
                        └── evt_001.json      # EventCard

AI提取内容：
1. 本章出场人物快照（MBTI/情绪/此刻所思所求）
2. 关键事件（起因/经过/结果）+ 人物分类（主要/次要/龙套）
3. 章节概述
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from tiandao_core.core.profile import CharacterProfile
from tiandao_core.core.mbti import MBTISystem
from tiandao_core.adapters.character_card import CharacterCardAdapter
from tiandao_core.adapters.world_book import WorldBookAdapter
from tiandao_core.adapters.event_card import EventCardAdapter


class CharacterRole(Enum):
    """事件中的人物角色分类"""
    PROTAGONIST = "主要"
    MAIN = "主要"
    SECONDARY = "次要"
    SUPPORTING = "次要"
    NPC = "龙套"
    BACKGROUND = "龙套"


class EventCard:
    """事件卡"""
    def __init__(
        self,
        event_id: str,
        title: str,
        cause: str,
        process: str,
        result: str,
        characters: List[Dict] = None,
        y_value_impact: Dict[str, int] = None
    ):
        self.event_id = event_id
        self.title = title
        self.cause = cause
        self.process = process
        self.result = result
        self.characters = characters or []
        self.y_value_impact = y_value_impact or {}

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "cause": self.cause,
            "process": self.process,
            "result": self.result,
            "characters": self.characters,
            "y_value_impact": self.y_value_impact
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'EventCard':
        return cls(
            event_id=data.get("event_id", ""),
            title=data.get("title", ""),
            cause=data.get("cause", ""),
            process=data.get("process", ""),
            result=data.get("result", ""),
            characters=data.get("characters", []),
            y_value_impact=data.get("y_value_impact", {})
        )


class CharacterSnapshot:
    """角色快照 - 记录人物出场时的当前状态"""
    def __init__(
        self,
        name: str,
        mbti: str,
        current_y: int,
        emotional_state: str,
        current_desire: str,
        appearance: str = ""
    ):
        self.name = name
        self.mbti = mbti
        self.current_y = current_y
        self.emotional_state = emotional_state
        self.current_desire = current_desire
        self.appearance = appearance

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "mbti": self.mbti,
            "current_y": self.current_y,
            "emotional_state": self.emotional_state,
            "current_desire": self.current_desire,
            "appearance": self.appearance
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CharacterSnapshot':
        return cls(
            name=data.get("name", ""),
            mbti=data.get("mbti", "UNKNOWN"),
            current_y=data.get("current_y", 50),
            emotional_state=data.get("emotional_state", ""),
            current_desire=data.get("current_desire", ""),
            appearance=data.get("appearance", "")
        )


class ChapterSplit:
    """章节拆解结果"""
    def __init__(
        self,
        chapter_num: int,
        chapter_title: str,
        content: str,
        summary: str = "",
        character_snapshots: List[CharacterSnapshot] = None,
        event_cards: List[EventCard] = None
    ):
        self.chapter_num = chapter_num
        self.chapter_title = chapter_title
        self.content = content
        self.summary = summary
        self.character_snapshots = character_snapshots or []
        self.event_cards = event_cards or []

    def to_dict(self) -> Dict:
        return {
            "chapter_num": self.chapter_num,
            "chapter_title": self.chapter_title,
            "summary": self.summary,
            "character_snapshots": [s.to_dict() for s in self.character_snapshots],
            "event_cards": [e.to_dict() for e in self.event_cards]
        }


class VolumeSplit:
    """卷拆解结果"""
    def __init__(
        self,
        volume_num: int,
        volume_title: str,
        chapters: List[ChapterSplit] = None,
        overview: str = ""
    ):
        self.volume_num = volume_num
        self.volume_title = volume_title
        self.chapters = chapters or []
        self.overview = overview

    def to_dict(self) -> Dict:
        return {
            "volume_num": self.volume_num,
            "volume_title": self.volume_title,
            "overview": self.overview,
            "chapter_count": len(self.chapters)
        }


class NovelSplit:
    """小说拆解结果"""
    def __init__(
        self,
        title: str,
        overview: str = "",
        world: Dict = None,
        characters: List[Dict] = None,
        volumes: List[VolumeSplit] = None,
        chapters: List[ChapterSplit] = None
    ):
        self.title = title
        self.overview = overview
        self.world = world or {}
        self.characters = characters or []
        self.volumes = volumes or []
        self.chapters = chapters or []

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "overview": self.overview,
            "world": self.world,
            "characters": self.characters,
            "volumes": [v.to_dict() for v in self.volumes],
            "chapters": [c.to_dict() for c in self.chapters]
        }


class NovelSplitter:
    """
    小说拆书系统

    使用AI分析小说文本，提取：
    1. 角色信息（MBTI、Y值、情绪状态）
    2. 世界设定
    3. 事件序列
    4. 章节结构
    5. 卷结构
    """

    def __init__(self, api=None):
        self.api = api
        self.split_result: Optional[NovelSplit] = None

    def split_by_volumes_and_chapters(self, text: str) -> List[Tuple[int, str, List[Tuple[int, str, str]]]]:
        """
        按卷和章节分割小说文本

        返回: [(卷号, 卷名, [(章节号, 章节名, 内容), ...]), ...]
        """
        volumes = []
        current_volume = None
        current_chapters = []

        lines = text.split('\n')
        chapter_pattern = re.compile(r'^第[一二三四五六七八九十百千\d]+[章节]')
        volume_pattern = re.compile(r'^第[一二三四五六七八九十百千\d]+[卷部]')

        for line in lines:
            stripped = line.strip()
            if volume_pattern.match(stripped):
                # 保存上一卷
                if current_volume is not None:
                    volumes.append((current_volume[0], current_volume[1], current_chapters))
                # 开始新卷
                title = stripped
                num_match = re.search(r'第([一二三四五六七八九十百千\d]+)', title)
                volume_num = self._chinese_to_number(num_match.group(1)) if num_match else len(volumes) + 1
                current_volume = (volume_num, title)
                current_chapters = []
            elif chapter_pattern.match(stripped):
                # 保存上一章
                if current_chapters and current_chapters[-1][2].strip():
                    pass  # 内容已积累
                # 开始新章节
                title = stripped
                num_match = re.search(r'第([一二三四五六七八九十百千\d]+)', title)
                chapter_num = self._chinese_to_number(num_match.group(1)) if num_match else len(current_chapters) + 1
                current_chapters.append((chapter_num, title, ""))
            else:
                # 累加内容到当前章节
                if current_chapters:
                    current_chapters[-1] = (current_chapters[-1][0], current_chapters[-1][1], current_chapters[-1][2] + line + "\n")

        # 保存最后一卷
        if current_volume is not None:
            volumes.append((current_volume[0], current_volume[1], current_chapters))

        # 如果没有找到卷结构，按简单章节分割
        if not volumes:
            chapters = self.split_by_chapters(text)
            if chapters:
                volumes.append((1, "第1卷", chapters))

        return volumes

    def split_by_chapters(self, text: str) -> List[Tuple[int, str, str]]:
        """
        按章节分割小说文本（无卷结构时使用）

        返回: [(章节号, 章节名, 内容), ...]
        """
        chapters = []
        lines = text.split('\n')
        current_chapter = None
        current_content = []

        chapter_pattern = re.compile(r'^第[一二三四五六七八九十百千\d]+[章节]')

        for line in lines:
            if chapter_pattern.match(line.strip()):
                if current_chapter is not None:
                    content = '\n'.join(current_content)
                    if content.strip():
                        chapters.append((current_chapter[0], current_chapter[1], content))
                title = line.strip()
                num_match = re.search(r'第([一二三四五六七八九十百千\d]+)', title)
                chapter_num = self._chinese_to_number(num_match.group(1)) if num_match else len(chapters) + 1
                current_chapter = (chapter_num, title)
                current_content = []
            elif current_chapter is not None:
                current_content.append(line)

        if current_chapter is not None:
            content = '\n'.join(current_content)
            if content.strip():
                chapters.append((current_chapter[0], current_chapter[1], content))

        if not chapters:
            paragraphs = text.split('\n\n')
            for i, para in enumerate(paragraphs):
                if para.strip():
                    chapters.append((i + 1, f"第{i+1}章", para))

        return chapters

    def _chinese_to_number(self, chinese: str) -> int:
        """将中文数字转换为整数"""
        chinese_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000, '万': 10000
        }

        if chinese.isdigit():
            return int(chinese)

        result = 0
        temp = 0

        for char in chinese:
            if char in chinese_map:
                value = chinese_map[char]
                if value >= 1000:
                    result += temp * value
                    temp = 0
                elif value >= 100:
                    temp = value
                else:
                    temp += value

        return result + temp

    def split_novel(
        self,
        novel_text: str,
        novel_title: str = "未命名小说",
        output_dir: str = None
    ) -> NovelSplit:
        """
        拆解整本小说

        参数:
        - novel_text: 小说文本
        - novel_title: 小说标题
        - output_dir: 输出目录

        返回:
        - NovelSplit: 拆解结果
        """
        if self.api is None:
            return self._split_without_ai(novel_text, novel_title)

        # 按卷和章节分割
        volume_data = self.split_by_volumes_and_chapters(novel_text)

        split_result = NovelSplit(
            title=novel_title,
            overview="",
            world={},
            characters=[],
            volumes=[],
            chapters=[]
        )

        for volume_num, volume_title, chapters in volume_data:
            volume = VolumeSplit(volume_num=volume_num, volume_title=volume_title)

            for chapter_num, chapter_title, content in chapters:
                print(f"正在分析第{volume_num}卷 第{chapter_num}章: {chapter_title[:20]}...")

                # 使用AI分析章节
                chapter_data = self.api.split_chapter(content, chapter_num)

                # 解析角色快照
                snapshots = []
                for char_data in chapter_data.get("characters", []):
                    snapshot = CharacterSnapshot(
                        name=char_data.get("name", "未知"),
                        mbti=char_data.get("mbti", "UNKNOWN"),
                        current_y=char_data.get("current_y", 50),
                        emotional_state=char_data.get("emotional_state", ""),
                        current_desire=char_data.get("current_desire", ""),
                        appearance=char_data.get("appearance", "")
                    )
                    snapshots.append(snapshot)

                # 解析事件卡
                event_cards = []
                for i, evt in enumerate(chapter_data.get("events", [])):
                    event_card = EventCard(
                        event_id=f"evt_{volume_num}_{chapter_num}_{i+1:03d}",
                        title=evt.get("title", f"事件{i+1}"),
                        cause=evt.get("cause", ""),
                        process=evt.get("process", ""),
                        result=evt.get("result", ""),
                        characters=evt.get("characters", []),  # [{"name": "张三", "role": "主要"}, ...]
                        y_value_impact=evt.get("y_value_impact", {})
                    )
                    event_cards.append(event_card)

                chapter_split = ChapterSplit(
                    chapter_num=chapter_num,
                    chapter_title=chapter_title,
                    content=content[:5000],
                    summary=chapter_data.get("summary", ""),
                    character_snapshots=snapshots,
                    event_cards=event_cards
                )

                volume.chapters.append(chapter_split)
                split_result.chapters.append(chapter_split)

                # 收集角色（用于全局角色列表）
                for char_data in chapter_data.get("characters", []):
                    if not any(c.get("name") == char_data.get("name") for c in split_result.characters):
                        split_result.characters.append(char_data)

            split_result.volumes.append(volume)

        self.split_result = split_result

        if output_dir:
            self._save_split_result(split_result, output_dir)

        return split_result

    def _split_without_ai(self, novel_text: str, novel_title: str) -> NovelSplit:
        """不使用AI的简单分割"""
        volume_data = self.split_by_volumes_and_chapters(novel_text)

        split_result = NovelSplit(
            title=novel_title,
            overview="",
            world={},
            characters=[],
            volumes=[],
            chapters=[]
        )

        for volume_num, volume_title, chapters in volume_data:
            volume = VolumeSplit(volume_num=volume_num, volume_title=volume_title)

            for chapter_num, chapter_title, content in chapters:
                chapter_split = ChapterSplit(
                    chapter_num=chapter_num,
                    chapter_title=chapter_title,
                    content=content,
                    summary="",
                    character_snapshots=[],
                    event_cards=[]
                )
                volume.chapters.append(chapter_split)
                split_result.chapters.append(chapter_split)

            split_result.volumes.append(volume)

        return split_result

    def _save_split_result(self, result: NovelSplit, output_dir: str):
        """保存拆解结果到文件"""
        base_dir = Path(output_dir) / result.title
        base_dir.mkdir(parents=True, exist_ok=True)

        # 保存整体信息
        overview = {
            "title": result.title,
            "overview": result.overview,
            "total_volumes": len(result.volumes),
            "total_chapters": len(result.chapters),
            "total_characters": len(result.characters)
        }

        (base_dir / "overview.json").write_text(
            json.dumps(overview, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # 保存每卷
        for volume in result.volumes:
            volume_dir = base_dir / f"v{volume.volume_num:02d}_{volume.volume_title[:20]}"
            volume_dir.mkdir(exist_ok=True)

            # 卷概述
            volume_overview = volume.to_dict()
            (volume_dir / "volume_overview.json").write_text(
                json.dumps(volume_overview, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )

            # 保存每章
            chapters_dir = volume_dir / "chapters"
            chapters_dir.mkdir(exist_ok=True)

            for chapter in volume.chapters:
                chapter_dir = chapters_dir / f"ch{chapter.chapter_num:02d}_{chapter.chapter_title[:20]}"
                chapter_dir.mkdir(exist_ok=True)

                # 章节内容
                (chapter_dir / "chapter_content.txt").write_text(
                    chapter.content, encoding='utf-8'
                )

                # 章节摘要
                chapter_summary = chapter.to_dict()
                # 移除content避免重复
                chapter_summary["content_length"] = len(chapter.content)
                (chapter_dir / "chapter_summary.json").write_text(
                    json.dumps(chapter_summary, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )

                # 角色快照
                chars_dir = chapter_dir / "characters"
                chars_dir.mkdir(exist_ok=True)

                for snapshot in chapter.character_snapshots:
                    char_file = chars_dir / f"{snapshot.name}.json"
                    char_file.write_text(
                        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2),
                        encoding='utf-8'
                    )

                # 事件卡
                events_dir = chapter_dir / "events"
                events_dir.mkdir(exist_ok=True)

                for event_card in chapter.event_cards:
                    evt_file = events_dir / f"{event_card.event_id}.json"
                    evt_file.write_text(
                        json.dumps(event_card.to_dict(), ensure_ascii=False, indent=2),
                        encoding='utf-8'
                    )

        print(f"拆解结果已保存到: {base_dir}")

    def export_to_tiandao_format(self, result: NovelSplit) -> Dict:
        """导出为天道系统格式"""
        world_data = result.world.copy() if result.world else {}
        world_data["name"] = result.title
        world_data["type"] = "通用"

        character_profiles = []
        for char_data in result.characters:
            profile = CharacterCardAdapter.from_tiandao_format(char_data)
            character_profiles.append(profile)

        return {
            "world": world_data,
            "characters": character_profiles,
            "chapters": [
                {
                    "num": ch.chapter_num,
                    "title": ch.chapter_title,
                    "summary": ch.summary,
                    "characters": [s.to_dict() for s in ch.character_snapshots],
                    "events": [e.to_dict() for e in ch.event_cards]
                }
                for ch in result.chapters
            ]
        }


def create_novel_splitter(api=None) -> NovelSplitter:
    """工厂函数：创建小说拆书器"""
    return NovelSplitter(api=api)
