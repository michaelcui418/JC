# 计划管理模块

## 功能概览
- 使用 `plans/*.json` 维护阶段化训练计划（可版本化/可扩展）。
- 每个阶段包含：阶段名称、日期范围、动作清单、训练频次。
- 支持按当前日期或用户选择阶段加载计划。

## 配置结构（JSON）
示例文件：`plans/default_plan.json`。

```json
{
  "version": "1.0",
  "name": "年度训练计划",
  "metadata": {
    "owner": "plan_manager",
    "description": "示例计划，按季度划分训练阶段。"
  },
  "stages": [
    {
      "id": "foundation",
      "name": "基础期",
      "start_date": "2024-01-01",
      "end_date": "2024-03-31",
      "actions": ["建立有氧基础", "核心力量训练", "灵活性提升"],
      "training_frequency_per_week": 3
    }
  ]
}
```

字段说明：
- `version`：计划版本号，便于后续扩展或迁移。
- `name`：计划名称。
- `metadata`：扩展字段（可选）。
- `stages`：阶段列表。
  - `id`：阶段标识符（用于用户选择/程序定位）。
  - `name`：阶段名称。
  - `start_date` / `end_date`：阶段日期范围（ISO 8601）。
  - `actions`：动作清单。
  - `training_frequency_per_week`：每周训练频次。

## 代码使用方式
- 默认加载 `plans/default_plan.json`。
- 按日期加载对应阶段：
  ```python
  manager = PlanManager()
  plan, stage = manager.load_plan_for_date_or_stage(target_date=date(2024, 5, 1))
  ```
- 按用户选择阶段加载：
  ```python
  manager = PlanManager()
  plan, stage = manager.load_plan_for_date_or_stage(stage_id="build")
  ```

## 如何新增/修改阶段
1. 在 `plans/` 新建或复制 JSON 文件，例如 `plans/custom_plan.json`。
2. 修改 `version` 与 `name` 便于管理。
3. 在 `stages` 中新增/修改阶段，确保日期范围不重叠且遵循 ISO 日期格式。
4. 在代码中使用：
   ```python
   manager = PlanManager()
   plan, stage = manager.load_plan_for_date_or_stage(
       plan_file="custom_plan.json",
       target_date=date.today(),
   )
   ```
