# 次元笔记本拆书计划

## 目标
将《次元笔记本》小说拆解为结构化数据，供天道/人道系统使用

## 目录结构
```
data/novel_split/次元笔记本/
├── 总览/
│   ├── 人物总览/人物总览.md
│   ├── 事件总览/事件总览.md
│   ├── 天道总览/天道总览.md
│   └── 人道总览/人道总览.md
├── 第一卷_少年歌行/ (64章)
├── 第二卷_射雕英雄传/ (43章)
├── 第三卷_过渡/ (4章)
├── 第四卷_笑傲江湖/ (33章)
└── 第五卷_旧地重游/ (13章)
```

## 每章文件清单
每个章节目录下包含：
- `chapter_content.txt` - 原始章节内容
- `spacetime_slice.json` - 时空切片（完整状态）
- `characters/` - 人物快照目录（每人一个.json）
- `events/` - 事件卡目录（每事一个.json）

## AI分析提示词
```
你是一位天道系统分析师。根据小说章节内容，提取：

1. 人物快照（数组，每个角色一个对象）：
   - name: 角色名
   - mbti: MBTI类型（如INTJ、ENTP）
   - base_y: 基础Y值(1-100)
   - current_y: 当前Y值
   - baseline_y: 基线Y值
   - weight: 权重(0-100)
   - role: 角色定位
   - location: 当前位置
   - emotions: 情绪状态{joy, anger, worry, sadness, fear}
   - current_desire: 当前欲望
   - current_state: 当前状态描述

2. 事件卡（数组，每个事件一个对象）：
   - id: 事件ID（如E001_01）
   - title: 事件标题
   - chapter: 章节号
   - cause: 起因
   - process: 经过
   - result: 结果
   - characters_involved: 涉及人物数组
   - character_roles: 人物角色映射
   - type: 事件类型（BREAKTHROUGH/CONFLICT/CAUSAL_CHAIN等）
   - y_value_changes: Y值变化
   - butterfly_effect: 蝴蝶效应描述
   - tiandao_judgment: 天道评判

3. 时空切片（对象）：
   - chapter_title: 章节标题
   - volume: 卷名
   - chapter_number: 章节号
   - word_count: 字数
   - world_state: 世界状态{location, season, weather, atmosphere}
   - characters_present: 出场人物列表
   - tiandao_state: 天道状态{y_value_distribution, triggered_events, causal_chain}
   - rendao_state: 人道状态{weight_distribution, lao_tian_qi_judgments}
   - causal_state: 因果状态{butterfly_effects, chain_reactions}

返回完整JSON格式。
```

## 执行流程
1. 创建目录结构
2. 读取源文件
3. 调用MiniMax API分析每章
4. 保存JSON文件
5. 更新总览

## 技术配置
- API: MiniMax (包月key优先，量计key备用)
- Python path: src
- 工作目录: tiandaotext