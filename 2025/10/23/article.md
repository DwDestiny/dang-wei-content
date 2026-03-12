# Claude Code、Cursor、Codex 配置来回改？做了个工具一键同步！

![](images/image-01.png)
![](images/image-02.png)
![](images/image-03.png)

早上用 Claude Code，中午切 Cursor，晚上换 Codex，每次都得重新配一次 MCP，这件事很多人都经历过。

你早上在 Claude Code 里写的是 JSON，到了 Codex CLI 又得改成 TOML；下午切到 Cursor，还得再去它自己的配置文件里补一遍。晚上切回 Codex，早上改过的内容还不一定同步上，报错更是常态。

所以今天想说的，就是一个专门解决多 AI 编程工具配置同步问题的工具：Vibe Manager。

它是一款 macOS 原生应用，专门给同时使用 Claude Code、Cursor、Codex、Gemini CLI 的 vibecoder 设计。

## 为什么会有这个工具

很多人其实已经有自己的同步方案，比如：

- 手动复制
- 自己写脚本
- 用 Git 管配置

但这些方案都绕不开一个核心问题：不同工具的配置格式不一样。

Vibe Manager 的核心价值，就是把这些麻烦统一收掉：自动格式转换、同步状态检测、时间戳备份，一次修改，多端生效。

## Vibe Manager 能做什么

### 1. 一键同步 MCP

你只需要在 Vibe Manager 里维护一份 MCP 服务器列表，点击同步，它就会自动转换成不同工具需要的格式，然后写到对应位置：

- Claude Code
- Codex CLI
- Gemini CLI
- Cursor

这样你就不用再记每个工具到底吃 JSON 还是 TOML。

### 2. 集中管理编码规则

所有提示词、协作规则、项目模板，只写一次就够了。

- Claude Code 的 `claude.md`
- Codex 的 `agents.md`
- Gemini CLI 的 `gemini.md`

Cursor 目前还不完全一样，但整体上已经能把大部分重复劳动收起来。

### 3. 自动转换 slash 命令

Claude 的 slash 命令、Cursor 和 Gemini 的自定义命令，配置格式本来也不一样。

Vibe Manager 会帮你做转换，不用你自己手抄。

### 4. 实时状态检测

仪表板会直接显示每个工具当前的状态：

- 安装状态：已安装还是未检测到
- 同步状态：已同步还是待同步

这样你在覆盖配置前，就能先看到风险。

### 5. 带时间戳的备份

每次写入配置时，Vibe Manager 都会生成快照，存到 `~/.vibemanager/backups/`。

比如：

- `2025-10-23-19:00_claude_mcp.json`
- `2025-10-23-19:00_cursor_commands.json`

如果哪次改崩了，也能随时回滚。

## 和传统方案相比，有什么差别

### 手动复制粘贴

要改 4 份文件，容易漏，也容易写错。

### 自己写脚本

你要自己处理格式转换、版本管理、冲突检测，维护成本不低。

### Git 同步配置

不同工具的配置文件格式本来就不一致，merge 冲突也很烦。

### Vibe Manager

自动格式转换、可视化管理、一键同步、自动备份，适合长期多工具切换的人。

## 开始使用

Vibe Manager 目前支持 macOS，已经上架，搜索 `vibe` 就能看到。后面也会继续补 Windows 和 Linux 版本。

它是纯客户端工具，所有配置都在本地处理，不上传到云端。

### 使用流程

1. 安装 Vibe Manager
2. 首次启动后自动检测已安装的 AI 编程工具
3. 导入现有配置，或者从零开始
4. 在可视化界面里管理 MCP、规则和命令
5. 点击同步，选择目标工具
6. 完成

后面你每次改配置，都只需要在 Vibe Manager 里改一次。

## 常见问题

### 支持哪些工具

目前支持 Claude Code、Cursor、Codex CLI、Gemini CLI，后续会继续补更多工具，比如 GitHub Copilot、Trae 等。

### 会不会覆盖现有配置

会，但同步前会提示确认，而且每次写入都会自动备份，可以随时回滚。

### 价格

18 元一次性买断，基本就是一杯奶茶钱，能换掉不少重复配置时间。

## 互动话题

你现在在用哪些 AI 编程工具？配置同步最烦的点是什么？

- A. 手动在多个工具之间复制配置，太累
- B. 配置格式不一样，每次都得查文档
- C. 经常忘同步，导致工具行为不一致
- D. 改崩了配置，没备份，只能重配
- E. 其他情况

欢迎留言，我会继续根据大家的反馈优化 Vibe Manager，也会继续分享更多 vibe 开发 Apple 应用的实战经验。

*原文发布于：https://mp.weixin.qq.com/s/nvAydMdyXh2KcOl8EhJlzw*
