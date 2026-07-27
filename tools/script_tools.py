"""
剧本杀专用工具集 — 角色卡生成、线索卡生成、时间线生成、线索链校验
"""
import time
from pathlib import Path
from langchain_core.tools import tool
from api.monitor import monitor
from api.context import get_session_context
from utils.path_utils import resolve_path


@tool
def build_character_sheet(
        character_name: str,
        age: str,
        public_identity: str,
        real_identity: str,
        personality: str,
        background_story: str,
        public_goal: str,
        secret_goal: str,
        relationships: str,
        initial_clues: str,
        filename: str
) -> str:
    """
    生成单个角色的完整角色剧本（Markdown格式）。

    :param character_name: 角色姓名
    :param age: 年龄
    :param public_identity: 公开身份（职业/社会地位）
    :param real_identity: 真实身份（如果是伪装身份的话）
    :param personality: 性格描述（2-3句话）
    :param background_story: 背景故事（500+字，包含秘密但不暴露真相）
    :param public_goal: 公开目标（其他玩家知道的）
    :param secret_goal: 秘密目标（只有DM和本人知道）
    :param relationships: 与其他角色的关系描述（文字叙述即可）
    :param initial_clues: 角色初始持有的线索
    :param filename: 输出的Markdown文件名（如"角色_管家_张伯.md"）
    :return: 生成结果提示
    """
    _t0 = time.perf_counter()
    monitor.report_tool("角色卡生成器", {"character_name": character_name, "filename": filename})

    markdown_content = f"""# 角色剧本 — {character_name}

---

## 📋 角色封面

| 项目 | 内容 |
|------|------|
| **姓名** | {character_name} |
| **年龄** | {age} |
| **公开身份** | {public_identity} |
| **性格特点** | {personality} |

---

## 📖 背景故事

{background_story}

---

## 🎯 你的目标

### 公开目标
{public_goal}

### 秘密目标
> ⚠️ 以下内容仅你自己和 DM 知晓，请勿在游戏结束前公开。

{secret_goal}

---

## 🔗 人际关系

{relationships}

---

## 🃏 初始线索

{initial_clues}

---

## 🎭 行动建议

### 第一幕：相识与案发
- 了解在场所有人，建立初步关系
- 注意观察每个人的反应和说辞

### 第二幕：搜证与推理
- 根据你的目标选择是分享还是隐藏信息
- 重点调查与你的秘密目标相关的人

### 第三幕：真相揭晓
- 在投票前评估局势
- 根据你掌握的信息做出最终判断

---

> 🤫 **DM备注**：{real_identity}
"""

    session_dir = get_session_context()
    file_path = resolve_path(filename, session_dir)
    path_obj = Path(file_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(markdown_content, encoding='utf-8')
    dt = time.perf_counter() - _t0
    monitor.report_tool(f"角色卡生成器 完成 ({dt:.1f}s)", {"character_name": character_name})
    return f"角色剧本 '{filename}' 已生成。"


@tool
def generate_clue_cards(
        clue_list: str,
        filename: str
) -> str:
    """
    生成线索卡汇总文件（Markdown格式）。
    调用前需要先整理好全部线索信息，以结构化文本形式传入。

    :param clue_list: 结构化线索卡文本，格式为每条线索包含：编号|名称|描述|获取方式|幕|指向真相|难度|是否红鲱鱼
    :param filename: 输出的Markdown文件名（如"线索卡汇总.md"）
    :return: 生成结果提示
    """
    _t0 = time.perf_counter()
    monitor.report_tool("线索卡生成器", {"filename": filename})

    markdown_content = f"""# 线索卡汇总

---

> 📌 共 Y 条线索 | 其中 🔴 红鲱鱼(误导线索) X 条 | 🟢 关键线索 Z 条

---

{clue_list}

---

## 🧩 推理路径说明（仅供 DM 参考）

在第三幕最终推理前，玩家应该能够通过以下推理链锁定真凶：

1. **关键线索A** → 推导出 → **结论A**
2. **关键线索B** + **线索C** → 排除嫌疑人X → **结论B**
3. **关键线索D** → 结合结论A和B → **锁定真凶**

如玩家在推理中卡住，DM 可适当提示上述路径中的中间结论。
"""

    session_dir = get_session_context()
    file_path = resolve_path(filename, session_dir)
    path_obj = Path(file_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(markdown_content, encoding='utf-8')
    dt = time.perf_counter() - _t0
    monitor.report_tool(f"线索卡生成器 完成 ({dt:.1f}s)", {"filename": filename})
    return f"线索卡汇总 '{filename}' 已生成。"


@tool
def build_timeline(
        events_text: str,
        filename: str
) -> str:
    """
    生成案件时间线文件（Markdown格式）。

    :param events_text: 时间线事件描述文本，包含案发前关键时间点、每个角色的行动轨迹
    :param filename: 输出的Markdown文件名（如"案件时间线.md"）
    :return: 生成结果提示
    """
    _t0 = time.perf_counter()
    monitor.report_tool("时间线生成器", {"filename": filename})

    markdown_content = f"""# 案件时间线

---

## ⏰ 案发24小时内关键事件

{events_text}

---

## ⚠️ 时间线矛盾点（DM 注意）

以下节点可能存在角色证词与实际行动的矛盾，DM 在主持时需特别留意：

（由逻辑校验助手审查后填充）

---

## 📍 锚点时间

- **案发推定时间**：（填充）
- **尸体发现时间**：（填充）
- **报警/通知DM时间**：（填充）
"""

    session_dir = get_session_context()
    file_path = resolve_path(filename, session_dir)
    path_obj = Path(file_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(markdown_content, encoding='utf-8')
    dt = time.perf_counter() - _t0
    monitor.report_tool(f"时间线生成器 完成 ({dt:.1f}s)", {"filename": filename})
    return f"案件时间线 '{filename}' 已生成。"


@tool
def generate_dm_manual(
        script_info: str,
        story_background: str,
        case_truth: str,
        act_guide: str,
        ending: str,
        filename: str
) -> str:
    """
    生成组织者手册（DM手册），Markdown格式。

    :param script_info: 剧本基本信息（人数/类型/时长/难度）
    :param story_background: 完整故事背景（1000+字）
    :param case_truth: 案件真相（完整叙述+推理路径）
    :param act_guide: 分幕流程指南
    :param ending: 结局说明（正常结局+隐藏结局/反转）
    :param filename: 输出的Markdown文件名（如"DM_手册.md"）
    :return: 生成结果提示
    """
    _t0 = time.perf_counter()
    monitor.report_tool("DM手册生成器", {"filename": filename})

    markdown_content = f"""# 🎭 组织者手册（DM 专用）

---

> ⚠️ **本手册仅供 DM 阅读，请勿在游戏结束前向玩家公开。**

---

## 📋 剧本基本信息

{script_info}

---

## 📖 完整故事背景

{story_background}

---

## 🔍 案件真相

{case_truth}

---

## 🎬 分幕流程指南

{act_guide}

---

## 🎯 结局说明

{ending}

---

> 🤫 祝主持顺利。记住：你的职责是让每个人都感觉自己是主角。
"""

    session_dir = get_session_context()
    file_path = resolve_path(filename, session_dir)
    path_obj = Path(file_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(markdown_content, encoding='utf-8')
    dt = time.perf_counter() - _t0
    monitor.report_tool(f"DM手册生成器 完成 ({dt:.1f}s)", {"filename": filename})
    return f"组织者手册 '{filename}' 已生成。"
