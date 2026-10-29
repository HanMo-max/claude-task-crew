# 安装与回滚

先在隔离项目验证，再合并到真实项目。公开模板不包含账户配置，不需要复制任何 `settings.json`、密钥或供应商设置。

## 项目级安装

1. 备份目标项目同名 Skill、角色文件和指令入口；备份留在本地，不提交 Git。
2. 将 `templates/project/.claude/skills/opus-orchestrator/` 合并到目标项目的 `.claude/skills/opus-orchestrator/`。
3. 将五个 `.claude/agents/*.md` 合并到项目同目录。已有同名角色时先比较，保留项目专用约束；不要覆盖整目录。
4. 将模板 `AGENTS.md` 的简短路由入口合并到项目的 canonical `AGENTS.md`。在已有 `CLAUDE.md` 中按需添加 `@AGENTS.md` 引用，不重复复制规则正文。若客户端已直接加载 AGENTS.md，不必再添加重复引用。
5. 检查旧规则是否强制所有任务用 Sonnet、固定 reviewer effort、强制所有多文件任务委派，或设置了 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`。按目标规则消除冲突，保留无关约束。
6. 新建会话，确认 `/opus-orchestrator` 和五个角色可发现，再做运行验证。

本模板不写主会话模型默认值。独立简单任务可直接选择 Haiku，复杂主控按任务需要选择；Skill 不切换正在运行的会话。

## 用户级安装

若希望所有项目都能调用，可以将 Skill 放到 `~/.claude/skills/opus-orchestrator/`，将角色放到 `~/.claude/agents/`。全局指令只保留指向 Skill 的入口，模型分工正文由 Skill 维护。项目同名 Skill/角色或更高优先级配置可能覆盖用户级版本，需核对实际加载来源。

保留已安装角色权限。普通角色文件默认 Sonnet medium，reviewer 默认 Opus low；Skill 会通过每次调用的 `model`、`effort` 设置实际路由。不要为实现分工而把所有角色默认模型一起改成 Haiku，也不要设置全局强制子代理模型。

per-call effort 要求 Claude Code 2.1.292 或更高版本；当前文档中的 Haiku 5.5 要求 2.1.293 或更高版本。CLI 和桌面内置运行时可能不同，分别验证。[官方模型配置](https://code.claude.com/docs/en/model-config)

## 验证

先运行仓库静态检查，再按 [运行验证](runtime-verification.md) 做隔离测试。静态检查不调用模型，不证明安装和实际路由成功。不要在验证中使用客户资料或触发真实业务写入。

## 回滚

恢复本次备份的 Skill、角色和入口；安装时原先不存在的文件只移除本次新增项。新建会话并核对实际加载来源，不覆盖其他项目或账户配置。
