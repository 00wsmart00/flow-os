# 架构基线

## 背景

FlowOS AI 当前采用单一代码仓库，包含 Python API、规划中的 React 客户端、PostgreSQL、项目文档和本地 Docker Compose。首个目标流程为：订单查询 → 库存缺口分析 → 采购建议草稿。

## 当前实现

- 后端已实现订单查询、基于显式 BOM 版本的物料需求展开，以及基于显式最终库存快照的缺口分析。
- API 统一位于 `/api/v1`，业务错误返回 `error.code`、`error.message` 和可选 `error.details`。
- 物料需求和缺口计算均位于纯 `domain` 层，并返回规则版本与来源引用。
- 前端目录仍是占位结构；采购建议草稿、任务生命周期和审计事件尚未实现。

## 后端分层边界

```text
HTTP 路由 → Pydantic Schema → Service → Repository → SQLAlchemy Model → PostgreSQL
                                  ↓
                          纯领域计算函数
```

- **API 路由**负责 HTTP 协议相关处理，并声明响应模型。
- **Pydantic Schema** 是公开 API 契约，不直接返回 SQLAlchemy 对象。
- **Service** 编排用例，并将持久化结果转换为契约对象。
- **Repository** 负责数据库查询及结果范围限制。
- **SQLAlchemy Model** 只描述持久化结构。
- **Domain** 存放确定性业务计算，不依赖 ORM、HTTP 或其他框架。

这种分层使缺口计算可独立测试，支持未来更换数据来源，也避免数据库结构意外成为公开 API 契约。

## 持久化

运行时使用 SQLAlchemy 的 PostgreSQL 连接池和 Psycopg 3 驱动。Session 作为显式的 Repository 依赖传入，应用关闭时释放数据库引擎。数据库迁移通过 `alembic upgrade head` 执行，当前迁移版本记录在 `alembic_version` 表中。

迁移按版本演进：`0001` 建立客户与销售订单，`0002` 增加产品、订单行、物料和版本化 BOM，`0003` 增加库存快照与物料供应位置。这些模型有意保持最小化和独立命名，不得通过复制现有企业数据库结构来扩展。

## 测试

- HTTP 测试通过 FastAPI 测试客户端验证接口。
- 基础测试将持久化模型绑定到隔离的内存 SQLite，以快速验证契约边界。
- 已有显式开关控制的本地 PostgreSQL Repository 集成测试；仍需接入 CI 的一次性 PostgreSQL 数据库。
- 纯领域规则应使用表格驱动的单元测试，覆盖舍入、单位、零值和负值边界以及解释性数据。

## 安全与 AI 边界

V0.1 不支持任意 SQL、自主采购或 LLM 集成。未来的 AI 功能只能接收由 Service 组装的、经过白名单筛选和最小化的数据上下文；AI 不得直接查询数据库，也不得执行具有业务约束力的操作。确定性领域逻辑始终是数量计算结果的权威来源。

当前基础架构尚未达到生产可用标准。在使用经过授权的真实数据前，必须补齐身份认证、权限控制、租户隔离、审计事件、限流、可观测性、密钥管理和运维控制。

## 跨会话上下文

项目级规则位于根目录 `AGENTS.md`。动态状态位于 `.codex-context/current-task.md` 和 `.codex-context/handoff.md`；它们用于恢复工作，不替代 Git、代码、迁移、测试或本目录中的正式文档。已确认技术决策见 `docs/decisions.md`，简明阶段状态见 `docs/roadmap.md`。
