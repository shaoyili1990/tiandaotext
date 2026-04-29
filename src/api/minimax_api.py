"""
天道作家系统 - MiniMax API 调用模块
优先使用包月套餐API，限额后自动切换到按量计费API
集成天道系统(Y值/MBTI/三大机制/蝴蝶效应)
"""

import os
import json
import base64
import time
import httpx
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def _load_keys_from_file() -> dict:
    """从keys.ts文件加载Base64编码的API Key"""
    keys_file = Path(__file__).parent.parent.parent / "keys.ts"
    if not keys_file.exists():
        return {"primary": "", "backup": ""}

    try:
        content = keys_file.read_text(encoding='utf-8').strip()
        lines = content.split('\n')
        if len(lines) >= 2:
            primary = base64.b64decode(lines[0].strip()).decode()
            backup = base64.b64decode(lines[1].strip()).decode()
            return {"primary": primary, "backup": backup}
    except Exception as e:
        print(f"Failed to load keys: {e}")
    return {"primary": "", "backup": ""}


def _get_api_keys():
    """获取API Keys（优先从环境变量，其次从keys.ts文件）"""
    primary = os.getenv("MINIMAX_PRIMARY_API_KEY", "")
    backup = os.getenv("MINIMAX_BACKUP_API_KEY", "")

    if not primary or not backup:
        # 从keys.ts文件加载
        file_keys = _load_keys_from_file()
        primary = primary or file_keys.get("primary", "")
        backup = backup or file_keys.get("backup", "")

    return {"primary": primary, "backup": backup}


# API端点
MINIMAX_API_HOST = os.getenv("MINIMAX_API_HOST", "https://api.minimaxi.com")
CHAT_COMPLETION_URL = f"{MINIMAX_API_HOST}/v1/text/chatcompletion_v2"

# 可用模型列表
AVAILABLE_MODELS = [
    "MiniMax-Text-01",
    "abab6.5s-chat",
]

# 记录切换状态
_last_switch_time = 0
_using_backup = False


class MiniMaxAPI:
    """MiniMax API 调用类 - 自动切换API以节省费用"""

    def __init__(self, api_key: str = ""):
        keys = _get_api_keys()
        self.primary_key = api_key or keys.get("primary", "")
        self.backup_key = keys.get("backup", "")
        self.host = MINIMAX_API_HOST
        self._using_backup = False

    def _get_headers(self, api_key: str) -> dict:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _call_api(self, api_key: str, messages: list, model: str = "MiniMax-Text-01", temperature: float = 0.7, max_tokens: int = 1000) -> dict:
        url = f"{self.host}/v1/text/chatcompletion_v2"
        headers = self._get_headers(api_key)
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _call_with_fallback(self, messages: list, model: str = "MiniMax-Text-01", temperature: float = 0.7, max_tokens: int = 1000) -> str:
        global _last_switch_time, _using_backup

        try:
            data = self._call_api(self.primary_key, messages, model, temperature, max_tokens)
            base_resp = data.get("base_resp", {})

            if base_resp.get("status_code") == 0:
                if self._using_backup:
                    print("📡 已切换回主API（包月套餐）")
                    self._using_backup = False
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")

            status_msg = base_resp.get("status_msg", "")
            if "not support" in status_msg or "limit" in status_msg.lower() or base_resp.get("status_code") in [2061, 2049]:
                if not self._using_backup:
                    print("📡 主API达到限额，自动切换到备用API（按量计费）")
                    self._using_backup = True
                    _using_backup = True
                    _last_switch_time = time.time()

            if self._using_backup:
                data = self._call_api(self.backup_key, messages, model, temperature, max_tokens)
                base_resp = data.get("base_resp", {})
                if base_resp.get("status_code") == 0:
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")

            return f"【错误】API返回: {status_msg}"

        except Exception as e:
            if not self._using_backup:
                print(f"📡 主API异常 ({str(e)[:50]})，切换到备用API")
                self._using_backup = True
                _using_backup = True

            try:
                data = self._call_api(self.backup_key, messages, model, temperature, max_tokens)
                base_resp = data.get("base_resp", {})
                if base_resp.get("status_code") == 0:
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return f"【错误】备用API返回: {base_resp.get('status_msg', str(e))}"
            except Exception as e2:
                return f"【错误】API调用失败: {str(e2)}"

    def set_api_key(self, api_key: str):
        self.primary_key = api_key

    def is_configured(self) -> bool:
        return bool(self.primary_key and len(self.primary_key) > 10)

    def _call(self, messages: list, model: str = "MiniMax-Text-01", temperature: float = 0.7, max_tokens: int = 1000) -> str:
        return self._call_with_fallback(messages, model, temperature, max_tokens)

    def generate_world(self, world_type: str = "urban", style: str = "现实", tone: str = "中性") -> Dict:
        system_prompt = """你是一位资深的小说世界架构师。根据用户输入的信息，生成一个完整的的世界设定。

请以JSON格式返回，包含以下字段：
- name: 世界名称
- overview: 世界概述（200字）
- geography: 地理与社会（500字）
- factions: 势力与组织（400字）
- rules: 规则与法则（300字）
- atmosphere_keywords: 氛围关键词数组（10个）
- suggested_characters: 推荐角色列表
- suggested_events: 推荐事件列表

只返回JSON，不要其他内容。"""

        user_prompt = f"""生成一个{world_type}类型的世界设定。
风格：{style}
基调：{tone}

请生成完整的JSON格式世界设定。"""

        result = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.8, max_tokens=1500)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return {"error": "生成失败", "raw": result}

    def generate_character(self, world_name: str = "", world_type: str = "", character_role: str = "主角") -> Dict:
        system_prompt = """你是一位专业的角色设计师。根据世界设定创建符合MBTI和Y值心理体系的角色。

请以JSON格式返回，包含以下字段：
- name: 角色名称
- mbti: MBTI类型（如INFJ、INTJ等）
- base_y: Y值（心理强度，1-100）
- personality: 性格描述
- appearance: 外貌描述
- background: 背景故事
- motivation: 角色动机
- relationships: 与其他角色的关系

只返回JSON，不要其他内容。"""

        user_prompt = f"""在{world_name}（{world_type}类型）世界中创建角色。
角色定位：{character_role}

请生成完整的JSON格式角色设定。"""

        result = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.7, max_tokens=1200)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return {"error": "生成失败", "raw": result}

    def generate_event(self, world_name: str = "", event_type: str = "剧情") -> Dict:
        system_prompt = """你是一位专业的小说情节设计师。创建引人入胜的剧情事件。

请以JSON格式返回，包含以下字段：
- title: 事件标题
- description: 事件描述
- trigger_conditions: 触发条件列表
- choices: 选择列表（含text和outcome）
- consequences: 后果列表

只返回JSON，不要其他内容。"""

        user_prompt = f"""在{world_name}中创建一个{event_type}类型的事件。

请生成完整的JSON格式事件设定。"""

        result = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.8, max_tokens=1000)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return {"error": "生成失败", "raw": result}

    def parse_novel(self, novel_text: str) -> Dict:
        """拆解小说 - 使用天道系统分析角色和事件"""
        system_prompt = """你是一位专业的小说分析师。使用天道系统分析并拆解小说文本。

天道系统核心概念：
- Y值：人物「主观意识凝练强度」(1-100)，代表精神内核稳定指数
- MBTI：人物「人格骨架」，决定基础心理模式和Y值回弹基线
- 击穿机制：当ΔY(对方Y-自身Y)≥阈值时触发，高Y者对低Y者的意识压制
- 补偿机制：被击穿后的防御性调整，持续1-3个剧情节点
- 回弹机制：补偿结束后Y值回归自身基线

请以JSON格式返回，包含以下字段：
- title: 小说标题
- overview: 故事概述
- world: 世界设定
- characters: 角色列表（含MBTI、base_y、性格描述）
- events: 事件列表（含起因、经过、结果）

只返回JSON，不要其他内容。"""

        text = novel_text[:50000] if len(novel_text) > 50000 else novel_text
        user_prompt = f"使用天道系统分析以下小说，提取关键信息：\n\n{text}"

        result = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.7, max_tokens=2500)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return {"error": "拆解失败", "raw": result[:500]}

    def split_chapter(self, chapter_text: str, chapter_num: int = 1) -> Dict:
        """拆解单章 - 提取角色快照和事件"""
        system_prompt = """你是一位专业的章节分析师。使用天道系统拆解小说章节。

对于输入的章节文本，请提取：

1. 本章出场人物快照（每个角色包含）：
   - name: 角色名
   - mbti: MBTI类型
   - y_value: 当前Y值
   - emotions: 当前情绪状态
   - thoughts: 此刻所思
   - wants: 此刻所求

2. 本章关键事件（每个事件包含）：
   - id: 事件ID
   - title: 事件标题
   - cause: 起因
   - process: 经过
   - result: 结果
   - characters_involved: 涉及角色列表
   - y_value_changes: Y值变化记录

请以JSON格式返回。"""

        text = chapter_text[:20000] if len(chapter_text) > 20000 else chapter_text
        user_prompt = f"分析第{chapter_num}章，提取角色快照和事件：\n\n{text}"

        result = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.7, max_tokens=2000)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return {"error": "章节拆解失败", "raw": result[:500]}

    def generate_outline(self, story_idea: str = "", genre: str = "都市") -> Dict:
        system_prompt = """你是一位专业的小说大纲策划师。根据用户输入的故事灵感，生成完整的小说大纲。

请以JSON格式返回，包含以下字段：
- title: 小说标题
- genre: 类型
- overview: 故事概述
- chapters: 章节列表
- main_characters: 主要角色列表
- plot_twists: 剧情转折点

只返回JSON，不要其他内容。"""

        user_prompt = f"根据以下灵感生成小说大纲：\n类型：{genre}\n灵感：{story_idea}"

        result = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.8, max_tokens=1500)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return {"error": "大纲生成失败", "raw": result}

    def write_continue(
        self,
        context: str = "",
        world_info: str = "",
        character_profiles: str = "",
        genre: str = "都市"
    ) -> str:
        """续写 - 基于角色画像的天道系统续写"""
        system_prompt = """你是一位专业的小说作家。根据给定上下文续写故事。

【核心原则：禁止自由发挥，必须遵循天道/人道系统约束】

【天道系统 - Y值规则】
Y值 = 主观意识凝练强度(0-100)，不代表情绪、血量、好感度
- Y>70：意志极强，不易被动摇
- Y<40：极度脆弱，易被影响、操控、击穿
- Y=40-70：普通人

【击穿阈值】
- Y<40者被击穿：ΔY≥30（对方Y-自身Y）
- Y=40-70者被击穿：ΔY≥20
- Y≥70者被击穿：ΔY≥15

【三大机制 - 必须遵循】
1. 触发机制：Y值瞬间跃迁（被击穿/重大事件/PTSD/情绪极限）
2. 补偿机制：跃迁后启动1-3个剧情节点的防御性缓冲
3. 回弹机制：补偿结束后Y值缓慢回归自身基线

【4种补偿类型】
- 被击穿后补偿：Y值临时下降后回升
- 愧疚爆发补偿：Y值冲高后缓慢回落
- 自我麻痹补偿：Y值被压制到低位
- 依恋填补补偿：Y值围绕基线波动

【MBTI人格骨架】
不同MBTI有固定的心理模式和反应倾向：
- INTJ：理性、内耗、独立性强
- INFP：敏感、共情、理想主义
- ESFJ：热情、关怀、注重和谐
- ISTJ：可靠、务实、传统
- 其他类型依此类推

【天道系统 - 人道规则】
【权重关系网】
角色按重要性分类，权重影响对话/行为频率：
- 主角：权重85-95，对话/行为最多
- 反派：权重80-90，与主角对立
- 主要角色：权重60-80，推动剧情
- 次要角色：权重40-60，偶尔出场
- NPC/龙套：权重0-30，功能性出场

【老天气变量 - 行为评判】
老天爷对角色行为的主观评判：
- 有价值行为：+权重，Y值上升
- 无价值行为：-权重，Y值下降
- 负面行为：严重减权重

【蝴蝶效应传导】
高Y值角色可影响低Y值角色：
- 空间距离越近，影响越大
- Y>70者可能压制/吞噬Y<30者
- Y>70者之间可能产生绝对碰撞

【角色画像格式】
- name: 角色名
- mbti: MBTI类型
- base_y: 基础Y值
- current_y: 当前Y值
- baseline_y: 基线Y值（心理稳定区间）
- weight: 权重
- emotional_state: 当前情绪
- current_desire: 此刻所思所求

请续写约500字的故事内容，直接输出正文。"""

        user_prompt = f"""【世界观】
{world_info}

【角色画像】
{character_profiles}

【当前情节】
{context}

请续写故事，保持风格和角色一致性。严格遵循上述天道/人道系统约束。"""

        return self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.8, max_tokens=1200)

    def evolve_character(
        self,
        character_data: Dict,
        action: str,
        context: str = ""
    ) -> Dict:
        """角色演化 - 基于行为更新角色状态"""
        system_prompt = """你是一位专业的角色演化分析师。根据角色行为判断天道系统中的状态变化。

输入角色当前状态和行为描述，输出：
- y_value_change: Y值变化（正/负）
- emotion_changes: 情绪变化
- motivation_activated: 被激活的动机
- memory_added: 是否产生新记忆
- weight_change: 权重变化（如适用）
- evolution_note: 演化说明

天道系统规则：
- 有价值行为：+1~3点Y值
- 关键行为：+3~5点Y值
- 无价值行为：-5~8点Y值
- 负面行为：-5~10点Y值
- 创伤行为：-8~15点Y值

请以JSON格式返回。"""

        user_prompt = f"""【角色当前状态】
{json.dumps(character_data, ensure_ascii=False, indent=2)}

【角色行为】
{action}

【情境上下文】
{context}

请分析行为对角色的天道系统影响。"""

        result = self._call([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.7, max_tokens=1000)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return {"error": "演化分析失败", "raw": result[:500]}

    def chat(self, prompt: str, system_context: str = "") -> str:
        messages = []
        if system_context:
            messages.append({"role": "system", "content": system_context})
        messages.append({"role": "user", "content": prompt})
        return self._call(messages, temperature=0.8)


# 全局API实例
_api_instance = None


def get_api(api_key: str = "") -> MiniMaxAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = MiniMaxAPI(api_key)
    return _api_instance


def configure_api(api_key: str):
    global _api_instance
    if _api_instance is None:
        _api_instance = MiniMaxAPI(api_key)
    else:
        _api_instance.set_api_key(api_key)