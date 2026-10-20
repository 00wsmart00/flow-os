# FlowOS 会话交接

更新时间：2026-10-20（Asia/Shanghai）

## 仓库状态

- 仓库：`/Users/congwei/flow_os`
- 分支：`main`
- HEAD：`45babf1`（`feat: add auditable order shortage workflow`）
- 上游：`origin/main`
- 本地跟踪引用显示 `main` 与 `origin/main` 对齐；本次未 fetch，不能据此断言远端最新状态。
- 阶段 1–2 业务与上下文机制已提交。工作区当前只有后端 CI workflow 和对应文档/上下文更新尚未提交。

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
- 上下文机制搭建本身只修改 Markdown；本轮 CI 增量的最新验证结果见下节。

## 当前 CI 增量

- 新增 `.github/workflows/backend-ci.yml`，在 push 到 `main` 和 pull request 时运行。
- CI 使用 PostgreSQL 16 服务、锁定的 uv 版本和只读仓库权限，执行 Ruff、全量迁移、模型漂移检查与完整测试。
- 第三方 action 固定到提交 SHA，checkout 不持久化 Git 凭据。
- 本地等价验证已通过；首轮 GitHub Actions 远端结果尚未产生。

## 最近验证结果

- 本轮本地 PostgreSQL 可连接，当前迁移保持在 `0003_inventory_snapshot`。
- `alembic check` 报告无模型漂移。
- 完整测试 26 项通过；Ruff、YAML 解析和 `git diff --check` 通过。
- 合成订单 `SYN-SO-0001` 的端到端缺口结果当时为面料 34 米、纽扣 62 个。
- FastAPI/Starlette 测试客户端有一条弃用警告，不影响当前测试结果。
- 新会话需要数据库时仍应重新验证，失败立即报告。

## 未提交文件分组

以新会话执行的 `git status --short` 为最终准确信息。当前已知未提交文件：

- `.github/workflows/backend-ci.yml`
- `README.md`
- `docs/decisions.md`
- `docs/development-plan.md`
- `docs/roadmap.md`
- `.codex-context/current-task.md`
- `.codex-context/handoff.md`

## 已知待办与风险

- CI 已配置但尚未提交/推送，首轮 GitHub Actions 结果待确认。
- 尚未增加密钥扫描。
- 快照新鲜度、批次/颜色资格、在途资格、单位换算和采购舍入规则仍待确认。
- 采购建议草稿、任务生命周期、审计事件、前端、身份授权和租户隔离尚未实现。
- 项目未达到生产可用标准，只能使用合成数据。

## 新会话恢复步骤

1. 读取根目录 `AGENTS.md`、本文件和 `current-task.md`。
2. 运行 `git status --short --branch`；按当前任务查看相关 diff，不依赖本文件替代 Git。
3. 读取 `docs/decisions.md`、`docs/roadmap.md`，再按任务加载 PRD、业务规则或详细开发规划。
4. 若继续当前任务，先提交/推送 CI 增量并检查首轮 Actions；若进入阶段 3，先确认采购规则。
5. 需要数据库时重新运行连接、迁移和集成验证；连接失败立即报告。

## 切换新对话时

当用户说“准备切换新对话”时，重新采集分支、HEAD、Git 状态和实际验证结果，更新本文件与 `current-task.md`。不得复制旧结论冒充最新状态，不得记录任何凭据或 `.env` 内容。
