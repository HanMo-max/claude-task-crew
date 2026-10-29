# Claude Task Crew

让 Claude Code 按任务分工：**Haiku 做边界明确的小任务，Sonnet 做日常开发，Opus 负责复杂判断与关键审查，Fable 用于确有必要的难题。**

这是面向 Claude Code CLI 和桌面端 Code 模式的 Skill 与五个角色模板，复用客户端已有的子代理功能，不需要额外调度服务。命名和目录结构参考同作者的 [ChatGPT Task Crew](https://github.com/HanMo-max/chatgpt-task-crew)。本项目由个人维护，与 Anthropic 无官方隶属关系。

## 怎么分工

| 任务 | 模型 | 推理强度 |
| --- | --- | --- |
| 短文本提取、定点查找、明确的分类整理 | Haiku 5.5 | low |
| 指定测试命令、按已定方案做机械性小改 | Haiku 5.5 | medium |
| 日常功能、局部排错、测试设计、一般审查 | Sonnet 5.5 | medium，必要时 high |
| 架构、跨组件根因、权限/计费/数据一致性、关键审查 | Opus 5.5 | medium / high |
| Opus 仍有实质推理阻塞，或用户指定的高难任务 | Fable 5.1 | high |

Haiku 任务必须目标清楚、范围有限、结果容易验证；不把所有任务都交给 Haiku 先试错。文件少不等于简单：一行权限判断也需要按实际风险分级。

简单独立任务可以在新会话直接选择 Haiku，普通开发可以用 Sonnet；复杂任务的主控模型由用户选择。Skill 不自动切换正在运行的主会话，也不改默认模型。

已有主控能用少量命令完成的小操作直接做；只有独立工作流、上下文隔离或独立验证有实际收益时才委派。关键任务保留独立 Builder + Challenger，一般小改不机械启动一整套代理。

## 如何实现

保留 `opus-orchestrator` 名称，对应 ChatGPT Task Crew 的 `astra-orchestrator`。复用五个角色：`explorer`、`worker`、`tester`、`researcher`、`reviewer`。

角色文件保留保守默认值：普通角色 Sonnet medium，reviewer Opus low。**加载 Skill 后，由主控在每次 `Agent` 调用中显式设置模型和 effort**：简单任务可覆盖为 Haiku，一般审查为 Sonnet medium，关键审查为 Opus medium/high。角色默认值不是最终路由；绕过 Skill 直接使用角色不会自动实现这里的动态分工。

Haiku 遇到需求歧义、跨模块推理或来源冲突时交回主控；原因明确的小错误允许一次针对性修正，再失败就转 Sonnet。必要时再转 Opus。Fable 不作为常规 worker，新增调用遵守当前任务授权；已有 Fable 主控直接接管难点。

## 仓库内容

```text
templates/project/
  AGENTS.md
  CLAUDE.md                              兼容入口，引用 AGENTS.md
  .claude/skills/opus-orchestrator/SKILL.md
  .claude/agents/{explorer,worker,tester,researcher,reviewer}.md
docs/
  installation.md                        合并安装与回滚
  runtime-verification.md                实际路由验证与证据边界
examples/delegation.md                   可直接改写的任务契约
scripts/check_bundle.py                  无第三方依赖的静态检查
```

模板放在 `templates/project/` 下；打开本仓库不会自动安装模板。

## 开始使用

1. 确认客户端支持 Skill、自定义子代理和所需模型。本文针对 2026-10-29 核对的模型；per-call effort 需要 Claude Code 2.1.292 或更高版本，模型能力和可用性仍受客户端及供应端影响。
2. 按 [安装说明](docs/installation.md) 备份并合并文件，不覆盖现有项目约束。
3. 新建会话，使用 `/opus-orchestrator`，例如：

```text
使用 opus-orchestrator。先判断任务难度和是否值得委派。
明确、可核对的小任务交给 Haiku；普通开发用 Sonnet；
复杂决策和关键审查用 Opus，Fable 仅在确有必要时使用。
每次实际调用明确模型、effort、范围、文件归属和验收标准。
请根据真实 diff、运行结果和来源证据验收，不只采信完成声明。
```

4. 按 [运行验证说明](docs/runtime-verification.md) 核对实际模型，不能只看角色文件或模型菜单。

静态检查：

```sh
python3 scripts/check_bundle.py
```

本模板不包含 API Key、账户设置或模型权限，不会安装到普通 Claude 网页聊天中。CLI 验证不能替代每个桌面版本的子代理路由验证；参见验证说明中的已验证范围。

## 依据

- [Haiku 5.5 官方介绍](https://www.anthropic.com/claude-haiku-5-5)：高频提取、摘要及辅助编码定位。
- [Haiku 提示指南](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5)：短任务可用 low，代理编码从 medium 起步，并要求实际检查。
- [Claude Code 子代理](https://code.claude.com/docs/en/sub-agents)：模型覆盖、effort 和运行时检查。
- [Claude Code Skills](https://code.claude.com/docs/en/skills) 与 [项目指令](https://code.claude.com/docs/en/memory)。

按实际 usage、返工和验收耗时判断总成本；目前不承诺节省比例或真实项目质量通过率。第三方网关实际账单与 Anthropic 公布价格可能不同。
