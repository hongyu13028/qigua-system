# 问卦系统 (qigua-system)

> 用《易经》64 卦 + 六大模块做决策辅助, 让 AI 帮你"问卦、解卦、行卦"。

## 这是什么

一个轻量级、易上手的"问卦系统":

- **64 卦结构化数据库** (`gua_64.json`) — 每个卦带模块归属、主题、场景、判断、现代解读
- **AI 问卦先生提示词** (`qigua_prompt.md`) — 贴进任何 LLM 就能用
- **起卦 CLI 工具** (`qigua.py`) — 数字/时间/铜钱三种起卦方式, 纯 Python 标准库, 无依赖
- **卦象档案** (`gua_log.md`) — 问卦记录, 形成个人卦象库, 30/60/90 天复盘
- **使用说明** (`使用说明.md`) — 怎么用这套系统
- **文章学习笔记** (`文章学习笔记.md`) — 系统设计源头: 头条《我把《易经》64卦编成了人生通关攻略》

## 快速上手

```bash
# 1) 数字起卦
python qigua.py --number 88 18 --question "我下一步该怎么走?"

# 2) 时间起卦
python qigua.py --time --question "我今晚去见客户能不能成?"

# 3) 铜钱起卦
python qigua.py --coins 1 1 0 0 1 0 --change 4 --question "我该不该招这个合伙人?"
```

## 跨设备同步

- 本仓库已推送 Gitee: `https://gitee.com/yaofeng-huang/qigua-system` (私有)
- 公司电脑 + 家里电脑 + 手机 (Gitee App) 三端共享
- 更新流程: 改完代码 → `git add .` → `git commit -m "..."` → `git push`
- 拉取: `git pull`

## 系统要求

- Python 3.10+ (无第三方依赖)
- Git
- 任意 LLM (ChatGPT / Claude / 通义 / MiniMax Code)
- 代码托管: Gitee (公司网络可访问) / GitHub (家里网络可访问)

## 项目结构

```
qigua-system/
├── .gitignore
├── README.md
├── gua_64.json          # 64 卦数据库
├── gua_log.md           # 卦象档案
├── qigua.py             # 起卦 + 解卦 CLI
├── qigua_prompt.md      # AI 问卦先生系统提示词
├── 使用说明.md
└── 文章学习笔记.md
```

## 设计哲学

> 卦不是答案, 是镜子。
> 起卦不是问神, 是问自己。
> 解卦不是听命, 是见路。
> 行动不是依卦, 是顺势。

— 用《易经》的方式过现代日子。

---

**版本**: v0.3
**最新更新**: 2026-06-08
**作者**: 黄耀锋 (科盈信息技术) + Mavis (Mavis)
