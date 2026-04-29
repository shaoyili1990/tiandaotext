"""
Novel Splitter - 小说拆书系统

功能：
1. 拆解小说文本为角色卡+世界书+事件卡
2. 使用AI提取角色快照和事件
3. 生成结构化的拆解结果

输出结构：
data/novel_split/
├── v01_第1卷/
│   ├── ch01_章节名/
│   │   ├── chapter_content.txt
│   │   ├── chapter_summary.json
│   │   ├── characters/
│   │   │   ├── 张三.json
│   │   │   └── 李四.json
│   │   └── events/
│   │       ├── evt_001.json
│   │       └── evt_002.json
│   └── overview.json
```

AI提取内容：
1. 本章出场人物快照（MBTI/情绪/此刻所思所求）
2. 关键事件（起因/经过/结果）
3. 章节概述
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from tiandao_core.core.profile import CharacterProfile
from tiandao_core.core.mbti import MBTISystem
from tiandao_core.adapters.character_card import CharacterCardAdapter
from tiandao_core.adapters.world_book import WorldBookAdapter
from tiandao_core.adapters.event_card import EventCardAdapter


@dataclass
class ChapterSplit:
    """章节拆解结果"""
    chapter_num: int
    chapter_title: str
    content: str
    summary: str
    characters: List[Dict] = field(default_factory=list)
    events: List[Dict] = field(default_factory=list)


@dataclass
class NovelSplit:
    """小说拆解结果"""
    title: str
    overview: str
    world: Dict
    characters: List[Dict] = field(default_factory=list)
    chapters: List[ChapterSplit] = field(default_factory=list)


class NovelSplitter:
    """
    小说拆书系统

    使用AI分析小说文本，提取：
    1. 角色信息（MBTI、Y值、情绪状态）
    2. 世界设定
    3. 事件序列
    4. 章节结构
    """

    def __init__(self, api=None):
        self.api = api
        self.split_result: Optional[NovelSplit] = None

    def split_by_chapters(self, text: str) -> List[Tuple[int, str, str]]:
        """
        按章节分割小说文本

        返回: [(章节号, 章节名, 内容), ...]
        """
        chapters = []

        # 尝试多种章节分割模式
        patterns = [
            r'第[一二三四五六七八九十百千\d]+章[章节]?\s*(.+?)\s*\n',  # 第X章 标题
            r'第[一二三四五六七八九十百千\d]+回\s*(.+?)\s*\n',        # 第X回 标题
            r'Chapter\s+(\d+):?\s*(.+?)\s*\n',                        # Chapter X: Title
            r'chapter\s+(\d+):?\s*(.+?)\s*\n',                        # chapter X: Title
        ]

        # 简化分割：按行分割，找到章节标题行
        lines = text.split('\n')
        current_chapter = None
        current_content = []

        chapter_pattern = re.compile(r'^第[一二三四五六七八九十百千\d]+[章节]')

        for line in lines:
            if chapter_pattern.match(line.strip()):
                # 保存上一章
                if current_chapter is not None:
                    content = '\n'.join(current_content)
                    if content.strip():
                        chapters.append((current_chapter[0], current_chapter[1], content))

                # 开始新章节
                title = line.strip()
                # 提取章节号
                num_match = re.search(r'第([一二三四五六七八九十百千\d]+)', title)
                if num_match:
                    chapter_num = self._chinese_to_number(num_match.group(1))
                else:
                    chapter_num = len(chapters) + 1

                current_chapter = (chapter_num, title)
                current_content = []
            else:
                if current_chapter is not None:
                    current_content.append(line)

        # 保存最后一章
        if current_chapter is not None:
            content = '\n'.join(current_content)
            if content.strip():
                chapters.append((current_chapter[0], current_chapter[1], content))

        # 如果没有找到章节，使用简单分割
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

        # 按章节分割
        chapters = self.split_by_chapters(novel_text)

        split_result = NovelSplit(
            title=novel_title,
            overview="",
            world={},
            characters=[],
            chapters=[]
        )

        for chapter_num, chapter_title, content in chapters:
            print(f"正在分析第{chapter_num}章: {chapter_title[:20]}...")

            # 使用AI分析章节
            chapter_data = self.api.split_chapter(content, chapter_num)

            chapter_split = ChapterSplit(
                chapter_num=chapter_num,
                chapter_title=chapter_title,
                content=content[:5000],  # 保留前5000字
                summary=chapter_data.get("summary", ""),
                characters=chapter_data.get("characters", []),
                events=chapter_data.get("events", [])
            )

            split_result.chapters.append(chapter_split)

            # 收集角色
            for char_data in chapter_data.get("characters", []):
                if not any(c.get("name") == char_data.get("name") for c in split_result.characters):
                    split_result.characters.append(char_data)

        self.split_result = split_result

        # 如果有输出目录，保存结果
        if output_dir:
            self._save_split_result(split_result, output_dir)

        return split_result

    def _split_without_ai(self, novel_text: str, novel_title: str) -> NovelSplit:
        """不使用AI的简单分割"""
        chapters = self.split_by_chapters(novel_text)

        split_result = NovelSplit(
            title=novel_title,
            overview="",
            world={},
            characters=[],
            chapters=[]
        )

        for chapter_num, chapter_title, content in chapters:
            chapter_split = ChapterSplit(
                chapter_num=chapter_num,
                chapter_title=chapter_title,
                content=content,
                summary="",
                characters=[],
                events=[]
            )
            split_result.chapters.append(chapter_split)

        return split_result

    def _save_split_result(self, result: NovelSplit, output_dir: str):
        """保存拆解结果到文件"""
        base_dir = Path(output_dir) / result.title
        base_dir.mkdir(parents=True, exist_ok=True)

        # 保存整体信息
        overview = {
            "title": result.title,
            "overview": result.overview,
            "total_chapters": len(result.chapters),
            "total_characters": len(result.characters)
        }

        (base_dir / "overview.json").write_text(
            json.dumps(overview, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # 保存每章
        for chapter in result.chapters:
            chapter_dir = base_dir / f"ch{chapter.chapter_num:02d}_{chapter.chapter_title[:20]}"
            chapter_dir.mkdir(exist_ok=True)

            # 保存章节内容
            (chapter_dir / "chapter_content.txt").write_text(
                chapter.content, encoding='utf-8'
            )

            # 保存章节摘要
            chapter_summary = {
                "chapter_num": chapter.chapter_num,
                "title": chapter.chapter_title,
                "summary": chapter.summary,
                "characters": chapter.characters,
                "events": chapter.events
            }
            (chapter_dir / "chapter_summary.json").write_text(
                json.dumps(chapter_summary, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )

            # 保存角色
            chars_dir = chapter_dir / "characters"
            chars_dir.mkdir(exist_ok=True)

            for char in chapter.characters:
                char_file = chars_dir / f"{char.get('name', 'unknown')}.json"
                char_file.write_text(
                    json.dumps(char, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )

            # 保存事件
            events_dir = chapter_dir / "events"
            events_dir.mkdir(exist_ok=True)

            for i, event in enumerate(chapter.events):
                evt_file = events_dir / f"evt_{i+1:03d}.json"
                evt_file.write_text(
                    json.dumps(event, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )

        print(f"拆解结果已保存到: {base_dir}")

    def export_to_tiandao_format(self, result: NovelSplit) -> Dict:
        """导出为天道系统格式"""
        # 导出世界
        world_data = result.world.copy() if result.world else {}
        world_data["name"] = result.title
        world_data["type"] = "通用"

        # 导出角色
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
                    "characters": ch.characters,
                    "events": ch.events
                }
                for ch in result.chapters
            ]
        }


def create_novel_splitter(api=None) -> NovelSplitter:
    """工厂函数：创建小说拆书器"""
    return NovelSplitter(api=api)