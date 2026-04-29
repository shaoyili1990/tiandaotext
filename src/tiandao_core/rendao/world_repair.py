"""
WorldRepair - 世界性整体干涉系统

基于 Coze 干涉理论：
- 用户修改某内容 → 触发天道/人道整体修复
- 不存在平行时空，只讨论当下影响力和滚雪球
- 变数产生更多变数，连锁反应

核心原则：
1. 整体性：修改必须联动所有相关变量
2. 实时性：当下生效，无延迟
3. 确定性：天道无随机
4. 滚雪球：一个变数触发更多变数
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime
from enum import Enum


class RepairType(Enum):
    """修复类型"""
    CHARACTER_UPDATE = "character_update"      # 角色更新
    Y_VALUE_CHANGE = "y_value_change"          # Y值变化
    WEIGHT_ADJUSTMENT = "weight_adjustment"     # 权重调整
    RELATIONSHIP_CHANGE = "relationship_change" # 关系变化
    TIMELINE_REVISION = "timeline_revision"     # 时间线修正
    EVENT_MODIFICATION = "event_modification"   # 事件修改
    WORLD_STATE_CHANGE = "world_state_change"  # 世界状态变化


@dataclass
class RepairOperation:
    """修复操作"""
    operation_id: str
    repair_type: RepairType
    target: str                          # 操作目标（角色名/事件ID等）
    old_value: Any
    new_value: Any
    reason: str                          # 修复原因
    timestamp: str
    affected_variables: List[str] = field(default_factory=list)  # 受影响的变量
    propagated: bool = False             # 是否已传导


@dataclass
class WorldRepairContext:
    """世界修复上下文"""
    trigger_user_modification: bool       # 是否由用户修改触发
    modification_point: str              # 修改点描述
    original_change: Any                # 原始变更
    repair_scope: Set[str] = field(default_factory=set)  # 修复范围
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class WorldRepair:
    """
    世界性整体干涉系统

    当用户修改某内容时，天道和人道必须进行世界性修复
    确保所有相关变量同步更新，不存在孤立变化
    """

    def __init__(self, three_layer_system=None):
        self.three_layer_system = three_layer_system
        self.repair_history: List[RepairOperation] = []
        self.repair_counter = 0

        # 修复回调函数
        self.repair_hooks: Dict[RepairType, List[Callable]] = {
            repair_type: [] for repair_type in RepairType
        }

    def _generate_operation_id(self) -> str:
        """生成操作ID"""
        self.repair_counter += 1
        return f"REPAIR_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.repair_counter}"

    def register_repair_hook(self, repair_type: RepairType, callback: Callable):
        """注册修复回调"""
        if repair_type not in self.repair_hooks:
            self.repair_hooks[repair_type] = []
        self.repair_hooks[repair_type].append(callback)

    def trigger_world_repair(
        self,
        repair_type: RepairType,
        target: str,
        old_value: Any,
        new_value: Any,
        reason: str,
        context: Optional[WorldRepairContext] = None
    ) -> List[RepairOperation]:
        """
        触发世界性修复

        当用户修改某内容时，调用此方法进行整体修复
        """
        operation_id = self._generate_operation_id()

        # 识别受影响的变量
        affected = self._identify_affected_variables(target, repair_type, new_value)

        # 创建修复操作
        operation = RepairOperation(
            operation_id=operation_id,
            repair_type=repair_type,
            target=target,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            timestamp=datetime.now().isoformat(),
            affected_variables=list(affected)
        )

        # 记录修复历史
        self.repair_history.append(operation)

        # 通知回调
        self._notify_hooks(repair_type, operation)

        # 滚雪球：触发连锁修复
        snowball_effects = self._trigger_snowball_effect(operation)
        all_operations = [operation] + snowball_effects

        return all_operations

    def _identify_affected_variables(
        self,
        target: str,
        repair_type: RepairType,
        new_value: Any
    ) -> Set[str]:
        """
        识别受影响的变量

        这是整体干涉的核心 - 必须找出所有相关变量
        """
        affected = {target}

        if self.three_layer_system is None:
            return affected

        # 根据修复类型识别相关变量
        if repair_type == RepairType.CHARACTER_UPDATE:
            # 角色更新影响Y值、权重、关系
            if target in self.three_layer_system.y_value_rules:
                affected.add(f"y_value:{target}")
            if target in self.three_layer_system.weight_network.characters:
                affected.add(f"weight:{target}")
            # 影响因果蝴蝶层的传导
            affected.add(f"butterfly_propagation:{target}")

        elif repair_type == RepairType.Y_VALUE_CHANGE:
            # Y值变化影响击穿阈值、补偿机制
            current_y = new_value
            if current_y < 40:
                affected.add(f"breakthrough_threshold:{target}:30")
            elif current_y < 70:
                affected.add(f"breakthrough_threshold:{target}:20")
            else:
                affected.add(f"breakthrough_threshold:{target}:15")
            # 触发天道层检测
            affected.add(f"tiandao_detection:{target}")

        elif repair_type == RepairType.WEIGHT_ADJUSTMENT:
            # 权重变化影响角色分类、对话频率
            affected.add(f"character_class:{target}")
            affected.add(f"butterfly_weight:{target}")

        elif repair_type == RepairType.EVENT_MODIFICATION:
            # 事件修改影响所有涉及角色
            affected.add(f"event_chain:{target}")
            # 时空位置可能需要更新
            affected.add(f"spacetime_update:{target}")

        return affected

    def _trigger_snowball_effect(self, operation: RepairOperation) -> List[RepairOperation]:
        """
        滚雪球效应

        一个变数触发更多变数，连锁反应
        """
        snowball_ops = []

        if self.three_layer_system is None:
            return snowball_ops

        # 根据操作类型触发连锁反应
        if operation.repair_type == RepairType.Y_VALUE_CHANGE:
            # Y值变化可能触发蝴蝶效应
            new_y = operation.new_value

            # 检查是否需要触发补偿机制
            if new_y < 40 or new_y > 70:
                # 可能触发补偿
                compensation_op = self._create_linked_operation(
                    operation.target,
                    RepairType.Y_VALUE_CHANGE,
                    new_y,
                    new_y - 5 if new_y < 40 else new_y + 5,
                    "补偿机制触发: Y值超出正常区间"
                )
                snowball_ops.append(compensation_op)

            # 高Y值角色可能影响低Y值角色
            if new_y > 70:
                # 检查附近低Y值角色
                for char_name, rules in self.three_layer_system.y_value_rules.items():
                    if char_name != operation.target:
                        target_y = rules.get("current_y", 50)
                        if target_y < 30:
                            # 可能触发吞噬效应
                            absorption_op = self._create_linked_operation(
                                char_name,
                                RepairType.Y_VALUE_CHANGE,
                                target_y,
                                max(1, target_y - 5),
                                f"被{operation.target}压制，Y值下降"
                            )
                            snowball_ops.append(absorption_op)

        elif operation.repair_type == RepairType.WEIGHT_ADJUSTMENT:
            # 权重变化可能触发角色分类调整
            if operation.new_value >= 85:
                # 可能晋升为主角
                promotion_op = self._create_linked_operation(
                    operation.target,
                    RepairType.WEIGHT_ADJUSTMENT,
                    operation.new_value,
                    operation.new_value,
                    "权重达到主角标准，分类晋升"
                )
                snowball_ops.append(promotion_op)

        # 传播到蝴蝶效应层
        if operation.affected_variables:
            for var in operation.affected_variables:
                if var.startswith("butterfly_"):
                    self.three_layer_system.trigger_y_value_change(
                        operation.target,
                        -3 if operation.new_value < operation.old_value else 3,
                        f"连锁反应: {operation.reason}"
                    )

        return snowball_ops

    def _create_linked_operation(
        self,
        target: str,
        repair_type: RepairType,
        old_value: Any,
        new_value: Any,
        reason: str
    ) -> RepairOperation:
        """创建关联操作"""
        self.repair_counter += 1
        return RepairOperation(
            operation_id=f"REPAIR_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.repair_counter}",
            repair_type=repair_type,
            target=target,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            timestamp=datetime.now().isoformat(),
            affected_variables=[target],
            propagated=False
        )

    def _notify_hooks(self, repair_type: RepairType, operation: RepairOperation):
        """通知修复回调"""
        if repair_type in self.repair_hooks:
            for callback in self.repair_hooks[repair_type]:
                try:
                    callback(operation)
                except Exception as e:
                    print(f"Repair hook error: {e}")

    def apply_user_modification(
        self,
        modification_type: str,
        target: str,
        old_value: Any,
        new_value: Any,
        reason: str = ""
    ) -> Dict:
        """
        应用用户修改并进行世界性修复

        这是整体干涉的入口点
        """
        context = WorldRepairContext(
            trigger_user_modification=True,
            modification_point=f"{modification_type}:{target}",
            original_change=new_value
        )

        # 根据修改类型选择修复类型
        repair_type_map = {
            "character": RepairType.CHARACTER_UPDATE,
            "y_value": RepairType.Y_VALUE_CHANGE,
            "weight": RepairType.WEIGHT_ADJUSTMENT,
            "event": RepairType.EVENT_MODIFICATION,
            "relationship": RepairType.RELATIONSHIP_CHANGE,
        }

        repair_type = repair_type_map.get(modification_type, RepairType.WORLD_STATE_CHANGE)

        # 触发世界性修复
        operations = self.trigger_world_repair(
            repair_type=repair_type,
            target=target,
            old_value=old_value,
            new_value=new_value,
            reason=reason or f"用户修改: {modification_type}",
            context=context
        )

        # 执行天道和人道反馈
        if self.three_layer_system:
            for op in operations:
                self.three_layer_system.lao_tian_qi_judgment(
                    character_name=op.target,
                    action=f"世界性修复: {op.reason}"
                )

        return {
            "repair_triggered": True,
            "operations_count": len(operations),
            "operations": [
                {
                    "id": op.operation_id,
                    "type": op.repair_type.value,
                    "target": op.target,
                    "old": op.old_value,
                    "new": op.new_value,
                    "affected": op.affected_variables
                }
                for op in operations
            ]
        }

    def get_repair_summary(self) -> Dict:
        """获取修复摘要"""
        repair_counts = {}
        for op in self.repair_history:
            repair_counts[op.repair_type.value] = repair_counts.get(op.repair_type.value, 0) + 1

        return {
            "total_repairs": len(self.repair_history),
            "repair_distribution": repair_counts,
            "recent_repairs": [
                {
                    "id": op.operation_id,
                    "type": op.repair_type.value,
                    "target": op.target,
                    "reason": op.reason
                }
                for op in self.repair_history[-5:]
            ]
        }


def create_world_repair(three_layer_system=None) -> WorldRepair:
    """工厂函数：创建世界性修复系统"""
    return WorldRepair(three_layer_system=three_layer_system)