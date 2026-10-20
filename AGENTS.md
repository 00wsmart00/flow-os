# FlowOS Codex Guide

本文件适用于整个仓库。所有结论以当前代码、Git 状态和明确需求为准；上下文文档只是交接索引，不得覆盖事实。

## 项目目标与边界

- V0.1 聚焦可审计流程：订单查询 → BOM 物料需求 → 库存缺口 → 无约束力的采购建议草稿。
- 先完成可独立运行的确定性 API 和结构化 UI，再考虑 Core Agent。
- 开发、测试、文档和演示只使用明显标记的合成数据，禁止记录凭据、真实业务数据或专有规则。
- 不支持任意 SQL、自主采购、绕过审批或未经授权的外部写入。

## 架构与编码原则

- 后端采用 FastAPI、Pydantic、SQLAlchemy 2.x、Alembic 和 PostgreSQL；依赖由 `uv` 管理，源配置在 `backend/pyproject.toml`。
- 分层保持为 `API → Service → Repository → SQLAlchemy Model`，确定性计算放在 `app/domain`，不得依赖 ORM 或 HTTP。
- API 使用 `/api/v1`，公开契约由 Pydantic 定义，错误使用 `error.code/message/details` 信封。
- 数量使用 `Decimal`；显式携带单位、规则版本和来源引用，不使用二进制浮点进行业务计算。
- 数据结构变更必须提供 Alembic 迁移并运行漂移检查；不得通过启动时代码直接建表。
- 查询必须有边界，避免 N+1；Repository 负责加载策略，Service 负责用例与契约转换。
- 保持现有命名、类型注解、Ruff 规则和测试风格，不顺手修改任务外代码。

## 按任务加载文档

- 产品范围：[docs/prd-v0.1.md](docs/prd-v0.1.md)
- 架构边界：[docs/architecture.md](docs/architecture.md)
- 已确认决策与待决事项：[docs/decisions.md](docs/decisions.md)
- 当前路线概览：[docs/roadmap.md](docs/roadmap.md)
- 详细实施规划：[docs/development-plan.md](docs/development-plan.md)
- 领域计算：[docs/business-rules.md](docs/business-rules.md)
- 数据安全：[docs/data-compliance.md](docs/data-compliance.md)
- 长期 AI 方向：[docs/ai-manufacturing-os.md](docs/ai-manufacturing-os.md)

只读取与当前任务相关的文档；不要把全部长期规划加载成当前需求。

## 常用验证

在 `backend/` 下使用：

```bash
uv run ruff check .
uv run pytest -m "not integration"
FLOWOS_RUN_POSTGRES_TESTS=1 uv run pytest
uv run alembic check
```

PostgreSQL 是本地依赖。需要数据库的迁移或测试若无法连接，立即报告，不要伪造通过结果。种子数据命令必须保持幂等并拒绝生产环境。

## 会话开始与交接

新会话开始时必须：

1. 读取本文件，以及更深目录中适用的 `AGENTS.md`（若存在）。
2. 读取 `.codex-context/current-task.md` 和 `.codex-context/handoff.md`。
3. 运行 `git status --short --branch`，必要时查看 `git diff`；保留已有未提交改动。
4. 按任务读取上面的相关文档，并用代码和测试校验交接记录是否仍然准确。
5. 从已验证的下一步继续；状态冲突时以 Git、代码和最新用户指令为准，并更新上下文文件。

当用户说“准备切换新对话”时，必须在结束前更新两个上下文文件：

- `current-task.md`：当前目标、范围、进度、实际修改、验证结果、阻塞和下一步。
- `handoff.md`：仓库/分支/HEAD/工作区状态、已完成能力、未提交文件分组、数据库与测试的最后验证状态、风险和恢复步骤。

只写已发生且可验证的事实；未验证项明确标注。不得写入密码、Token、`.env` 内容或其他敏感数据。
