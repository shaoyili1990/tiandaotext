"""
拆书系统测试
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import unittest
import tempfile
import os
from splitter.novel_splitter import (
    NovelSplitter, VolumeSplit, ChapterSplit,
    CharacterSnapshot, EventCard, NovelSplit
)


class TestCharacterSnapshot(unittest.TestCase):
    """角色快照测试"""

    def test_create_snapshot(self):
        snapshot = CharacterSnapshot('张三', 'INTJ', 70, '平静', '想要成功')
        self.assertEqual(snapshot.name, '张三')
        self.assertEqual(snapshot.mbti, 'INTJ')
        self.assertEqual(snapshot.current_y, 70)

    def test_snapshot_to_dict(self):
        snapshot = CharacterSnapshot('李四', 'ENFP', 65, '开心', '追求自由')
        data = snapshot.to_dict()
        self.assertEqual(data['name'], '李四')
        self.assertEqual(data['mbti'], 'ENFP')


class TestEventCard(unittest.TestCase):
    """事件卡测试"""

    def test_create_event(self):
        event = EventCard(
            'evt_001', '吃饭', '饿了', '去餐厅', '吃完回家',
            characters=[{'name': '张三', 'role': '主要'}]
        )
        self.assertEqual(event.title, '吃饭')
        self.assertEqual(len(event.characters), 1)
        self.assertEqual(event.characters[0]['role'], '主要')

    def test_event_to_dict(self):
        event = EventCard('evt_002', '打架', '冲突', '打起来', '两败俱伤')
        data = event.to_dict()
        self.assertEqual(data['title'], '打架')
        self.assertEqual(data['cause'], '冲突')


class TestChapterSplit(unittest.TestCase):
    """章节拆解测试"""

    def test_create_chapter(self):
        snapshot = CharacterSnapshot('王五', 'ISTJ', 60, '紧张', '担心')
        event = EventCard('evt_001', '会议', '开始', '进行中', '结束')

        chapter = ChapterSplit(
            chapter_num=1,
            chapter_title='第1章',
            content='章节内容...',
            summary='章节摘要',
            character_snapshots=[snapshot],
            event_cards=[event]
        )

        self.assertEqual(chapter.chapter_num, 1)
        self.assertEqual(len(chapter.character_snapshots), 1)
        self.assertEqual(len(chapter.event_cards), 1)


class TestVolumeSplit(unittest.TestCase):
    """卷拆解测试"""

    def test_create_volume(self):
        chapter = ChapterSplit(1, '第1章', '内容', '摘要')
        volume = VolumeSplit(1, '第1卷', chapters=[chapter])

        self.assertEqual(volume.volume_num, 1)
        self.assertEqual(len(volume.chapters), 1)


class TestNovelSplitter(unittest.TestCase):
    """拆书器测试"""

    def test_split_by_chapters(self):
        splitter = NovelSplitter()
        text = '''
第1章 开端
这是第一章的内容。

第2章 发展
这是第二章的内容。
        '''
        chapters = splitter.split_by_chapters(text)
        self.assertGreaterEqual(len(chapters), 1)

    def test_split_novel_without_ai(self):
        splitter = NovelSplitter(api=None)
        text = '''
第1卷 起源
第1章 开始
第一章内容。

第2章 继续
第二章内容。

第2卷 发展
第3章 高潮
第三章内容。
        '''
        result = splitter.split_novel(text, '测试小说')

        self.assertEqual(result.title, '测试小说')
        self.assertGreaterEqual(len(result.volumes), 1)
        self.assertGreaterEqual(len(result.chapters), 1)

    def test_save_split_result(self):
        splitter = NovelSplitter(api=None)
        result = NovelSplit(title='测试')
        result.volumes = [
            VolumeSplit(1, '第1卷', chapters=[
                ChapterSplit(1, '第1章', '内容', '摘要')
            ])
        ]
        result.chapters = result.volumes[0].chapters

        with tempfile.TemporaryDirectory() as tmpdir:
            splitter._save_split_result(result, tmpdir)

            # Check files were created
            novel_dir = Path(tmpdir) / '测试'
            self.assertTrue(novel_dir.exists())

            overview = novel_dir / 'overview.json'
            self.assertTrue(overview.exists())


if __name__ == '__main__':
    unittest.main()
