"""
天道作家系统 - 主入口
集成天道系统(Y值/MBTI/三大机制/蝴蝶效应)和人道系统(权重关系网/老天气变量)
基于Gradio的Web界面
"""

import os
import sys
import json
import gradio as gr
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from api.minimax_api import MiniMaxAPI, configure_api, get_api
from tiandao_core.core.profile import CharacterProfile
from tiandao_core.core.y_value import YValueSystem
from tiandao_core.core.mbti import MBTISystem
from tiandao_core.rendao.weight_network import WeightNetwork, CharacterClass
from tiandao_core.rendao.lao_tian_qi import LaoTianQi
from tiandao_core.rendao.butterfly_effect import ButterflyEffectSystem, Position3D
from splitter.novel_splitter import NovelSplitter
from continuation.continuation_system import ContinuationSystem
from evolution.evolution_system import EvolutionSystem

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
WORLDS_DIR = DATA_DIR / "worlds"
CHARACTERS_DIR = DATA_DIR / "characters"
EVENTS_DIR = DATA_DIR / "events"
NOVELS_DIR = DATA_DIR / "novels"

# 确保目录存在
for d in [WORLDS_DIR, CHARACTERS_DIR, EVENTS_DIR, NOVELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 配置文件
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


def _get_default_api_key():
    return os.getenv("MINIMAX_PRIMARY_API_KEY", "")


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return {"api_key": _get_default_api_key(), "unified_api": True}


def save_config(config: dict):
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')


def get_all_worlds() -> list:
    worlds = []
    for f in WORLDS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            worlds.append({"name": data.get("name", f.stem), "file": f.name})
        except:
            pass
    return worlds


def get_all_characters() -> list:
    chars = []
    for f in CHARACTERS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            chars.append({
                "name": data.get("name", f.stem),
                "mbti": data.get("mbti", ""),
                "world": data.get("world", "通用"),
                "base_y": data.get("base_y", 50),
                "current_y": data.get("current_y", 50)
            })
        except:
            pass
    return chars


def get_all_events() -> list:
    events = []
    for f in EVENTS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            events.append({"title": data.get("title", f.stem), "type": data.get("type", "剧情")})
        except:
            pass
    return events


# ============================================
# AI API设置
# ============================================

def update_api_key(api_key: str, use_unified: bool = True):
    config = load_config()
    config["api_key"] = api_key
    config["unified_api"] = use_unified
    save_config(config)
    configure_api(api_key)
    return "API Key 已保存"


def test_api_key(api_key: str) -> str:
    api = MiniMaxAPI(api_key)
    result = api.chat("你好，请回复'API配置成功'")
    if "成功" in result or "API" in result:
        return "API Key 有效"
    return f"测试失败: {result[:100]}"


# ============================================
# 世界书管理
# ============================================

def create_world(world_type: str, style: str, tone: str) -> str:
    config = load_config()
    api = get_api(config.get("api_key") or _get_default_api_key())

    result = api.generate_world(world_type, style, tone)

    if "error" in result:
        return f"生成失败: {result['error']}"

    world_name = result.get("name", "未命名世界")
    file_path = WORLDS_DIR / f"{world_name}.json"
    result["created_at"] = str(Path(__file__).parent.parent / "data").split("/")[-1]
    file_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    return f"世界'{world_name}'创建成功！包含{len(result.get('suggested_characters', []))}个推荐角色"


def load_world(world_name: str) -> dict:
    for f in WORLDS_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding='utf-8'))
        if data.get("name") == world_name:
            return data
    return {}


def save_world_edits(original_name: str, edits_json: str) -> str:
    try:
        edits = json.loads(edits_json)
        file_path = WORLDS_DIR / f"{original_name}.json"
        if file_path.exists():
            file_path.write_text(json.dumps(edits, ensure_ascii=False, indent=2), encoding='utf-8')
            return "世界保存成功"
    except Exception as e:
        return f"保存失败: {str(e)}"
    return "保存失败"


def delete_world(world_name: str) -> str:
    file_path = WORLDS_DIR / f"{world_name}.json"
    if file_path.exists():
        file_path.unlink()
        return f"世界'{world_name}'已删除"
    return f"世界'{world_name}'不存在"


# ============================================
# 人物卡管理
# ============================================

def create_character(world_name: str, character_role: str) -> str:
    config = load_config()
    api = get_api(config.get("api_key") or _get_default_api_key())

    result = api.generate_character(world_name, world_name, character_role)

    if "error" in result:
        return f"生成失败: {result['error']}"

    char_name = result.get("name", "未命名角色")
    file_path = CHARACTERS_DIR / f"{char_name}.json"
    result["world"] = world_name
    file_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    return f"角色'{char_name}'创建成功！MBTI: {result.get('mbti', '未知')}, Y值: {result.get('base_y', 50)}"


def load_character(char_name: str) -> dict:
    for f in CHARACTERS_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding='utf-8'))
        if data.get("name") == char_name:
            return data
    return {}


def save_character_edits(original_name: str, edits_json: str) -> str:
    try:
        edits = json.loads(edits_json)
        file_path = CHARACTERS_DIR / f"{original_name}.json"
        if file_path.exists():
            file_path.write_text(json.dumps(edits, ensure_ascii=False, indent=2), encoding='utf-8')
            return "角色保存成功"
    except Exception as e:
        return f"保存失败: {str(e)}"
    return "保存失败"


def delete_character(char_name: str) -> str:
    file_path = CHARACTERS_DIR / f"{char_name}.json"
    if file_path.exists():
        file_path.unlink()
        return f"角色'{char_name}'已删除"
    return f"角色'{char_name}'不存在"


# ============================================
# 事件卡管理
# ============================================

def create_event(world_name: str, event_type: str) -> str:
    config = load_config()
    api = get_api(config.get("api_key") or _get_default_api_key())

    result = api.generate_event(world_name, event_type)

    if "error" in result:
        return f"生成失败: {result['error']}"

    event_title = result.get("title", "未命名事件")
    file_path = EVENTS_DIR / f"{event_title}.json"
    result["world"] = world_name
    result["type"] = event_type
    file_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    return f"事件'{event_title}'创建成功！包含{len(result.get('choices', []))}个选择"


def delete_event(event_title: str) -> str:
    file_path = EVENTS_DIR / f"{event_title}.json"
    if file_path.exists():
        file_path.unlink()
        return f"事件'{event_title}'已删除"
    return f"事件'{event_title}'不存在"


# ============================================
# 小说拆解
# ============================================

def parse_novel(novel_text: str) -> str:
    config = load_config()
    api = get_api(config.get("api_key") or _get_default_api_key())

    result = api.parse_novel(novel_text)

    if "error" in result:
        return f"拆解失败: {result['error']}"

    title = result.get("title", "未命名小说")

    # 保存世界
    world_data = result.get("world", {})
    if world_data:
        world_name = world_data.get("name", title + "的世界")
        world_file = WORLDS_DIR / f"{world_name}.json"
        world_file.write_text(json.dumps(world_data, ensure_ascii=False, indent=2), encoding='utf-8')

    # 保存角色
    for char_data in result.get("characters", []):
        char_name = char_data.get("name", "未命名")
        char_file = CHARACTERS_DIR / f"{char_name}.json"
        char_data["world"] = world_name
        char_file.write_text(json.dumps(char_data, ensure_ascii=False, indent=2), encoding='utf-8')

    return f"""小说拆解成功！

标题：{title}
世界：{world_name}（已保存）
角色：{len(result.get('characters', []))}个（已保存）
事件：{len(result.get('events', []))}个"""


# ============================================
# 大纲生成
# ============================================

def generate_outline(story_idea: str, genre: str) -> str:
    config = load_config()
    api = get_api(config.get("api_key") or _get_default_api_key())

    result = api.generate_outline(story_idea, genre)

    if "error" in result:
        return f"生成失败: {result['error']}"

    return json.dumps(result, ensure_ascii=False, indent=2)


# ============================================
# 创作/续写
# ============================================

def write_content(context: str, world_info: str, character_info: str, genre: str) -> str:
    config = load_config()
    api = get_api(config.get("api_key") or _get_default_api_key())

    result = api.write_continue(context, world_info, character_info, genre)

    return result if result else "创作失败"


def chat_with_ai(prompt: str, system_context: str) -> str:
    config = load_config()
    api = get_api(config.get("api_key") or _get_default_api_key())

    result = api.chat(prompt, system_context)

    return result if result else "AI无响应"


# ============================================
# 天道系统 - Y值/心理计算
# ============================================

def calculate_psychology(character_name: str, situation: str, other_y: int = None) -> str:
    """计算角色对情境的心理反应"""
    char_data = load_character(character_name)
    if not char_data:
        return f"角色'{character_name}'不存在"

    mbti_type = char_data.get("mbti", "INTJ")
    base_y = char_data.get("base_y", 50)

    # 创建角色画像
    profile = CharacterProfile.create(
        character_id=character_name,
        name=character_name,
        base_y=base_y,
        mbti_type=mbti_type
    )

    # 计算反应
    interaction_y = other_y if other_y else None
    result = profile.calculate_response(situation, interaction_y=interaction_y)

    # 检查击穿
    y_report = profile.y_system.get_state_report()
    mbti_profile = profile.mbti_system.get_full_profile()

    output = f"""【{character_name}】心理分析

MBTI: {mbti_type} ({mbti_profile.get('type_name', '')})
当前Y值: {result['y_value']}
基线Y值: {y_report['baseline_y']}
行为倾向: {result['behavioral_tendency']}

情绪状态:
- 效价(正负): {result['emotional_state']['valence']:.2f}
- 唤醒度: {result['emotional_state']['arousal']:.2f}
- 控制感: {result['emotional_state']['dominance']:.2f}

道德修正: {result['moral_adjustment']:+.1f}
溢出警告: {'是' if result['overflow_warning'] else '否'}

触发消息:
{chr(10).join(result['messages'])}
"""

    return output


def analyze_breakthrough(attacker_name: str, defender_name: str) -> str:
    """分析击穿可能性"""
    attacker_data = load_character(attacker_name)
    defender_data = load_character(defender_name)

    if not attacker_data or not defender_data:
        return "角色不存在"

    attacker_y = attacker_data.get("current_y", attacker_data.get("base_y", 50))
    defender_y = defender_data.get("current_y", defender_data.get("base_y", 50))

    delta = attacker_y - defender_y

    # 击穿阈值
    if defender_y < 40:
        threshold = 30
    elif defender_y < 70:
        threshold = 20
    else:
        threshold = 15

    output = f"""【击穿分析】

攻击方: {attacker_name} (Y={attacker_y})
防御方: {defender_name} (Y={defender_y})
Y值差(ΔY): {delta}

击穿阈值: {threshold}
触发击穿: {'是' if delta >= threshold else '否'}

"""

    if delta >= threshold:
        new_y = defender_data.get("baseline_y", 50) - 10
        output += f"""击穿后Y值跃迁:
{defender_name}: Y={defender_y} -> Y={new_y} (基线±10)

击穿影响:
- {defender_name}意识被压制
- 启动补偿机制(1-3节点)
- 补偿结束后启动回弹机制
"""
    else:
        output += f"""未达到击穿阈值
{attacker_name}的气场不足以击穿{defender_name}
"""

    return output


# ============================================
# 人道系统 - 权重/老天气
# ============================================

def evaluate_with_laotianqi(character_name: str, action: str) -> str:
    """使用老天气系统评估行为"""
    char_data = load_character(character_name)
    if not char_data:
        return f"角色'{character_name}'不存在"

    mbti = char_data.get("mbti", "INTJ")
    y_value = char_data.get("current_y", char_data.get("base_y", 50))

    lao_tian_qi = LaoTianQi()
    judgment = lao_tian_qi.evaluate_action(action, mbti, y_value)

    output = f"""【老天气评判】- {character_name}

行为: {action[:50]}...
评估: {judgment.action_value.value}
权重建议: {judgment.weight_suggestion:+.1f}

老天爷之言: "{judgment.message}"

冲突检测:
{chr(10).join(judgment.conflict_hints) if judgment.conflict_hints else '无'}

突破点: {'是' if judgment.is_breaking_point else '否'}
"""

    return output


def show_weight_network() -> str:
    """显示权重关系网"""
    chars = get_all_characters()
    if not chars:
        return "暂无角色"

    weight_network = WeightNetwork()

    # 注册角色
    for char in chars:
        weight_network.register_character(
            name=char["name"],
            character_class=CharacterClass.MAIN,
            custom_weight=char.get("current_y", 50)
        )

    summary = weight_network.get_network_summary()
    rankings = weight_network.get_weight_rankings(10)

    output = f"""【权重关系网】

总角色数: {summary['total_characters']}
平均权重: {summary['average_weight']:.1f}

分类分布:
{chr(10).join([f"- {k}: {v}" for k, v in summary['class_distribution'].items()])}

权重排行:
"""

    for i, (name, weight) in enumerate(rankings, 1):
        output += f"{i}. {name}: {weight}\n"

    return output


# ============================================
# 角色演化
# ============================================

def evolve_character(character_name: str, action: str, context: str = "") -> str:
    """角色演化"""
    api = get_api(load_config().get("api_key") or _get_default_api_key())

    evolution_system = EvolutionSystem(api=api)

    # 创建临时角色
    char_data = load_character(character_name)
    if not char_data:
        return f"角色'{character_name}'不存在"

    profile = CharacterProfile.create(
        character_id=character_name,
        name=character_name,
        base_y=char_data.get("base_y", 50),
        mbti_type=char_data.get("mbti", "INTJ")
    )

    evolution_system.register_character(profile, char_data.get("current_y", 50))

    # 演化
    result = evolution_system.evolve_character(character_name, action, context)

    output = f"""【角色演化】- {character_name}

行为: {action[:50]}...

演化事件:
"""

    for event in result["events"]:
        output += f"- [{event['type']}] {event['description']}\n"

    state = result["current_state"]
    output += f"""
当前状态:
- Y值: {state['y_value']}
- 权重: {state['weight']}
- 分类: {state['character_class']}
- 创伤等级: {state['trauma_level']:.2f}
- 疯狂: {'是' if state['is_insane'] else '否'}
- 脑死亡: {'是' if state['is_brain_dead'] else '否'}
"""

    return output


# ============================================
# Gradio UI
# ============================================

def build_ui():
    """构建Gradio界面"""

    config = load_config()
    configure_api(config.get("api_key") or _get_default_api_key())

    with gr.Blocks(title="天道作家系统 v2.0", theme="default") as app:

        gr.Markdown("# 天道作家系统 v2.0")
        gr.Markdown("*集成天道系统(Y值/MBTI/三大机制/蝴蝶效应)与人道系统(权重关系网/老天气变量)*")

        with gr.Tabs():

            # ============================================
            # Tab 1: AI API设置
            # ============================================
            with gr.TabItem("AI设置"):
                gr.Markdown("## AI API 配置")

                with gr.Row():
                    api_key_input = gr.Textbox(
                        label="MiniMax API Key",
                        value=config.get("api_key") or _get_default_api_key() or "",
                        type="password",
                        scale=3
                    )
                    use_unified = gr.Checkbox(
                        label="统一API模式",
                        value=config.get("unified_api", True),
                        scale=1
                    )

                with gr.Row():
                    save_btn = gr.Button("保存配置", variant="primary")
                    test_btn = gr.Button("测试连接")

                test_output = gr.Textbox(label="测试结果", lines=2)

                save_btn.click(fn=update_api_key, inputs=[api_key_input, use_unified], outputs=test_output)
                test_btn.click(fn=test_api_key, inputs=[api_key_input], outputs=test_output)

            # ============================================
            # Tab 2: 世界书管理
            # ============================================
            with gr.TabItem("世界书"):
                gr.Markdown("## 世界书管理")

                with gr.Row():
                    world_type = gr.Dropdown(
                        label="世界类型",
                        choices=["都市", "玄幻", "科幻", "言情", "悬疑", "仙侠", "自定义"],
                        value="都市"
                    )
                    style = gr.Dropdown(
                        label="风格",
                        choices=["现实", "浪漫", "黑暗", "史诗", "轻松"],
                        value="现实"
                    )
                    tone = gr.Dropdown(
                        label="基调",
                        choices=["中性", "积极", "消极", "悬疑"],
                        value="中性"
                    )

                create_world_btn = gr.Button("AI生成世界", variant="primary")
                world_output = gr.Textbox(label="生成结果", lines=5)

                create_world_btn.click(fn=create_world, inputs=[world_type, style, tone], outputs=world_output)

                gr.Markdown("---")
                gr.Markdown("### 已有的世界")

                worlds_list = gr.Dataframe(headers=["世界名称", "操作"], value=[], interactive=False)

                def refresh_worlds():
                    worlds = get_all_worlds()
                    return [[w["name"], "删除"] for w in worlds]

                refresh_btn = gr.Button("刷新列表")
                refresh_btn.click(fn=refresh_worlds, outputs=worlds_list)

                gr.Markdown("### 编辑世界")
                world_detail = gr.Textbox(label="世界详情(JSON)", lines=10)
                world_load_btn = gr.Button("加载")
                world_save_btn = gr.Button("保存编辑")
                world_edit_output = gr.Textbox(label="操作结果")

                def load_world_detail(name):
                    data = load_world(name)
                    return json.dumps(data, ensure_ascii=False, indent=2) if data else "{}"

                world_load_btn.click(fn=load_world_detail, inputs=worlds_list, outputs=world_detail)

            # ============================================
            # Tab 3: 人物卡管理
            # ============================================
            with gr.TabItem("人物卡"):
                gr.Markdown("## 人物卡管理")

                with gr.Row():
                    char_world = gr.Textbox(label="所属世界", value="通用")
                    char_role = gr.Dropdown(
                        label="角色定位",
                        choices=["主角", "女主", "男主", "配角", "反派", "导师", "神秘人"],
                        value="主角"
                    )

                create_char_btn = gr.Button("AI生成角色", variant="primary")
                char_output = gr.Textbox(label="生成结果", lines=4)

                create_char_btn.click(fn=create_character, inputs=[char_world, char_role], outputs=char_output)

                gr.Markdown("---")
                gr.Markdown("### 已有的角色")

                chars_list = gr.Dataframe(
                    headers=["角色名", "MBTI", "所属世界", "Y值", "操作"],
                    value=[],
                    interactive=False
                )

                def refresh_chars():
                    chars = get_all_characters()
                    return [[c["name"], c.get("mbti", ""), c.get("world", ""), c.get("current_y", ""), "删除"] for c in chars]

                refresh_chars_btn = gr.Button("刷新")
                refresh_chars_btn.click(fn=refresh_chars, outputs=chars_list)

                gr.Markdown("### 编辑角色")
                char_detail = gr.Textbox(label="角色详情(JSON)", lines=10)
                char_load_btn = gr.Button("加载")
                char_save_btn = gr.Button("保存")
                char_edit_output = gr.Textbox(label="操作结果")

                def load_char_detail(name):
                    data = load_character(name)
                    return json.dumps(data, ensure_ascii=False, indent=2) if data else "{}"

                char_load_btn.click(fn=load_char_detail, inputs=chars_list, outputs=char_detail)

            # ============================================
            # Tab 4: 事件卡管理
            # ============================================
            with gr.TabItem("事件卡"):
                gr.Markdown("## 事件卡管理")

                with gr.Row():
                    event_world = gr.Textbox(label="所属世界", value="通用")
                    event_type = gr.Dropdown(
                        label="事件类型",
                        choices=["剧情", "支线", "随机", "高潮", "结局"],
                        value="剧情"
                    )

                create_event_btn = gr.Button("AI生成事件", variant="primary")
                event_output = gr.Textbox(label="生成结果", lines=4)

                create_event_btn.click(fn=create_event, inputs=[event_world, event_type], outputs=event_output)

                gr.Markdown("---")
                gr.Markdown("### 已有的事件")

                events_list = gr.Dataframe(headers=["事件标题", "类型", "操作"], value=[], interactive=False)

                def refresh_events():
                    events = get_all_events()
                    return [[e["title"], e.get("type", ""), "删除"] for e in events]

                refresh_events_btn = gr.Button("刷新")
                refresh_events_btn.click(fn=refresh_events, outputs=events_list)

            # ============================================
            # Tab 5: 小说拆解
            # ============================================
            with gr.TabItem("小说拆解"):
                gr.Markdown("## 小说拆解")
                gr.Markdown("上传小说文本，AI使用天道系统自动拆解为角色卡+世界书+事件卡")

                novel_input = gr.Textbox(
                    label="小说文本",
                    lines=15,
                    placeholder="请粘贴小说文本（支持 txt 格式）..."
                )

                parse_btn = gr.Button("开始拆解", variant="primary")
                parse_output = gr.Textbox(label="拆解结果", lines=10)

                parse_btn.click(fn=parse_novel, inputs=[novel_input], outputs=parse_output)

            # ============================================
            # Tab 6: 天道系统
            # ============================================
            with gr.TabItem("天道系统"):
                gr.Markdown("## 天道系统")
                gr.Markdown("Y值/击穿机制/补偿机制/回弹机制/PTSD检测")

                with gr.TabItem("心理计算"):
                    gr.Markdown("### 角色心理计算")

                    with gr.Row():
                        psy_char = gr.Textbox(label="角色名", value="")
                        psy_situation = gr.Textbox(label="情境描述", value="", lines=2)
                        psy_other_y = gr.Number(label="对方Y值(可选)", value=None)

                    psy_btn = gr.Button("计算心理反应")
                    psy_output = gr.Textbox(label="分析结果", lines=15)

                    psy_btn.click(
                        fn=calculate_psychology,
                        inputs=[psy_char, psy_situation, psy_other_y],
                        outputs=psy_output
                    )

                with gr.TabItem("击穿分析"):
                    gr.Markdown("### 击穿机制分析")

                    with gr.Row():
                        attack_char = gr.Textbox(label="攻击方(高Y)", value="")
                        defend_char = gr.Textbox(label="防御方(低Y)", value="")

                    breakthrough_btn = gr.Button("分析击穿")
                    breakthrough_output = gr.Textbox(label="分析结果", lines=12)

                    breakthrough_btn.click(
                        fn=analyze_breakthrough,
                        inputs=[attack_char, defend_char],
                        outputs=breakthrough_output
                    )

            # ============================================
            # Tab 7: 人道系统
            # ============================================
            with gr.TabItem("人道系统"):
                gr.Markdown("## 人道系统")
                gr.Markdown("老天气变量/权重关系网/角色分类")

                with gr.TabItem("老天气评判"):
                    gr.Markdown("### 老天气行为评判")

                    with gr.Row():
                        ltq_char = gr.Textbox(label="角色名", value="")
                        ltq_action = gr.Textbox(label="行为描述", value="", lines=3)

                    ltq_btn = gr.Button("老天气评判")
                    ltq_output = gr.Textbox(label="评判结果", lines=12)

                    ltq_btn.click(fn=evaluate_with_laotianqi, inputs=[ltq_char, ltq_action], outputs=ltq_output)

                with gr.TabItem("权重网络"):
                    gr.Markdown("### 权重关系网")

                    weight_btn = gr.Button("显示权重网络")
                    weight_output = gr.Textbox(label="权重网络", lines=20)

                    weight_btn.click(fn=show_weight_network, outputs=weight_output)

            # ============================================
            # Tab 8: 角色演化
            # ============================================
            with gr.TabItem("角色演化"):
                gr.Markdown("## 角色演化系统")
                gr.Markdown("行为累积影响Y值/记忆触发状态变化/权重达到阈值触发晋升降级")

                with gr.Row():
                    evo_char = gr.Textbox(label="角色名", value="")
                    evo_action = gr.Textbox(label="行为描述", value="", lines=3)

                evo_context = gr.Textbox(label="情境上下文(可选)", value="", lines=2)

                evo_btn = gr.Button("触发演化")
                evo_output = gr.Textbox(label="演化结果", lines=15)

                evo_btn.click(
                    fn=evolve_character,
                    inputs=[evo_char, evo_action, evo_context],
                    outputs=evo_output
                )

            # ============================================
            # Tab 9: 大纲生成
            # ============================================
            with gr.TabItem("大纲生成"):
                gr.Markdown("## 小说大纲生成")
                gr.Markdown("输入故事灵感，AI生成完整大纲")

                with gr.Row():
                    outline_idea = gr.Textbox(
                        label="故事灵感",
                        lines=5,
                        placeholder="描述你的故事想法..."
                    )
                    outline_genre = gr.Dropdown(
                        label="类型",
                        choices=["都市", "玄幻", "科幻", "言情", "悬疑", "仙侠"],
                        value="都市"
                    )

                gen_outline_btn = gr.Button("生成大纲", variant="primary")
                outline_output = gr.JSON(label="生成的大纲")

                gen_outline_btn.click(fn=generate_outline, inputs=[outline_idea, outline_genre], outputs=outline_output)

            # ============================================
            # Tab 10: 创作助手
            # ============================================
            with gr.TabItem("创作助手"):
                gr.Markdown("## AI创作助手")
                gr.Markdown("输入上下文，让AI帮你续写故事")

                with gr.Row():
                    writing_world = gr.Textbox(label="世界观设定", lines=3, value="")
                    writing_char = gr.Textbox(label="角色设定", lines=3, value="")

                writing_context = gr.Textbox(
                    label="当前剧情",
                    lines=5,
                    placeholder="输入故事开头或当前情节..."
                )

                with gr.Row():
                    writing_genre = gr.Dropdown(
                        label="类型",
                        choices=["都市", "玄幻", "科幻", "言情", "悬疑", "仙侠"],
                        value="都市"
                    )
                    write_btn = gr.Button("AI续写", variant="primary")

                write_output = gr.Textbox(label="续写结果", lines=8)

                write_btn.click(
                    fn=write_content,
                    inputs=[writing_context, writing_world, writing_char, writing_genre],
                    outputs=write_output
                )

                gr.Markdown("---")
                gr.Markdown("### AI对话")

                chat_prompt = gr.Textbox(label="输入", lines=2, placeholder="问AI任何问题...")
                chat_context = gr.Textbox(label="上下文(可选)", lines=2)
                chat_btn = gr.Button("发送")
                chat_output = gr.Textbox(label="AI回复", lines=4)

                chat_btn.click(fn=chat_with_ai, inputs=[chat_prompt, chat_context], outputs=chat_output)

        gr.Markdown("---")
        gr.Markdown("天道作家系统 v2.0 | 基于MiniMax AI | 集成天道/人道系统")

    return app


def main():
    """主入口"""
    app = build_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()