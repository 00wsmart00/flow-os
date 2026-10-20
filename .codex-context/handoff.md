# FlowOS 会话交接

更新时间：2026-10-20（Asia/Shanghai）

## 仓库状态

- 仓库：`/Users/congwei/flow_os`
- 分支：`main`
- HEAD：`f13d9f1`（`chore: initialize FlowOS AI`）
- 上游：`origin/main`
- 本地相对跟踪分支：ahead 0 / behind 0；本次未 fetch，不能据此断言远端最新状态。
- 工作区：有大量未提交的阶段 1–2 业务改动，以及本次上下文文档改动。不得清理、重置或覆盖。

## 已完成且已验证的业务能力

- 订单列表、筛选、游标分页和详情 API。
- 统一 `error.code/message/details` 错误信封。
- 产品、订单行、物料、版本化 BOM，以及 `material-requirement-v1` 需求展开。
- 最终库存快照、供应位置，以及 `shortage-v1` 缺口分析和来源/警告。
- Alembic 迁移：`0001_initial`、`0002_order_requirements`、`0003_inventory_snapshot`。
- 幂等且拒绝生产环境的合成数据命令。

## 跨会话机制状态

- 已建立根目录 `AGENTS.md`、`docs/decisions.md`、`docs/roadmap.md` 和 `.codex-context/` 双文件交接机制。
- 已增量更新现有架构文档并在 README 增加入口，没有覆盖原有有效内容。
- 本次仅修改 Markdown；入口文件/链接目标存在，`git diff --check` 和常见凭据模式检查通过。
- 本次没有重新运行后端测试或连接数据库，业务验证结果沿用下节明确标注的上一任务结果。

## 最近验证结果

- 在上一开发任务中，本地 PostgreSQL 可连接并已迁移至 `0003_inventory_snapshot`。
- `alembic check` 当时报告无模型漂移。
- 完整测试当时为 26 项通过；Ruff 通过。
- 合成订单 `SYN-SO-0001` 的端到端缺口结果当时为面料 34 米、纽扣 62 个。
- FastAPI/Starlette 测试客户端有一条弃用警告，不影响当前测试结果。
- 本次上下文任务不重新连接数据库；新会话需要数据库时应重新验证，失败立即报告。

## 未提交文件分组

以新会话执行的 `git status --short` 为最终准确信息。当前已知分组：

- 迁移与模型：`backend/alembic/`、`backend/app/models/`。
- API 与用例：`backend/app/api/`、`backend/app/core/errors.py`、`backend/app/services/`、`backend/app/repositories/`、`backend/app/schemas/`。
- 纯领域计算：`backend/app/domain/material_requirements.py`、`backend/app/domain/shortage.py`。
- 合成数据与测试：`backend/app/commands/`、`backend/tests/`。
- 产品与技术文档：`README.md`、`docs/business-rules.md`、`docs/development-plan.md`、`docs/prd-v0.1.md`、`docs/architecture.md`、`docs/decisions.md`、`docs/roadmap.md`。
- 跨会话机制：`AGENTS.md`、`.codex-context/current-task.md`、`.codex-context/handoff.md`。

## 已知待办与风险

- 当前阶段 1–2 改动尚未提交或推送，应先评审 Git diff，再决定提交边界。
- 尚无 CI 和一次性 PostgreSQL 集成环境。
- 快照新鲜度、批次/颜色资格、在途资格、单位换算和采购舍入规则仍待确认。
- 采购建议草稿、任务生命周期、审计事件、前端、身份授权和租户隔离尚未实现。
- 项目未达到生产可用标准，只能使用合成数据。

## 新会话恢复步骤

1. 读取根目录 `AGENTS.md`、本文件和 `current-task.md`。
2. 运行 `git status --short --branch`；按当前任务查看相关 diff，不依赖本文件替代 Git。
3. 读取 `docs/decisions.md`、`docs/roadmap.md`，再按任务加载 PRD、业务规则或详细开发规划。
4. 若继续业务开发，先确认用户是否希望评审/提交现有批次，或直接进入阶段 3。
5. 需要数据库时重新运行连接、迁移和集成验证；连接失败立即报告。

## 切换新对话时

当用户说“准备切换新对话”时，重新采集分支、HEAD、Git 状态和实际验证结果，更新本文件与 `current-task.md`。不得复制旧结论冒充最新状态，不得记录任何凭据或 `.env` 内容。
