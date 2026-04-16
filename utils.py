from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List
from urllib.parse import urlparse

FORM_KEYS = [
    "domain",
    "specialization",
    "specificGoal",
    "action",
    "details",
    "constraints",
    "format",
    "structure",
    "unwantedResult",
]

ACTION_TYPE_MAP_ZH = {
    "Search": "搜尋",
    "Lookup": "查找",
    "Browse": "瀏覽",
}

PROMPT_PRESETS = {
    "en": {
        "Startup GTM Plan": {
            "domain": "growth marketing",
            "specialization": "B2B SaaS go-to-market and demand generation",
            "specificGoal": "build a 90-day GTM plan to grow qualified pipeline for a seed-stage SaaS product",
            "action": [
                {"type": "Search", "value": "latest B2B SaaS demand generation benchmarks in 2025"},
                {"type": "Lookup", "value": "framework for ICP segmentation and messaging matrix"},
                {"type": "Browse", "value": "https://www.saastr.com"},
            ],
            "details": "Target market: US SMB teams. Current monthly traffic: 35k. Budget: $40k/month.",
            "constraints": "Keep CAC payback under 12 months and avoid channel plans with heavy paid ads dependence.",
            "format": "markdown",
            "structure": "{executive_summary, assumptions, 90_day_plan, channel_experiments, KPI_dashboard, risks}",
            "unwantedResult": "generic tactics with no timeline or metric targets",
        },
        "Research Synthesis": {
            "domain": "machine learning",
            "specialization": "LLM applications and evaluation",
            "specificGoal": "summarize key advances in retrieval-augmented generation and propose a practical implementation plan",
            "action": [
                {"type": "Search", "value": "recent RAG system design papers and production case studies"},
                {"type": "Lookup", "value": "tradeoffs among vector search strategies and reranking"},
            ],
            "details": "Audience: engineering managers and applied scientists. System currently handles 20k docs.",
            "constraints": "Use plain language for non-research readers and include implementation risks.",
            "format": "markdown",
            "structure": "{overview, key_findings, implementation_options, recommendation, rollout_plan}",
            "unwantedResult": "paper list without actionable recommendations",
        },
        "Product Strategy Brief": {
            "domain": "product management",
            "specialization": "consumer subscription products",
            "specificGoal": "design a retention improvement strategy for a mobile subscription app",
            "action": [
                {"type": "Search", "value": "subscription retention playbooks and lifecycle messaging best practices"},
                {"type": "Lookup", "value": "cohort analysis interpretation for churn diagnosis"},
            ],
            "details": "Current D30 retention is 18%. App category: wellness. Primary market: Taiwan and US.",
            "constraints": "Prioritize low-engineering-cost experiments for next 8 weeks.",
            "format": "markdown",
            "structure": "{problem_statement, insights, experiment_backlog, measurement_plan, next_steps}",
            "unwantedResult": "recommendations with no owner or measurable KPI",
        },
    },
    "zh": {
        "新創成長策略": {
            "domain": "成長行銷",
            "specialization": "B2B SaaS 市場進入策略與需求開發",
            "specificGoal": "制定 90 天 GTM 計畫，提升新創 SaaS 的高品質商機數量",
            "action": [
                {"type": "Search", "value": "2025 年 B2B SaaS 需求開發 benchmark"},
                {"type": "Lookup", "value": "ICP 分群與訊息矩陣的實務框架"},
                {"type": "Browse", "value": "https://www.saastr.com"},
            ],
            "details": "目標市場：美國 SMB。每月流量：35k。預算：每月 4 萬美元。",
            "constraints": "CAC 回收期需低於 12 個月，避免高度依賴付費廣告。",
            "format": "markdown",
            "structure": "{執行摘要, 假設, 90天計畫, 渠道實驗, KPI儀表板, 風險}",
            "unwantedResult": "只有概念建議、沒有時程與指標",
        },
        "研究整理簡報": {
            "domain": "機器學習",
            "specialization": "LLM 應用與評估",
            "specificGoal": "整理 RAG 最新進展，並提出可落地的導入方案",
            "action": [
                {"type": "Search", "value": "近期 RAG 系統設計論文與案例"},
                {"type": "Lookup", "value": "向量檢索與 reranker 的取捨"},
            ],
            "details": "受眾為工程經理與應用科學家，現有知識庫約 2 萬份文件。",
            "constraints": "用非研究人員也能理解的語言，並說明風險與限制。",
            "format": "markdown",
            "structure": "{背景, 關鍵洞察, 方案比較, 建議, 上線路線圖}",
            "unwantedResult": "只列論文，不提供執行建議",
        },
        "產品策略提案": {
            "domain": "產品管理",
            "specialization": "訂閱制 App 成長",
            "specificGoal": "為行動訂閱產品規劃留存提升策略",
            "action": [
                {"type": "Search", "value": "subscription retention lifecycle best practices"},
                {"type": "Lookup", "value": "如何解讀 cohort 分析找出 churn 主因"},
            ],
            "details": "目前 D30 留存 18%，品類為 wellness，主要市場為台灣與美國。",
            "constraints": "優先考慮 8 週內可執行且工程成本低的實驗。",
            "format": "markdown",
            "structure": "{問題定義, 洞察, 實驗清單, 量測方案, 下一步}",
            "unwantedResult": "沒有 KPI 或負責人的建議",
        },
    },
}


def get_default_form_data() -> Dict[str, Any]:
    """Return a fresh default form state."""
    return {
        "domain": "",
        "specialization": "",
        "specificGoal": "",
        "action": [{"type": "Search", "value": ""}],
        "details": "",
        "constraints": "",
        "format": "",
        "structure": "",
        "unwantedResult": "",
    }


def get_prompt_presets(lang: str = "en") -> Dict[str, Dict[str, Any]]:
    """Return preset examples keyed by display name."""
    return deepcopy(PROMPT_PRESETS.get(lang, PROMPT_PRESETS["en"]))


def normalize_form_data(form_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """Normalize incoming form data into the expected schema."""
    normalized = get_default_form_data()
    if not form_data:
        return normalized

    for key in FORM_KEYS:
        if key == "action":
            normalized["action"] = normalize_actions(form_data.get("action"))
            continue

        value = form_data.get(key, "")
        normalized[key] = _clean_text(value)
    return normalized


def normalize_actions(raw_actions: Any) -> List[Dict[str, str]]:
    """Normalize action values to a stable list of action dictionaries."""
    normalized: List[Dict[str, str]] = []

    if isinstance(raw_actions, list):
        for item in raw_actions:
            if isinstance(item, dict):
                action_type = _clean_text(item.get("type")) or "Search"
                value = _clean_text(item.get("value"))
                normalized.append({"type": action_type, "value": value})
            elif isinstance(item, str):
                value = _clean_text(item)
                normalized.append({"type": "Search", "value": value})
    elif isinstance(raw_actions, str):
        lines = [line.strip() for line in raw_actions.splitlines() if line.strip()]
        normalized = [{"type": "Search", "value": line} for line in lines]

    if not normalized:
        normalized = [{"type": "Search", "value": ""}]

    return normalized


def get_prompt_health_report(form_data: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    """Return a prompt readiness report with score and actionable feedback."""
    normalized = normalize_form_data(form_data)

    weights = {
        "domain": 15,
        "specialization": 10,
        "specificGoal": 20,
        "action": 25,
        "details": 10,
        "constraints": 10,
        "format": 5,
        "structure": 3,
        "unwantedResult": 2,
    }
    required_fields = ["domain", "specificGoal", "action", "format"]

    score = 0
    for key, weight in weights.items():
        if key == "action":
            if _has_action_content(normalized["action"]):
                score += weight
        elif normalized.get(key):
            score += weight

    missing_required = [
        field for field in required_fields if not _field_has_value(normalized, field)
    ]

    warnings = _action_warnings(normalized["action"], lang)
    suggestions = _build_suggestions(missing_required, normalized, lang)

    return {
        "score": score,
        "missing_required": missing_required,
        "warnings": warnings,
        "suggestions": suggestions,
    }


def generate_prompt(form_data: Dict[str, Any], lang: str = "en") -> str:
    """Generate a structured AI prompt based on input fields."""
    normalized = normalize_form_data(form_data)
    if lang == "zh":
        return _generate_zh_prompt(normalized)
    return _generate_en_prompt(normalized)


def _generate_en_prompt(form_data: Dict[str, Any]) -> str:
    actions_str = _format_actions(form_data["action"], lang="en")
    structure = form_data.get("structure")

    lines = [
        "# <Role>",
        (
            "- You are an expert in "
            f"{form_data.get('domain') or '{domain}'} "
            f"with specialization in {form_data.get('specialization') or '{specialization}'}"
            "."
        ),
        "",
        "# <Task>",
        f"- Your task is to {form_data.get('specificGoal') or '{specific goal}'}.",
        "",
        "# <ReAct Framework: Reasoning & Action>",
        "## Reasoning",
        "- Let's think step by step.",
        "## Action",
        actions_str,
        "## Observation",
        "- Use the action results to produce the answer.",
        "",
        "# <Context>",
        "- Here is the context you need:",
        f"  - {form_data.get('details') or '{details}'}",
        f"  - {form_data.get('constraints') or '{constraints}'}",
        "",
        "# <Output Format>",
        (
            f"- Return a {form_data.get('format') or '{format}'} file"
            + (
                f" and follow this structure: {structure}."
                if structure
                else " (any structure is fine)."
            )
        ),
        f"- Don't {form_data.get('unwantedResult') or '{unwanted result}'}.",
    ]

    return "\n".join(lines)


def _generate_zh_prompt(form_data: Dict[str, Any]) -> str:
    actions_str = _format_actions(form_data["action"], lang="zh")
    structure = form_data.get("structure")

    lines = [
        "# <角色>",
        (
            "- 你是 "
            f"{form_data.get('domain') or '{領域}'} "
            f"的專家，專精於 {form_data.get('specialization') or '{專精項目}'}。"
        ),
        "",
        "# <任務>",
        f"- 你的任務是 {form_data.get('specificGoal') or '{具體目標}'}。",
        "",
        "# <先推理再行動>",
        "## 推理",
        "- 讓我們一步一步思考。",
        "## 行動",
        actions_str,
        "## 觀察",
        "- 依據行動的結果產出答案。",
        "",
        "# <背景>",
        "- 你需要的背景資訊：",
        f"  - {form_data.get('details') or '{背景細節}'}",
        f"  - {form_data.get('constraints') or '{限制條件}'}",
        "",
        "# <輸出格式>",
        (
            f"- 請以 {form_data.get('format') or '{輸出格式}'} 格式"
            + (
                f"，並依照下列結構：{structure}。"
                if structure
                else "，結構可自行決定。"
            )
        ),
        f"- 請避免 {form_data.get('unwantedResult') or '{避免結果}'}。",
    ]

    return "\n".join(lines)


def _format_actions(actions: List[Dict[str, str]], lang: str = "en") -> str:
    valid_actions = [action for action in actions if action.get("value")]

    if not valid_actions:
        return '- [搜尋("{行動}")]' if lang == "zh" else '- [Search("{action}")]'

    lines = []
    for action in valid_actions:
        action_type = action.get("type") or "Search"
        action_value = _escape_for_prompt(action.get("value", ""))

        if lang == "zh":
            action_type = ACTION_TYPE_MAP_ZH.get(action_type, action_type)

        lines.append(f'- [{action_type}("{action_value}")]')

    return "\n".join(lines)


def _action_warnings(actions: List[Dict[str, str]], lang: str) -> List[str]:
    warnings: List[str] = []
    for action in actions:
        action_type = action.get("type")
        value = action.get("value", "")
        if action_type != "Browse" or not value:
            continue
        if not _looks_like_url(value):
            warnings.append(
                "Browse actions should contain a valid URL (include https://)."
                if lang == "en"
                else "瀏覽類型建議填入有效網址（包含 https://）。"
            )
            break
    return warnings


def _build_suggestions(
    missing_required: List[str], form_data: Dict[str, Any], lang: str
) -> List[str]:
    suggestions: List[str] = []

    if missing_required:
        if lang == "en":
            suggestions.append("Fill all required fields first (Domain, Goal, Action, Format).")
        else:
            suggestions.append("先補齊必要欄位（領域、目標、行動、輸出格式）。")

    if not form_data.get("constraints"):
        suggestions.append(
            "Add at least one constraint to reduce vague answers."
            if lang == "en"
            else "建議補上一條限制條件，避免答案過於籠統。"
        )

    if not form_data.get("unwantedResult"):
        suggestions.append(
            "Define an unwanted result so the model knows what to avoid."
            if lang == "en"
            else "建議設定「避免結果」，讓模型更清楚要避開什麼。"
        )

    return suggestions


def _field_has_value(form_data: Dict[str, Any], key: str) -> bool:
    if key == "action":
        return _has_action_content(form_data.get("action", []))
    return bool(form_data.get(key))


def _has_action_content(actions: List[Dict[str, str]]) -> bool:
    return any(action.get("value") for action in actions)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value).strip()
    return value.strip()


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def _escape_for_prompt(value: str) -> str:
    return value.replace('"', '\\"')
