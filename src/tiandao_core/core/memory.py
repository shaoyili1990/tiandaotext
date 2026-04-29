"""
Memory System - 记忆系统

记忆类型 (5型记忆):
1. 情景记忆: 具体事件的时间、地点、人物、行为
2. 程序记忆: 技能、习惯、身体记忆
3. 语义记忆: 概念、知识、意义理解
4. 情绪记忆: 情感印记和身体反应
5. 感觉记忆: 感官体验的即时印记

PTSD机制:
- 闪回记忆: 创伤场景的强制重演
- 异常情绪记忆: 过度强烈的情绪反应
- 回避记忆: 对创伤相关刺激的回避
- 负性认知记忆: 消极的自我/世界认知

公式:
- 记忆强度 = 情绪强度 × 重复次数 × 重要性
- PTSD触发 = 当前事件相似度 × 历史创伤强度
- 记忆衰减 = 基础衰减率 / (情绪印记深度 + 1)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime
import math


class MemoryType(Enum):
    """记忆类型枚举"""
    EPISODIC = "episodic"       # 情景记忆
    PROCEDURAL = "procedural"  # 程序记忆
    SEMANTIC = "semantic"      # 语义记忆
    EMOTIONAL = "emotional"     # 情绪记忆
    SENSORY = "sensory"         # 感觉记忆


@dataclass
class MemoryNode:
    """记忆节点"""
    id: str
    memory_type: MemoryType
    content: str                    # 记忆内容
    timestamp: datetime
    emotional_intensity: float      # 情绪强度 [0-1]
    importance: float               # 重要性 [0-1]
    associations: List[str] = field(default_factory=list)  # 关联记忆ID
    tags: Set[str] = field(default_factory=set)            # 标签
    access_count: int = 0           # 访问次数
    last_access: Optional[datetime] = None

    # PTSD相关
    is_traumatic: bool = False
    trauma_level: float = 0.0       # 创伤等级 [0-1]
    triggers: List[str] = field(default_factory=list)      # 触发关键词

    @property
    def strength(self) -> float:
        """
        计算记忆强度
        记忆强度 = 情绪强度 × 重复次数 × 重要性
        """
        return self.emotional_intensity * (1 + math.log1p(self.access_count)) * self.importance

    @property
    def decay_rate(self) -> float:
        """
        计算记忆衰减率
        记忆衰减 = 基础衰减率 / (情绪印记深度 + 1)
        情绪印记深的记忆衰减慢
        """
        base_decay = 0.1
        emotional_anchor = self.emotional_intensity * self.trauma_level
        return base_decay / (emotional_anchor + 1)


@dataclass
class MemoryContext:
    """记忆上下文"""
    location: Optional[str] = None
    participants: List[str] = field(default_factory=list)
    situation: Optional[str] = None
    time_period: Optional[str] = None


@dataclass
class MemoryRetrieval:
    """记忆检索结果"""
    memory: MemoryNode
    relevance: float                # 相关度 [0-1]
    trigger_type: Optional[str] = None


class MemorySystem:
    """
    记忆系统 - 5型记忆与PTSD机制

    核心功能:
    1. 5种记忆类型的存储与检索
    2. 记忆强度与衰减计算
    3. PTSD扳机检测与闪回
    4. 记忆关联网络
    5. 异常记忆惩罚机制
    """

    # 基础衰减率
    BASE_DECAY_RATE = 0.1

    # PTSD相关配置
    PTSD_TRIGGER_THRESHOLD = 0.6    # PTSD触发阈值
    FLASHBACK_PROBABILITY = 0.3     # 闪回概率

    def __init__(self):
        self.memories: Dict[str, MemoryNode] = {}
        self.memory_sequence: List[str] = []  # 按时间顺序的记忆ID
        self.trauma_triggers: Dict[str, List[str]] = {}  # 触发词 -> 记忆ID

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        emotional_intensity: float = 0.5,
        importance: float = 0.5,
        context: Optional[MemoryContext] = None,
        tags: Optional[Set[str]] = None,
        is_traumatic: bool = False,
        trauma_level: float = 0.0,
        triggers: Optional[List[str]] = None
    ) -> MemoryNode:
        """
        添加新记忆

        参数:
        - content: 记忆内容
        - memory_type: 记忆类型
        - emotional_intensity: 情绪强度 [0-1]
        - importance: 重要性 [0-1]
        - context: 记忆上下文
        - tags: 标签
        - is_traumatic: 是否为创伤记忆
        - trauma_level: 创伤等级 [0-1]
        - triggers: PTSD触发关键词
        """
        memory_id = self._generate_memory_id()

        memory = MemoryNode(
            id=memory_id,
            memory_type=memory_type,
            content=content,
            timestamp=datetime.now(),
            emotional_intensity=emotional_intensity,
            importance=importance,
            tags=tags or set(),
            is_traumatic=is_traumatic,
            trauma_level=trauma_level,
            triggers=triggers or []
        )

        # 添加关联标记
        if context:
            if context.location:
                memory.tags.add(f"loc:{context.location}")
            if context.situation:
                memory.tags.add(f"sit:{context.situation}")
            memory.participants = context.participants

        # 存储记忆
        self.memories[memory_id] = memory
        self.memory_sequence.append(memory_id)

        # 注册PTSD触发器
        if is_traumatic and triggers:
            for trigger in triggers:
                if trigger not in self.trauma_triggers:
                    self.trauma_triggers[trigger] = []
                self.trauma_triggers[trigger].append(memory_id)

        return memory

    def retrieve(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        include_traumatic: bool = True
    ) -> List[MemoryRetrieval]:
        """
        检索相关记忆

        返回与查询相关的记忆列表，按相关度排序
        """
        results = []

        for memory in self.memories.values():
            # 过滤类型
            if memory_types and memory.memory_type not in memory_types:
                continue

            # 过滤创伤记忆
            if not include_traumatic and memory.is_traumatic:
                continue

            # 计算相关度
            relevance = self._calculate_relevance(query, memory)

            if relevance > 0:
                results.append(MemoryRetrieval(
                    memory=memory,
                    relevance=relevance,
                    trigger_type="trauma" if memory.is_traumatic else None
                ))

        # 排序并限制结果
        results.sort(key=lambda x: (x.relevance, x.memory.strength), reverse=True)
        return results[:limit]

    def _calculate_relevance(self, query: str, memory: MemoryNode) -> float:
        """计算查询与记忆的相关度"""
        query_lower = query.lower()
        relevance = 0.0

        # 内容匹配
        if query_lower in memory.content.lower():
            relevance += 0.5

        # 标签匹配
        for tag in memory.tags:
            if query_lower in tag.lower():
                relevance += 0.3

        # 触发词匹配
        for trigger in memory.triggers:
            if query_lower in trigger.lower():
                relevance += 0.4

        # 关联匹配
        for assoc_id in memory.associations:
            if assoc_id in self.memories:
                assoc = self.memories[assoc_id]
                if query_lower in assoc.content.lower():
                    relevance += 0.2

        return min(relevance, 1.0)

    def check_ptsd_triggers(
        self,
        event_description: str,
        current_y: int
    ) -> Tuple[bool, List[MemoryRetrieval], float]:
        """
        检查PTSD触发

        返回:
        - 是否触发
        - 触发的记忆列表
        - 触发强度
        """
        triggered_memories = []

        for memory in self.memories.values():
            if memory.is_traumatic:
                # 计算相似度
                similarity = self._calculate_relevance(event_description, memory)

                if similarity >= self.PTSD_TRIGGER_THRESHOLD:
                    # PTSD触发强度 = 当前事件相似度 × 历史创伤强度
                    # 异常情绪记忆惩罚: 记忆越强烈，情绪反应越过度
                    trigger_strength = similarity * memory.trauma_level

                    # Y值影响: 低Y值更易被触发
                    y_factor = 1.0 if current_y >= 50 else (1.0 + (50 - current_y) / 50)
                    trigger_strength *= y_factor

                    triggered_memories.append(MemoryRetrieval(
                        memory=memory,
                        relevance=similarity,
                        trigger_type="ptsd"
                    ))

        # 判断是否触发
        if triggered_memories:
            avg_strength = sum(m.relevance * m.memory.trauma_level for m in triggered_memories) / len(triggered_memories)
            return True, triggered_memories, min(avg_strength, 1.0)

        return False, [], 0.0

    def get_abnormal_memory_penalty(self, memory_type: MemoryType) -> float:
        """
        获取异常记忆惩罚

        PTSD/异常情绪记忆会获得惩罚系数:
        - 情绪记忆过强惩罚: 0.8
        - 感觉记忆失真惩罚: 0.7
        - 闪回记忆惩罚: 0.6
        """
        penalties = {
            MemoryType.EMOTIONAL: 0.8,
            MemoryType.SENSORY: 0.7,
            MemoryType.EPISODIC: 0.9,
        }
        return penalties.get(memory_type, 1.0)

    def access_memory(self, memory_id: str) -> Optional[MemoryNode]:
        """访问记忆，增加访问计数"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            memory.access_count += 1
            memory.last_access = datetime.now()
            return memory
        return None

    def decay_memories(self, time_delta_days: float) -> int:
        """
        记忆衰减处理

        返回被删除的记忆数量
        """
        decay_factor = time_delta_days * self.BASE_DECAY_RATE
        removed_count = 0

        # 标记需要删除的记忆
        to_remove = []

        for memory in self.memories.values():
            # 创伤记忆不衰减
            if memory.is_traumatic:
                continue

            # 计算当前衰减率
            current_decay = decay_factor / (memory.decay_rate + 1)

            # 更新重要性
            memory.importance = max(0.1, memory.importance - current_decay * 0.1)

            # 情绪强度逐渐减弱
            memory.emotional_intensity = max(0.0, memory.emotional_intensity - current_decay * 0.05)

            # 重要性低于阈值时标记删除
            if memory.importance < 0.15 and memory.access_count == 0:
                to_remove.append(memory.id)

        # 删除低价值记忆
        for memory_id in to_remove:
            del self.memories[memory_id]
            self.memory_sequence.remove(memory_id)
            removed_count += 1

        return removed_count

    def get_memory_summary(self, memory_type: Optional[MemoryType] = None) -> Dict:
        """获取记忆摘要"""
        memories = list(self.memories.values())

        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        total_strength = sum(m.strength for m in memories)
        traumatic_count = sum(1 for m in memories if m.is_traumatic)

        return {
            "total_memories": len(memories),
            "traumatic_memories": traumatic_count,
            "average_strength": total_strength / len(memories) if memories else 0,
            "memory_types": {
                mt.value: sum(1 for m in memories if m.memory_type == mt)
                for mt in MemoryType
            }
        }

    def _generate_memory_id(self) -> str:
        """生成唯一记忆ID"""
        return f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.memories)}"


def create_memory_system() -> MemorySystem:
    """工厂函数：创建记忆系统"""
    return MemorySystem()