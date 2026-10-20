# 当前任务

更新日期：2026-10-20

## 目标

为 FlowOS 增加后端 GitHub Actions CI，在一次性 PostgreSQL 上验证代码、迁移和测试，不引入尚未确认的采购业务规则。

## 状态

已完成：CI workflow 和相关决策/路线文档已建立，本地等价命令验证通过；首轮 GitHub Actions 结果待提交并推送后确认。

## 计划与实际修改文件

- `.github/workflows/backend-ci.yml`
- `README.md`
- `docs/decisions.md`
- `docs/roadmap.md`
- `docs/development-plan.md`
- `.codex-context/current-task.md`
- 验证完成后更新 `.codex-context/handoff.md`

## 验证

- Workflow YAML 解析通过，`git diff --check` 通过。
- Ruff 通过。
- 本地 PostgreSQL 连接正常，完整测试 26 项通过。
- `alembic check` 通过，无模型漂移。
- GitHub Actions 的首轮远端结果只有推送后才能确认。

## 待解决与下一步

- 采购包装、最小订购量等阶段 3 规则仍待用户确认，本轮不实现。
- 下一步是提交并推送 CI 改动、观察首轮运行结果，然后确认阶段 3 规则或增加密钥扫描。
- 当用户说“准备切换新对话”时，重新采集 Git 和验证事实并更新本文件与 `handoff.md`。
