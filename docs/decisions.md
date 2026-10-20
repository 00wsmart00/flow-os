# FlowOS 技术决策

本文件只记录已由需求或代码确认的决策。尚未确认的业务规则列在末尾，不应被实现者自行补全。

## 已确认

### D-001 技术栈与依赖管理

- 后端使用 Python 3.12、FastAPI、Pydantic、SQLAlchemy 2.x、Alembic、Psycopg 3 和 PostgreSQL。
- Python 依赖使用 `uv` 与 `backend/uv.lock` 管理；`backend/pyproject.toml` 配置清华 PyPI 镜像。

### D-002 分层与确定性计算

- HTTP、Service、Repository、持久化模型和领域计算职责分离。
- 数量计算以纯 Python `domain` 函数和 `Decimal` 为权威，不把 ORM 模型作为 API 契约。

### D-003 API 契约

- API 使用 `/api/v1` 前缀、Pydantic 响应模型和统一错误信封。
- 列表查询必须有上限；当前订单列表使用 `before_id` 游标。

### D-004 显式版本与快照

- 订单行显式选择 BOM 版本，不隐式使用“最新 BOM”。
- 物料需求记录规则版本和订单行/BOM 来源。
- 缺口分析必须显式选择状态为 `final` 的库存快照，并返回供应位置、排除量、警告和规则版本。

### D-005 数据与操作边界

- 只使用 `SYN-` 等明显标识的合成数据；种子命令必须幂等且拒绝生产环境。
- V0.1 不执行任意 SQL、生产采购、供应商消息、自主审批或 LLM 直接数据库访问。

### D-006 数据库变更与启动

- Schema 变更通过评审后的 Alembic 迁移完成。
- Docker Compose 的 API 启动命令先执行 `alembic upgrade head`；直接运行应用时仍应显式执行迁移。

### D-007 Agent 引入顺序

- 先验证普通 API、确定性计算、任务状态、审计和结构化 UI；Core Agent 在生产就绪门槛之后引入。

### D-008 后端持续集成

- GitHub Actions 使用一次性 PostgreSQL 16 服务，从空数据库执行全部 Alembic 迁移。
- CI 使用锁文件安装依赖，并依次执行 Ruff、`alembic check`、单元/API 测试和 PostgreSQL 集成测试。
- Workflow 只授予仓库内容读取权限，第三方 action 固定到提交 SHA，且不持久化 Git 凭据。

## 待确认，不得臆定

- 快照新鲜度、批次/颜色资格、在途资格、分配优先级和单位换算策略。
- 采购包装、最小订购量、供应商选择和人工可编辑字段。
- 任务同步/异步阈值、事件传递方式、审计保留策略和并发控制细节。
- 身份、租户、角色权限及真实数据试点范围。

详细领域规则见 [business-rules.md](business-rules.md)，实施顺序见 [roadmap.md](roadmap.md) 和 [development-plan.md](development-plan.md)。
