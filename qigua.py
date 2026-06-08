#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问卦系统 — 实战工具
=========================================
三件功能：
  1) 数字起卦 (qigua_number)         - 给两个数字 → 本卦 + 变爻
  2) 时间起卦 (qigua_time)           - 给一个时间戳 → 本卦 + 变爻
  3) 铜钱/奇偶起卦 (qigua_coins)     - 给 6 个 0/1 → 本卦 + 变爻

并自动从 gua_64.json 加载卦象数据，输出 6 要素解卦骨架。
用户拿到结果后，可以直接交给任何 LLM（贴上 qigua_prompt.md）做深度解读。

用法：
  $ python qigua.py
  > 选择起卦方式: 1/2/3
  > 输入...
  > 输出完整卦象 + 解卦骨架
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 八卦二进制编码 (从下到上: 初/二/三爻)
TRIGRAMS = {
    "111": "乾 ☰",
    "110": "兑 ☱",
    "101": "离 ☲",
    "100": "震 ☳",
    "011": "巽 ☴",
    "010": "坎 ☵",
    "001": "艮 ☶",
    "000": "坤 ☷",
}
# 八卦序号 (0-7) → 八卦名
TRIGRAM_BY_IDX = {
    0: "坤 ☷",
    1: "乾 ☰",
    2: "兑 ☱",
    3: "离 ☲",
    4: "震 ☳",
    5: "巽 ☴",
    6: "坎 ☵",
    7: "艮 ☶",
}
# 时辰地支对应数字
SHICHEN = {
    "子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6,
    "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12,
}

# 数据加载
DATA_FILE = Path(__file__).parent / "gua_64.json"
GUA_DB = {}
GUA_BY_BINARY = {}

def load_db():
    global GUA_DB, GUA_BY_BINARY
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for g in data["gua"]:
        GUA_DB[g["id"]] = g
        GUA_BY_BINARY[g["binary"]] = g
    return data

def get_gua_by_binary(binary_str):
    return GUA_BY_BINARY.get(binary_str)

# === 起卦算法 ===

def qigua_number(a: int, b: int):
    """数字起卦: 给两个正整数 a, b"""
    upper_idx = a % 8
    lower_idx = b % 8
    change_idx = (a + b) % 6
    upper = TRIGRAM_BY_IDX[upper_idx]
    lower = TRIGRAM_BY_IDX[lower_idx]
    binary = _join_binary(lower, upper)
    return {
        "method": "数字起卦",
        "params": f"a={a}, b={b}",
        "upper_idx": upper_idx, "lower_idx": lower_idx, "change_idx": change_idx,
        "upper": upper, "lower": lower,
        "binary": binary,
        "change_yao": change_idx,  # 1-6, 1=初爻
    }

def qigua_time(dt: datetime = None, shichen: str = None):
    """时间起卦: 给一个 datetime 对象和时辰地支"""
    if dt is None:
        dt = datetime.now()
    if shichen is None:
        shichen = _auto_shichen(dt.hour)
    s = SHICHEN[shichen]
    upper_idx = (dt.year + dt.month + dt.day) % 8
    lower_idx = (dt.year + dt.month + dt.day + s) % 8
    change_idx = (dt.year + dt.month + dt.day + s) % 6
    upper = TRIGRAM_BY_IDX[upper_idx]
    lower = TRIGRAM_BY_IDX[lower_idx]
    binary = _join_binary(lower, upper)
    return {
        "method": "时间起卦",
        "params": f"{dt.strftime('%Y-%m-%d %H:%M')} 时辰={shichen}({s})",
        "upper_idx": upper_idx, "lower_idx": lower_idx, "change_idx": change_idx,
        "upper": upper, "lower": lower,
        "binary": binary,
        "change_yao": change_idx if change_idx > 0 else 6,
    }

def qigua_coins(yao_list):
    """铜钱起卦: 给 6 个 0/1, 从下到上 (初爻到上爻)"""
    if len(yao_list) != 6:
        raise ValueError("需要 6 个爻位 (从下到上)")
    binary = "".join(str(x) for x in yao_list)
    # 自动判定变爻: 第一个 0->1 或 1->0 的位置
    # 这里采用最简版: 用户手动指定变爻位置
    return {
        "method": "铜钱起卦",
        "params": f"爻(下→上): {yao_list}",
        "binary": binary,
        # 变爻位置会在用户输入时指定
    }

# === 工具函数 ===

def _auto_shichen(hour):
    """根据小时自动返回时辰地支"""
    h = hour
    mapping = [
        ("子", (23, 24)), ("子", (0, 1)),
        ("丑", (1, 3)), ("寅", (3, 5)),
        ("卯", (5, 7)), ("辰", (7, 9)),
        ("巳", (9, 11)), ("午", (11, 13)),
        ("未", (13, 15)), ("申", (15, 17)),
        ("酉", (17, 19)), ("戌", (19, 21)),
        ("亥", (21, 23)),
    ]
    for name, (lo, hi) in mapping:
        if lo <= h < hi:
            return name
    return "子"

def _join_binary(lower, upper):
    """把上下卦字符串 (含符号) 拼成 6 位二进制"""
    # 提取 '艮 ☶' 里的 '001'
    lower_bin = _trigram_to_bin(lower)
    upper_bin = _trigram_to_bin(upper)
    return lower_bin + upper_bin  # 下卦在前 (低位)

def _trigram_to_bin(trigram_str):
    """'乾 ☰' → '111'"""
    for k, v in TRIGRAMS.items():
        if v == trigram_str:
            return k
    return "000"

def _binary_change(binary_str, pos):
    """把 binary_str 的第 pos 位 (1-6, 从下到上) 取反"""
    lst = list(binary_str)
    # pos=1 → 第 0 位 (最下)
    idx = pos - 1
    lst[idx] = "1" if lst[idx] == "0" else "0"
    return "".join(lst)

def _binary_rotate(binary_str, reverse=False):
    """上下翻转 (综卦) - reverse=False: 上下互换"""
    if reverse:
        # 错卦: 全部取反
        return "".join("1" if x == "0" else "0" for x in binary_str)
    else:
        # 综卦: 前 3 位和后 3 位互换并倒序
        return binary_str[3:][::-1] + binary_str[:3][::-1]

def _binary_hu(binary_str):
    """互卦: 取 2-3-4 为下卦, 3-4-5 为上卦"""
    # binary_str: [初(0), 二(1), 三(2), 四(3), 五(4), 上(5)]
    # 互卦下卦 = [二(1), 三(2), 四(3)]
    # 互卦上卦 = [三(2), 四(3), 五(4)]
    lower = binary_str[1] + binary_str[2] + binary_str[3]
    upper = binary_str[2] + binary_str[3] + binary_str[4]
    return lower + upper

# === 完整解卦输出 ===

def full_divination(result, yao_change_pos=None, question=""):
    """完整解卦输出"""
    if "binary" not in result:
        raise ValueError("先起卦")
    binary = result["binary"]
    main_gua = get_gua_by_binary(binary)
    if not main_gua:
        return {"error": f"未找到卦象: {binary}"}

    # 之卦 (变卦)
    if yao_change_pos is None:
        yao_change_pos = result.get("change_idx")
    if yao_change_pos and 1 <= yao_change_pos <= 6:
        zhi_binary = _binary_change(binary, yao_change_pos)
        zhi_gua = get_gua_by_binary(zhi_binary)
    else:
        zhi_gua = None
        zhi_binary = binary

    # 互卦
    hu_binary = _binary_hu(binary)
    hu_gua = get_gua_by_binary(hu_binary)

    # 错卦
    cuo_binary = _binary_rotate(binary, reverse=True)
    cuo_gua = get_gua_by_binary(cuo_binary)

    # 综卦
    zong_binary = _binary_rotate(binary, reverse=False)
    zong_gua = get_gua_by_binary(zong_binary)

    # 上下关系
    lower_name = main_gua["lower"].split(" ")[0]
    upper_name = main_gua["upper"].split(" ")[0]
    rel = _gua_relationship(lower_name, upper_name)

    output = {
        "question": question,
        "method": result["method"],
        "params": result.get("params", ""),
        "main": {
            "id": main_gua["id"],
            "name": main_gua["name"],
            "symbol": main_gua["symbol"],
            "binary": binary,
            "module": main_gua["module"],
            "core": main_gua["core"],
            "judgment": main_gua["judgment"],
            "modern": main_gua["modern"],
        },
        "upper": main_gua["upper"],
        "lower": main_gua["lower"],
        "relationship": rel,
        "zhi": None,
        "hu": None,
        "cuo": None,
        "zong": None,
    }
    if zhi_gua:
        output["zhi"] = {
            "name": zhi_gua["name"],
            "symbol": zhi_gua["symbol"],
            "core": zhi_gua["core"],
            "change_yao": yao_change_pos,
        }
    if hu_gua:
        output["hu"] = {
            "name": hu_gua["name"],
            "symbol": hu_gua["symbol"],
            "core": hu_gua["core"],
        }
    if cuo_gua:
        output["cuo"] = {
            "name": cuo_gua["name"],
            "symbol": cuo_gua["symbol"],
            "core": cuo_gua["core"],
        }
    if zong_gua:
        output["zong"] = {
            "name": zong_gua["name"],
            "symbol": zong_gua["symbol"],
            "core": zong_gua["core"],
        }
    return output

def _gua_relationship(lower, upper):
    """上下卦关系: 五行生克"""
    wuxing = {
        "乾": "金", "兑": "金",
        "离": "火",
        "震": "木", "巽": "木",
        "坎": "水",
        "艮": "土", "坤": "土",
    }
    sheng = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
    ke = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    if lower not in wuxing or upper not in wuxing:
        return "未知关系"
    l_wx = wuxing[lower]
    u_wx = wuxing[upper]
    if sheng[l_wx] == u_wx:
        return f"下生上 ({lower}→{upper}): 内力滋养外势, 利于做事, 但要量力"
    elif sheng[u_wx] == l_wx:
        return f"上生下 ({upper}→{lower}): 外部托底, 内部可大胆推进"
    elif ke[l_wx] == u_wx:
        return f"下克上 ({lower}→{upper}): 内部能驾驭外部, 主动出击"
    elif ke[u_wx] == l_wx:
        return f"上克下 ({upper}→{lower}): 外部压力大, 内部承受风险"
    elif l_wx == u_wx:
        return f"比和 ({lower}={upper}): 内外协合, 顺势而为"
    return f"无直接关系 ({lower}/{upper})"

def print_divination(d):
    """打印漂亮的卦象报告"""
    if "error" in d:
        print(d["error"])
        return
    m = d["main"]
    print()
    print("══════════════════════════════════════════════")
    print(f"  【问卦】{d['question'] or '(无题)'}")
    print("══════════════════════════════════════════════")
    print(f"  起卦方式: {d['method']}  |  参数: {d['params']}")
    print("──────────────────────────────────────────────")
    print(f"  本卦: {m['name']} {m['symbol']}  ({m['id']}/64)  模块{m['module']}")
    print(f"  上下: 下卦 {d['lower']}  |  上卦 {d['upper']}")
    print(f"  关系: {d['relationship']}")
    print(f"  卦德: {m['core']}")
    print(f"  判断: {m['judgment']}")
    print(f"  现代: {m['modern']}")
    print("──────────────────────────────────────────────")
    if d.get("zhi"):
        z = d["zhi"]
        print(f"  之卦(变): {z['name']} {z['symbol']} (变爻在第 {z['change_yao']} 爻)")
        print(f"           {z['core']}")
    if d.get("hu"):
        h = d["hu"]
        print(f"  互卦:   {h['name']} {h['symbol']}  (事情的中间状态)")
        print(f"           {h['core']}")
    if d.get("cuo"):
        c = d["cuo"]
        print(f"  错卦:   {c['name']} {c['symbol']}  (反向选择会怎样)")
        print(f"           {c['core']}")
    if d.get("zong"):
        zg = d["zong"]
        print(f"  综卦:   {zg['name']} {zg['symbol']}  (站在对方视角)")
        print(f"           {zg['core']}")
    print("══════════════════════════════════════════════")
    print()
    print("  📖 下一步: 把以上内容贴给 LLM, 配上 qigua_prompt.md,")
    print("           即可获得完整「解卦 + 行动建议」解读。")
    print()


# === 交互式 CLI ===

def interactive():
    print()
    print("╔════════════════════════════════════════╗")
    print("║       问卦系统 v0.1 — 实战工具          ║")
    print("║   基于《易经》64卦 + 六大模块决策框架    ║")
    print("╚════════════════════════════════════════╝")
    print()
    print("  请先在心里想清楚你要问的问题（一事一卦）。")
    print()
    print("  选择起卦方式:")
    print("    1) 数字起卦 — 给我两个数字 a, b")
    print("    2) 时间起卦 — 用当前时间")
    print("    3) 铜钱起卦 — 你想 6 个 0/1, 从下到上")
    print()
    choice = input("  你的选择 (1/2/3): ").strip()

    question = input("  你想问什么？ (一句话): ").strip()

    if choice == "1":
        a = int(input("  数字 a: "))
        b = int(input("  数字 b: "))
        result = qigua_number(a, b)
    elif choice == "2":
        print("  [使用当前时间]")
        result = qigua_time()
    elif choice == "3":
        print("  依次输入 6 个爻 (1=阳/0=阴), 从下到上 (初爻→上爻):")
        yao_list = []
        positions = ["初", "二", "三", "四", "五", "上"]
        for pos in positions:
            y = int(input(f"    {pos}爻 (1=阳, 0=阴): "))
            yao_list.append(y)
        result = qigua_coins(yao_list)
        result["upper"] = get_gua_by_binary(result["binary"])["upper"]
        result["lower"] = get_gua_by_binary(result["binary"])["lower"]
        # 铜钱起卦默认以最后一爻为变爻 (或用户指定)
        change = int(input("  变爻位置 (1-6, 0=无变爻): "))
        result["change_idx"] = change if change > 0 else None
    else:
        print("  无效选择")
        return

    output = full_divination(result, result.get("change_idx"), question)
    print_divination(output)


def parse_args():
    """解析命令行参数"""
    args = {"method": None, "params": [], "question": "", "change": None}
    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--demo":
            args["method"] = "demo"
        elif a == "--number" and i + 2 < len(sys.argv):
            args["method"] = "number"
            args["params"] = [int(sys.argv[i+1]), int(sys.argv[i+2])]
            i += 2
        elif a == "--time":
            args["method"] = "time"
        elif a == "--coins" and i + 6 < len(sys.argv):
            args["method"] = "coins"
            args["params"] = [int(x) for x in sys.argv[i+1:i+7]]
            i += 6
        elif a == "--question" and i + 1 < len(sys.argv):
            args["question"] = sys.argv[i+1]
            i += 1
        elif a == "--change" and i + 1 < len(sys.argv):
            args["change"] = int(sys.argv[i+1])
            if not (0 <= args["change"] <= 6):
                print("[警告] --change 必须是 0-6 (0=无动爻)")
                args["change"] = None
            i += 1
        elif a == "--help" or a == "-h":
            print(__doc__)
            sys.exit(0)
        i += 1
    return args


if __name__ == "__main__":
    load_db()
    args = parse_args()

    if args["method"] == "demo":
        print("\n[演示模式] 用当前时间起卦, 问题: '我下一步 1688 运营最该做什么?'")
        result = qigua_time()
        output = full_divination(result, result.get("change_idx"), "我下一步 1688 运营最该做什么?")
        print_divination(output)

    elif args["method"] == "number":
        a, b = args["params"]
        question = args["question"] or f"数字起卦 a={a}, b={b}"
        print(f"\n[数字起卦] a={a}, b={b}  问题: {question}")
        result = qigua_number(a, b)
        output = full_divination(result, result.get("change_idx"), question)
        print_divination(output)

    elif args["method"] == "time":
        question = args["question"] or "用当前时间起卦"
        print(f"\n[时间起卦]  问题: {question}")
        result = qigua_time()
        output = full_divination(result, result.get("change_idx"), question)
        print_divination(output)

    elif args["method"] == "coins":
        yao_list = args["params"]
        question = args["question"] or f"铜钱起卦 爻={yao_list}"
        print(f"\n[铜钱起卦] 爻(下→上): {yao_list}  问题: {question}")
        result = qigua_coins(yao_list)
        g = get_gua_by_binary(result["binary"])
        if g:
            result["upper"] = g["upper"]
            result["lower"] = g["lower"]
        # 变爻位置: 由 --change 参数显式指定; 不指定则无动爻
        result["change_idx"] = args.get("change")
        output = full_divination(result, result.get("change_idx"), question)
        print_divination(output)

    else:
        interactive()
