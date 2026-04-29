# tiandaotext 任务规划

## 项目概述
基于用户天道系统的完整写作辅助工具，包含拆书/续写/演化三大功能。

## 任务清单

### P0 - 核心系统完成度检查 ✅
| 任务 | 状态 | 验证 |
|------|------|------|
| 天道核心(Y值/MBTI/画像) | ✅ 完成 | 12个单元测试通过 |
| 人道核心(权重/老天气/蝴蝶) | ✅ 完成 | 单元测试通过 |
| 拆书系统 | ✅ 完成 | 9个单元测试通过，支持卷/章/快照/事件卡 |
| 续写系统 | ✅ 完成 | check_physics_theorems签名正确 |
| 演化系统 | ✅ 完成 | 单元测试通过 |
| Gradio界面 | ✅ 完成 | 可导入构建 |
| 测试覆盖 | ✅ 完成 | 21个测试用例通过 |

### P1 - 拆书系统完善 ✅ 已完成
- [x] 添加卷(Volume)的层级结构
- [x] 添加CharacterSnapshot dataclass
- [x] 添加EventCard dataclass(含人物分类字段)
- [x] 修改split_novel支持卷分割
- [x] 修改_save_split_result按卷保存

### P2 - 续写系统修复 ✅ 已验证
- [x] check_physics_theorems签名正确，无需修复

### P3 - 测试覆盖 ✅ 已完成
- [x] 天道核心单元测试 (12 tests)
- [x] 拆书系统单元测试 (9 tests)

## 验收标准

### 拆书系统
```
输出结构:
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
```

### 续写系统
- 角色行为符合MBTI/Y值设定
- 蝴蝶效应正确传导
- 老天气评判记录

### 演化系统
- Y值变化正确
- 记忆累积触发状态变化
- 权重阈值触发分类变化

## 进度
- 2026-04-29: 完成核心模块，修复import问题，提交2个commit
- 2026-04-29: 自检发现问题，开始修复拆书系统