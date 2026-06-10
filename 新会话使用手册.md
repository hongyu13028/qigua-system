#新会话使用手册

> **黄总专属 · 在 Mavis Code 新开会话后, 第一句话说什么 +怎么用整套决策系统**
>适用：家里/公司电脑 clone完两个 Gitee仓库后

---

## 一、3步上手（30 秒）

### 第1步：同步两个仓库到本地（一次性）

打开 PowerShell（公司电脑/家里电脑），执行：

```powershell
#1) 创建目录
mkdir D:\决策系统\
cd D:\决策系统\

#2) clone 两个仓库
git clone https://gitee.com/yaofeng-huang/qigua-system.git
git clone https://gitee.com/yaofeng-huang/traditional-decision-kb.git
```

完成后 `D:\决策系统\` 下有两个文件夹：
- `qigua-system\` ——问卦系统 v2.0（轻量版）
- `traditional-decision-kb\` ——传统决策智慧知识库 v1.0（完整体系）

### 第2步：验证能跑（10 秒）

```powershell
cd D:\决策系统\qigua-system
python qigua.py --time --question "新会话环境验证"
```

应该看到：本卦 + 之卦 +互卦 +错卦 +综卦5 个卦象报告。

### 第3步：打开 Mavis Code 新会话，第一句话

直接说：

> **"起卦"** 或 **"按 qigua prompt 解卦"** 或 **"用传统决策体系"**

我会自动：
1. `Read D:\决策系统\qigua-system\qigua_prompt.md` →加载解卦角色（v2.0）
2.跑 `python qigua.py` →拿到卦象
3. 按 v2.0决策书模板输出双层并行解卦
4.提示你要不要存档

---

## 二、3 种典型用法

###场景1：日常轻量起卦（5 分钟）

> 你说："起卦"

我会自动跑 CLI + 解卦 + 出行动建议。**不污染上下文**——历史决策不会自动塞进新会话。

###场景2：深度决策（30 分钟）

> 你说："用传统决策体系 + 出完整决策书"

我会：
1.跑 CLI 起卦
2.主动 `Read D:\决策系统\traditional-decision-kb\03-决策体系\` 下6 个速查手册
3. 按 v2.0 prompt跑完6 层模型（阴阳遁/月令旺衰/爻位六神/用神/八门九星/三奇）
4. 出8 节完整决策书（卦象摘要→大节奏→主客→抓手→机遇→行动→风险→复盘）
5.提示存档到 `D:\决策系统\traditional-decision-kb\06-案例与日志\问卦决策日志.md`

###场景3：1688运营专项

> 你说："1688运营 +6-21前的节奏"

我会主动查：
- `D:\决策系统\traditional-decision-kb\05-场景应用\01-1688运营\`（6 文件）
- `D:\决策系统\traditional-decision-kb\03-决策体系\04-月令旺衰表.md`（火行业旺衰）
- `D:\决策系统\traditional-decision-kb\03-决策体系\07-阴阳遁与全年节奏.md`（2026攻守节奏）

---

## 三、跟以前会话的边界

✅ **跨会话可用**（基础设施）：
-仓库里的所有文件（CLI、prompt、知识库）—— 直接 Read
- agent memory里的元信息（知道你 +知道系统在哪）—— 自动加载
- 两个 Gitee仓库地址 ——已在 memory

❌ **不自动注入**（按你要求）：
-业务历史（智顺系列、1688定位、过去决策）—— 已归档到 `D:\决策系统\qigua-system\历史解读\`
- "上次你问 XX 是怎么决定的"——不会主动想起

📌 **黄总专属设计**：新会话 =干净状态 +工具随时可用。

---

## 四、常见问题

Q1：我新会话说了"起卦"，Mavis会不会主动读所有仓库内容？
A1：不会。Mavis只会按需 Read：`qigua_prompt.md`（解卦角色）+必要时查 `03-决策体系\`速查表。

Q2：怎么知道系统在哪？
A2：Mavis已经在 agent memory 里知道路径 `D:\决策系统\`。不需要你每次说。

Q3：家里电脑没装 Python怎么办？
A3：跑 `winget install Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements`。

Q4：家里电脑没装 Git怎么办？
A4：跑 `winget install Git.Git -e --source winget --accept-package-agreements --accept-source-agreements`。

Q5：怎么知道现在 Gitee是不是最新？
A5：跑 `git pull`拉取最新。两个仓库都拉一下。

Q6：公司网络封 GitHub 通 Gitee？
A6：是。两个仓库都在 Gitee，没问题。

Q7：跨会话的"业务上下文"不会自动塞进新会话？
A7：对。已归档到 `D:\决策系统\qigua-system\历史解读\`，需要时按索引查。

---

## 五、一句话总结

```
git clone两次 →装 Python →跑一次测试 → 新会话说"起卦" → 直接用
```

**真正用起来，就是这么简单。**

— Mavis整理 ·2026-06-10
