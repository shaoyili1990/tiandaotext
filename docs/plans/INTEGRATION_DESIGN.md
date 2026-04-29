# 天道作家系统(tiandaotext)整合设计文档

> 版本：2.0.0  
> 日期：2026/04/29  
> 状态：规划中

---

## 一、项目概述

### 1.1 整合目标

将`天道系统完整版`的Python核心库整合进`tiandaotext`项目，实现：
- **天道系统**：Y值/MBTI/三大机制/蝴蝶效应
- **人道系统**：权重关系网/老天气变量
- **拆书**：小说结构化拆解
- **续写**：基于角色画像的智能续写
- **演化**：角色状态动态演化

### 1.2 整合原则

1. 完全脱离SillyTavern独立运作
2. 用户操作简便（一键启动）
3. 功能齐全（五大核心功能）
4. 能完整自主运作

---

## 二、现有资源分析

### 2.1 核心代码库

| 路径 | 内容 | 状态 |
|------|------|------|
| `天道系统完整版/tiandao_core/tiandao/` | Y值/MBTI/心理学/记忆/动机/作者系统 | 完整实现 |
| `天道系统完整版/sillytavern_backend/` | SillyTavern插件后端 | 需适配 |
| `tiandaotext/src/systems/` | 简化版系统（y_value/mbti/memory/profile/splitter/continuation） | 基础版本 |
| `tiandao/天道公式/` | 10个公式文档 | 需代码化 |

### 2.2 公式文档清单

1. `01_Y值基础计算公式.txt`
2. `02_全域情绪波动计算公式.txt`
3. `03_击穿机制公式.txt`
4. `04_补偿机制公式.txt`
5. `05_回弹机制公式.txt`
6. `06_MBTI权重系统公式.txt`
7. `07_MBTI具体权重表.txt`
8. `08_人道系统权重公式.txt`
9. `09_记忆系统公式.txt`
10. `10_系统核心公式.txt`

---

## 三、系统架构设计

### 3.1 整体架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户交互层 (Gradio)                         │
│   世界书管理 | 人物卡管理 | 拆书 | 续写 | 演化                      │
└────────────────────────────┬─────────────────────────────────────┘
                               │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      业务逻辑层                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ 世界生成器 │ │ 角色生成器 │ │ 拆书系统  │ │ 续写系统  │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
└────────────────────────────┬─────────────────────────────────────┘
                               │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      核心引擎层 (tiandao_core)                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 天道系统          │ 人道系统          │ 格式适配              │ │
│  │ ───────────────  │ ───────────────  │ ───────────────        │ │
│  │ • Y值系统        │ • 权重关系网      │ • SillyTavern角色卡   │ │
│  │ • MBTI系统       │ • 老天气变量      │ • 世界书格式          │ │
│  │ • 三大机制       │ • 人物分类        │ • 事件卡格式          │ │
│  │ • 蝴蝶效应       │ • 权重升降规则     │ • 角色画像格式        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                               │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      数据持久层 (JSON文件)                         │
│   worlds/ | characters/ | events/ | novels/                       │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 核心模块依赖关系

```
tiandao_core/
├── core/
│   ├── __init__.py
│   ├── y_value.py      ←── 天道系统：Y值/击穿/补偿/回弹
│   ├── mbti.py         ←── 天道系统：16型MBTI/欲望权重/情绪权重
│   ├── psychology.py   ←── 天道系统：五步输出公式/道德修正
│   ├── memory.py       ←── 人道系统：长/短/异常记忆
│   ├── motivation.py   ←── 人道系统：本能/社会/价值三层动机
│   └── author.py       ←── 人道系统：叙事契约/AI边界约束
│
sillytavern_backend/
├── character_api.py   ←── 格式兼容：SillyTavern角色卡解析
├── psychology_api.py   ←── 心理学引擎API封装
└── message_formatter.py ←── 消息格式化
```

---

## 四、功能模块详细设计

### 4.1 天道系统模块 (TiandaoSystem)

#### 4.1.1 Y值系统 (YValueSystem)

**核心功能**：
- 基础Y值计算（1-100）
- 击穿机制（ΔY阈值判断）
- 补偿机制（被击穿后临时调整）
- 回弹机制（回归基线）

**击穿阈值**：
| 自身Y值区间 | 击穿阈值(ΔY) |
|------------|-------------|
| Y < 40（极度脆弱） | ≥ 30 |
| 40 ≤ Y < 70 | ≥ 20 |
| Y ≥ 70（意志极强） | ≥ 15 |

**跃迁规则**：被击穿后，Y值瞬间跃迁为「自身基线±10」

#### 4.1.2 MBTI系统 (MBTISystem)

**核心功能**：
- 16种人格类型定义
- 欲望权重计算（6维度：求生/求知/表达/表现/舒适/情欲）
- 情绪权重计算（7维度：喜/怒/忧/思/悲/恐/惊）
- Big Five特质映射
- 标签自动推断MBTI

**基线区间**：
| MBTI类型 | 基线区间 |
|---------|---------|
| INTJ/ENTJ | 60-75 |
| INFJ/ENFJ/ENTP/ENFP/INTP | 55-70 |
| 其他类型 | 50-65 |

#### 4.1.3 三大机制

**1. 击穿机制 (Breakthrough)**
- 触发条件：ΔY ≥ 击穿阈值
- 效果：Y值瞬间跃迁

**2. 补偿机制 (Compensation)**
- 触发时机：被击穿后
- 持续时间：1-3个剧情节点
- 效果：Y值临时调整（+2~5或-3~8）

**3. 回弹机制 (Rebound)**
- 触发时机：补偿机制结束
- 目标：回归人物基线区间
- 速度：每1-2节点调整±1~2

#### 4.1.4 蝴蝶效应 (ButterflyEffect)

**核心公式**：
- 时空距离计算：`d = sqrt((x1-x2)² + (y1-y2)² + (z1-z2)²)`
- 影响力衰减：`influence = max(0, 100 - d * 10)`
- 高Y值角色可影响低Y值角色

### 4.2 人道系统模块 (RendaoSystem)

#### 4.2.1 权重关系网 (WeightNetwork)

**人物分类与初始权重**：
| 人物类别 | 初始权重范围 |
|---------|------------|
| 主角团 | 85-95 |
| 反派团 | 80-90 |
| 主要人物 | 60-80 |
| 次要人物 | 40-60 |
| NPC | 0-30 |

**权重升降规则**：
- 有价值行为：+1~3点
- 关键行为：+3~5点
- 无价值行为（不符合风格/背景/老天爷价值）：-5~8点
- 负面行为：-5~10点

#### 4.2.2 老天气变量 (LaoTianQi)

**核心功能**：
- 主观倾向评判
- 行为价值评估
- 权重调整建议

### 4.3 拆书模块 (NovelSplitter)

**输入**：小说文本（txt/epub）

**输出结构**：
```
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

**AI提取内容**：
1. 本章出场人物快照（MBTI/情绪/此刻所思所求）
2. 关键事件（起因/经过/结果）
3. 章节概述

### 4.4 续写模块 (ContinuationSystem)

**核心原则**：
1. 基于角色画像生成行为（MBTI/Y值/欲望/情绪）
2. 基于蝴蝶效应传导影响
3. 老天爷变量作为主观评判
4. 不允许AI自由发挥

**续写流程**：
1. 加载当前章节角色状态
2. 构建续写提示词（含天道原则约束）
3. AI生成下一章
4. 自检一致性
5. 应用蝴蝶效应
6. 更新角色状态

### 4.5 演化模块 (EvolutionSystem)

**演化规则**：
1. 角色行为累积影响Y值
2. 记忆满额触发状态变化
3. 权重达到阈值触发类别晋升/降级
4. 异常记忆超限触发疯狂/脑死亡

---

## 五、数据格式设计

### 5.1 世界书格式 (world_*.json)

```json
{
  "name": "世界名称",
  "type": "都市|玄幻|科幻|...",
  "overview": "世界概述",
  "geography": "地理与社会",
  "factions": "势力与组织",
  "rules": "规则与法则",
  "keywords": ["氛围关键词1", "..."],
  "suggested_characters": ["推荐角色1", "..."],
  "initial_events": ["初始事件1", "..."],
  "created_at": "创建时间"
}
```

### 5.2 角色卡格式 (character_*.json)

```json
{
  "name": "角色名",
  "world": "所属世界",
  "mbti": "INTJ",
  "base_y": 65,
  "current_y": 65,
  "baseline_range": [60, 75],
  "character_class": "main|secondary|npc",
  "weight": 85,
  "position": [0, 0, 0],
  "appearance": "外貌特征",
  "personality": "性格描述",
  "background": "背景故事",
  "desires": {
    "survival": 5, "knowledge": 8, "expression": 5,
    "performance": 5, "comfort": 5, "desire": 6
  },
  "emotions": {
    "joy": 5, "anger": 3, "worry": 5, "thought": 7,
    "sadness": 4, "fear": 3, "surprise": 4
  },
  "current_thoughts": "此刻所思",
  "current_wants": "此刻所求",
  "long_term_memories": [],
  "short_term_memories": [],
  "anomalous_memories": []
}
```

### 5.3 事件卡格式 (event_*.json)

```json
{
  "id": "v01_ch01_e001",
  "title": "事件标题",
  "world": "所属世界",
  "type": "剧情|支线|随机|高潮|结局",
  "cause": "起因",
  "process": "经过",
  "result": "结果",
  "characters": {
    "main": ["主要人物"],
    "secondary": ["次要人物"],
    "background": ["龙套人物"]
  },
  "y_value_changes": {
    "角色名": {"old_y": 60, "new_y": 65, "reason": "击穿"}
  }
}
```

---

## 六、API接口设计

### 6.1 MiniMax API封装

```python
class MiniMaxAPI:
    def __init__(self, api_key: str)
    def chat(self, prompt: str, system_context: str = "") -> str
    def generate_world(self, world_type: str, style: str, tone: str) -> dict
    def generate_character(self, world_name: str, character_role: str) -> dict
    def generate_event(self, world_name: str, event_type: str) -> dict
    def parse_novel(self, novel_text: str) -> dict
    def generate_outline(self, story_idea: str, genre: str) -> dict
    def write_continue(self, context: str, world_info: str, character_info: str, genre: str) -> str
```

### 6.2 内部服务接口

```python
class TiandaoService:
    """整合后的天道服务"""

    def calculate_y_value(self, situation: str, context: dict) -> PsychologyOutput
    def apply_breakthrough(self, attacker_y: int, defender_y: int) -> TriggerResult
    def calculate_butterfly_effect(self, source_char: str, event: dict) -> List[dict]
    def evolve_character(self, char_name: str, action: dict) -> CharacterProfile

class RendaoService:
    """整合后的人道服务"""

    def evaluate_action(self, char_name: str, action: dict) -> WeightChange
    def update_weight(self, char_name: str, delta: int) -> int
    def check_class_change(self, char_name: str) -> Optional[str]

class SplitterService:
    """拆书服务"""

    def split_novel(self, novel_path: str, output_dir: str) -> dict
    def extract_characters(self, chapter_content: str) -> List[CharacterProfile]
    def extract_events(self, chapter_content: str) -> List[dict]

class ContinuationService:
    """续写服务"""

    def generate_continuation(self, current_chapter: str, ...) -> dict
    def check_self_consistency(self, content: str) -> dict
```

---

## 七、开发步骤

### 阶段一：核心库整合（1周）

**任务**：
1. 创建`tiandaotext/src/tiandao_core/`目录
2. 复制并适配`天道系统完整版/tiandao_core/tiandao/core/`核心文件
3. 修正import路径和依赖
4. 编写单元测试

**产出**：
- `tiandao_core/core/y_value.py` - Y值系统
- `tiandao_core/core/mbti.py` - MBTI系统
- `tiandao_core/core/psychology.py` - 心理学引擎
- `tiandao_core/core/memory.py` - 记忆系统
- `tiandao_core/core/motivation.py` - 动机系统
- `tiandao_core/core/author.py` - 作者约束系统

### 阶段二：人道系统实现（1周）

**任务**：
1. 实现权重关系网（WeightNetwork）
2. 实现老天气变量（LaoTianQi）
3. 实现蝴蝶效应传导（ButterflyEffect）
4. 整合天道与人道系统

**产出**：
- `tiandao_core/rendao/weight_network.py`
- `tiandao_core/rendao/lao_tian_qi.py`
- `tiandao_core/rendao/butterfly_effect.py`

### 阶段三：业务逻辑层实现（1周）

**任务**：
1. 适配`tiandaotext/src/systems/`现有代码
2. 实现世界/角色/事件生成器
3. 实现拆书系统（基于AI提取）
4. 实现续写系统（基于角色画像）

**产出**：
- `tiandaotext/src/generators/world_generator.py`
- `tiandaotext/src/generators/character_generator.py`
- `tiandaotext/src/generators/event_generator.py`
- `tiandaotext/src/splitter/novel_splitter.py`
- `tiandaotext/src/continuation/continuation_system.py`

### 阶段四：UI与集成（1周）

**任务**：
1. 更新Gradio UI，整合天道/人道系统可视化
2. 添加演化功能Tab
3. 添加角色状态监控面板
4. 完善数据导入/导出

**产出**：
- 更新的`main.py`（新增演化Tab）
- `docs/plans/USER_GUIDE.md`

### 阶段五：测试与优化（1周）

**任务**：
1. 编写集成测试
2. 性能优化
3. 错误处理完善
4. 文档完善

---

## 八、技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| Web框架 | Gradio | 简单易用，AI友好 |
| AI服务 | MiniMax API | 统一供应者 |
| 数据存储 | JSON文件 | 轻量级，无需数据库 |
| 格式兼容 | SillyTavern V2 | 角色卡格式 |
| 依赖管理 | pip/uv | Python包管理 |
| 核心库 | tiandao_core | 复用完整版代码 |

---

## 九、目录结构（整合后）

```
tiandaotext/
├── SPEC.md                          # 项目规格文档
├── README.md                        # 项目说明
├── requirements.txt                 # Python依赖
│
├── src/
│   ├── main.py                      # Gradio主入口
│   ├── config.py                    # 配置管理
│   │
│   ├── tiandao_core/                # 核心库（从完整版复制）
│   │   ├── __init__.py
│   │   ├── core/                    # 天道系统核心
│   │   │   ├── __init__.py
│   │   │   ├── y_value.py           # Y值系统
│   │   │   ├── mbti.py              # MBTI系统
│   │   │   ├── psychology.py        # 心理学引擎
│   │   │   ├── memory.py            # 记忆系统
│   │   │   ├── motivation.py        # 动机系统
│   │   │   └── author.py            # 作者约束系统
│   │   │
│   │   ├── rendao/                  # 人道系统
│   │   │   ├── __init__.py
│   │   │   ├── weight_network.py    # 权重关系网
│   │   │   ├── lao_tian_qi.py       # 老天气变量
│   │   │   └── butterfly_effect.py  # 蝴蝶效应
│   │   │
│   │   └── adapters/                # 格式适配器
│   │       ├── __init__.py
│   │       ├── character_card.py    # SillyTavern角色卡
│   │       ├── world_book.py        # 世界书格式
│   │       └── event_card.py        # 事件卡格式
│   │
│   ├── generators/                  # AI生成器
│   │   ├── __init__.py
│   │   ├── world_generator.py
│   │   ├── character_generator.py
│   │   ├── event_generator.py
│   │   └── outline_generator.py
│   │
│   ├── splitter/                    # 拆书系统
│   │   ├── __init__.py
│   │   └── novel_splitter.py
│   │
│   ├── continuation/                # 续写系统
│   │   ├── __init__.py
│   │   └── continuation_system.py
│   │
│   ├── evolution/                   # 演化系统
│   │   ├── __init__.py
│   │   └── evolution_system.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── minimax_api.py
│   │
│   └── web/                        # Web相关
│       └── ...
│
├── config/
│   └── prompts/                    # AI提示词模板
│       ├── world_gen.md
│       ├── character_gen.md
│       ├── novel_parse.md
│       ├── continuation.md
│       └── evolution.md
│
├── data/
│   ├── worlds/                     # 世界书存储
│   ├── characters/                 # 人物卡存储
│   ├── events/                    # 事件卡存储
│   └── novels/                    # 小说拆解结果
│
├── docs/
│   ├── USER_GUIDE.md              # 用户指南
│   ├── DEVELOPER_GUIDE.md          # 开发者指南
│   └── plans/                     # 设计文档
│       └── INTEGRATION_DESIGN.md  # 本文档
│
└── tests/
    ├── test_tiandao_core.py
    ├── test_generators.py
    └── test_integration.py
```

---

## 十、验收标准

| 功能 | 验收条件 |
|------|----------|
| Y值计算 | 输入情境，输出正确的Y值和情绪状态 |
| MBTI权重 | 16种MBTI类型有正确的欲望/情绪权重 |
| 击穿机制 | ΔY达到阈值时触发正确跃迁 |
| 拆书 | 上传小说，自动拆解为角色+世界+事件 |
| 续写 | 基于角色画像生成符合人意的续写 |
| 演化 | 角色行为累积导致状态/权重变化 |
| 脱离SillyTavern | 独立运行，无外部依赖 |
| 用户友好 | 一键启动，5分钟内可用 |

---

## 附录：公式文件清单

| 文件名 | 内容摘要 |
|--------|---------|
| 01_Y值基础计算公式.txt | 基础Y有效 = (基础Y + 关系分 + 压力分 + 利弊差) / 100 |
| 02_全域情绪波动计算公式.txt | 核心项/普通项计算，盈满而溃公式 |
| 03_击穿机制公式.txt | 击穿阈值规则表，跃迁规则 |
| 04_补偿机制公式.txt | 补偿规则：被击穿后/愧疚爆发/自我麻痹/依恋填补 |
| 05_回弹机制公式.txt | 回弹目标/速度/特殊情况 |
| 06_MBTI权重系统公式.txt | 欲望/情绪权重与MBTI维度映射 |
| 07_MBTI具体权重表.txt | 16种MBTI类型的详细权重值 |
| 08_人道系统权重公式.txt | 人物分类/权重升降规则 |
| 09_记忆系统公式.txt | 记忆数量上限/更新规则/异常惩罚 |
| 10_系统核心公式.txt | 系统=先天本能+后天参数+实时计算 |

---

**文档版本**：2.0.0  
**下一步行动**：
1. 阶段一：整合tiandao_core核心库
2. 阶段二：实现人道系统模块
3. 阶段三：完成业务逻辑层
4. 阶段四：UI与集成
5. 阶段五：测试与优化
