import io
import json

import streamlit as st
from streamlit_option_menu import option_menu

from utils import (
    get_default_form_data,
    get_prompt_health_report,
    get_prompt_presets,
    generate_prompt,
    normalize_form_data,
)

st.set_page_config(page_title="Structured Prompt Generator", page_icon="🎩", layout="wide")

ACTION_TYPES_I18N = {
    "en": [
        {
            "type": "Search",
            "label": "Search",
            "input_label": "Query",
            "placeholder": "e.g. latest AI news, market trend, competitor updates",
            "desc": "Find up-to-date info on the web.",
        },
        {
            "type": "Lookup",
            "label": "Lookup",
            "input_label": "Topic",
            "placeholder": "e.g. LLM theory basics, Python list vs tuple, SWOT analysis",
            "desc": "Quickly learn a concept or topic.",
        },
        {
            "type": "Browse",
            "label": "Browse",
            "input_label": "URL",
            "placeholder": "e.g. https://arxiv.org/abs/...",
            "desc": "Read a specific web page.",
        },
    ],
    "zh": [
        {
            "type": "Search",
            "label": "搜尋",
            "input_label": "查詢內容",
            "placeholder": "例如：最新 AI 新聞、市場趨勢、競品資訊",
            "desc": "在網路上找最新資訊。",
        },
        {
            "type": "Lookup",
            "label": "查找",
            "input_label": "主題",
            "placeholder": "例如：LLM 基本觀念、Python list 與 tuple 差異",
            "desc": "快速了解一個概念或主題。",
        },
        {
            "type": "Browse",
            "label": "瀏覽",
            "input_label": "網址",
            "placeholder": "例如：https://openai.com/blog",
            "desc": "閱讀指定網頁內容。",
        },
    ],
}

FIELDS_I18N = {
    "en": [
        {
            "key": "domain",
            "title": "Domain",
            "placeholder": "e.g. digital marketing, machine learning, financial planning",
            "description": "The general field you are working in.",
            "section": "Role",
        },
        {
            "key": "specialization",
            "title": "Specialization",
            "placeholder": "e.g. deep learning and NLP, investment analysis, product-led growth",
            "description": "Your focus inside the domain.",
            "section": "Role",
        },
        {
            "key": "specificGoal",
            "title": "Specific Goal",
            "placeholder": "e.g. create a 90-day go-to-market strategy for a B2B startup",
            "description": "Describe what you want in one sentence.",
            "section": "Task",
        },
        {
            "key": "action",
            "title": "Action",
            "placeholder": "",
            "description": "",
            "section": "Action",
        },
        {
            "key": "details",
            "title": "Context Details",
            "placeholder": "e.g. audience profile, budget, tech stack, data size",
            "description": "Key facts the assistant should know.",
            "section": "Context",
        },
        {
            "key": "constraints",
            "title": "Constraints",
            "placeholder": "e.g. must comply with GDPR, 8-week timeline, no paid ads",
            "description": "Rules or limits to follow.",
            "section": "Context",
        },
        {
            "key": "format",
            "title": "Output Format",
            "placeholder": "e.g. markdown, JSON, slide outline, report",
            "description": "Preferred format of the final answer.",
            "section": "Output",
        },
        {
            "key": "structure",
            "title": "Structure",
            "placeholder": "e.g. {summary, analysis, recommendations, timeline}",
            "description": "Optional fixed structure for output.",
            "section": "Output",
        },
        {
            "key": "unwantedResult",
            "title": "Unwanted Result",
            "placeholder": "e.g. generic advice, no data, over 1,000 words",
            "description": "What should be avoided.",
            "section": "Output",
        },
    ],
    "zh": [
        {
            "key": "domain",
            "title": "領域",
            "placeholder": "例如：數位行銷、機器學習、財務規劃",
            "description": "你正在處理的主要範疇。",
            "section": "角色",
        },
        {
            "key": "specialization",
            "title": "專精項目",
            "placeholder": "例如：NLP、投資分析、產品成長",
            "description": "你在此領域中的專注方向。",
            "section": "角色",
        },
        {
            "key": "specificGoal",
            "title": "具體目標",
            "placeholder": "例如：為新創產品設計 90 天成長策略",
            "description": "一句話說清楚要達成的結果。",
            "section": "任務",
        },
        {
            "key": "action",
            "title": "行動",
            "placeholder": "",
            "description": "",
            "section": "行動",
        },
        {
            "key": "details",
            "title": "背景細節",
            "placeholder": "例如：受眾輪廓、預算、技術限制、資料規模",
            "description": "助理需要知道的關鍵資訊。",
            "section": "背景",
        },
        {
            "key": "constraints",
            "title": "限制條件",
            "placeholder": "例如：需符合 GDPR、時程 8 週、不能投放廣告",
            "description": "需要遵守的規則或限制。",
            "section": "背景",
        },
        {
            "key": "format",
            "title": "輸出格式",
            "placeholder": "例如：markdown、JSON、簡報大綱、報告",
            "description": "希望收到的最終格式。",
            "section": "輸出",
        },
        {
            "key": "structure",
            "title": "結構",
            "placeholder": "例如：{摘要, 分析, 建議, 里程碑}",
            "description": "可選填，指定輸出段落結構。",
            "section": "輸出",
        },
        {
            "key": "unwantedResult",
            "title": "避免結果",
            "placeholder": "例如：泛泛而談、沒有數據、超過 1,000 字",
            "description": "希望模型避免的內容。",
            "section": "輸出",
        },
    ],
}

SECTION_ITEMS = {
    "en": [
        {"icon": "🧑‍💼", "title": "Role", "desc": "Clarify domain and specialization."},
        {"icon": "🎯", "title": "Task", "desc": "State one concrete goal."},
        {"icon": "🔍", "title": "Action", "desc": "List Search / Lookup / Browse steps."},
        {"icon": "📚", "title": "Context", "desc": "Provide constraints and background."},
        {"icon": "📤", "title": "Output", "desc": "Define format and quality bar."},
    ],
    "zh": [
        {"icon": "🧑‍💼", "title": "角色", "desc": "先定義領域與專精。"},
        {"icon": "🎯", "title": "任務", "desc": "描述單一且清楚的目標。"},
        {"icon": "🔍", "title": "行動", "desc": "規劃搜尋、查找、瀏覽步驟。"},
        {"icon": "📚", "title": "背景", "desc": "補上情境與限制條件。"},
        {"icon": "📤", "title": "輸出", "desc": "指定格式與品質要求。"},
    ],
}

APP_I18N = {
    "en": {
        "title": "Structured Prompt Generator",
        "subtitle": "Build stronger prompts with real-time quality feedback.",
        "intro_tab": "Guide",
        "build_tab": "Build Prompt",
        "guide_title": "How this builder helps",
        "guide_intro": "Use presets, fill key fields, and improve score before exporting.",
        "guide_tips": [
            "Start with Domain + Specific Goal for the biggest quality boost.",
            "Use multiple actions to show the assistant your workflow.",
            "Add constraints to reduce vague responses.",
        ],
        "workspace": "Prompt Workspace",
        "quality_score": "Prompt Score",
        "required_label": "Missing required fields",
        "none": "None",
        "preset_label": "Starter preset",
        "preset_placeholder": "Select one",
        "apply_preset": "Apply preset",
        "reset": "Reset form",
        "fill_header": "Parameters",
        "preview_header": "Prompt Preview",
        "preview_tip": "Tip: the code block has a built-in copy button.",
        "download_prompt": "Download .txt",
        "download_json": "Download JSON",
        "insights_tab": "Insights",
        "state_tab": "Form State",
        "warnings": "Warnings",
        "suggestions": "Suggestions",
        "all_good": "Looks good. You can export now.",
        "add_action": "+ Add Action",
        "remove": "Remove",
        "structure_toggle": "Specify output structure",
        "estimated_tokens": "Estimated prompt tokens",
    },
    "zh": {
        "title": "結構化提示詞生成器",
        "subtitle": "用即時品質回饋，打造更強的提示詞。",
        "intro_tab": "使用指南",
        "build_tab": "開始建立",
        "guide_title": "這個工具如何幫你",
        "guide_intro": "先套用範本，再補齊關鍵欄位，最後看分數再匯出。",
        "guide_tips": [
            "先填「領域」與「具體目標」，效果提升最大。",
            "用多個行動步驟，讓模型知道你的工作流程。",
            "加上限制條件，可以明顯降低空泛回答。",
        ],
        "workspace": "提示詞工作區",
        "quality_score": "提示詞分數",
        "required_label": "尚未完成的必要欄位",
        "none": "無",
        "preset_label": "快速範本",
        "preset_placeholder": "請選擇",
        "apply_preset": "套用範本",
        "reset": "重置表單",
        "fill_header": "參數設定",
        "preview_header": "提示詞預覽",
        "preview_tip": "小提醒：程式碼區塊右上角可直接複製。",
        "download_prompt": "下載 .txt",
        "download_json": "下載 JSON",
        "insights_tab": "品質建議",
        "state_tab": "表單狀態",
        "warnings": "警示",
        "suggestions": "建議",
        "all_good": "內容很完整，可以直接匯出。",
        "add_action": "+ 新增行動",
        "remove": "刪除",
        "structure_toggle": "指定輸出結構",
        "estimated_tokens": "預估提示詞 token",
    },
}

SECTIONS = {"en": ["Role", "Task", "Action", "Context", "Output"], "zh": ["角色", "任務", "行動", "背景", "輸出"]}


def init_state() -> None:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    if "form_data" not in st.session_state:
        st.session_state["form_data"] = get_default_form_data()
    else:
        st.session_state["form_data"] = normalize_form_data(st.session_state["form_data"])
    if "form_version" not in st.session_state:
        st.session_state["form_version"] = 0


def overwrite_form_data(new_data: dict) -> None:
    st.session_state["form_data"] = normalize_form_data(new_data)
    st.session_state["form_version"] += 1
    st.rerun()


def field_title_map(fields: list[dict]) -> dict:
    return {field["key"]: field["title"] for field in fields}


def render_intro(ui: dict, lang: str) -> None:
    st.subheader(ui["guide_title"])
    st.markdown(ui["guide_intro"])

    cols = st.columns(5)
    for idx, item in enumerate(SECTION_ITEMS[lang]):
        with cols[idx]:
            st.markdown(
                f"""
                <div style='padding:0.9rem;border:1px solid #E5E7EB;border-radius:12px;height:150px;'>
                    <div style='font-size:1.6rem'>{item['icon']}</div>
                    <div style='font-weight:700;margin-top:0.3rem'>{item['title']}</div>
                    <div style='font-size:0.92rem;color:#4B5563;margin-top:0.3rem'>{item['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    for tip in ui["guide_tips"]:
        st.markdown(f"- {tip}")


def render_action_inputs(form_data: dict, lang: str, ui: dict, form_version: int) -> None:
    action_types = ACTION_TYPES_I18N[lang]
    actions = form_data.get("action", [])
    remove_idx = None

    for index, action in enumerate(actions):
        card = st.container(border=True)
        with card:
            c1, c2 = st.columns([7, 1])
            with c1:
                action_type_key = f"v{form_version}_{lang}_action_type_{index}"
                action_value_key = f"v{form_version}_{lang}_action_value_{index}"

                selected_type = st.selectbox(
                    label=f"#{index + 1}",
                    options=[item["type"] for item in action_types],
                    index=next(
                        (
                            i
                            for i, item in enumerate(action_types)
                            if item["type"] == action.get("type", "Search")
                        ),
                        0,
                    ),
                    format_func=lambda value: next(
                        (item["label"] for item in action_types if item["type"] == value),
                        value,
                    ),
                    key=action_type_key,
                )

                type_config = next(
                    (item for item in action_types if item["type"] == selected_type),
                    action_types[0],
                )
                action_value = st.text_area(
                    label=type_config["input_label"],
                    value=action.get("value", ""),
                    placeholder=type_config["placeholder"],
                    help=type_config["desc"],
                    key=action_value_key,
                )
                actions[index] = {"type": selected_type, "value": action_value.strip()}

            with c2:
                if len(actions) > 1:
                    if st.button(ui["remove"], key=f"v{form_version}_{lang}_remove_{index}"):
                        remove_idx = index

    if remove_idx is not None:
        actions.pop(remove_idx)
        st.session_state["form_data"]["action"] = actions
        st.rerun()

    if st.button(ui["add_action"], key=f"v{form_version}_{lang}_add_action"):
        actions.append({"type": action_types[0]["type"], "value": ""})
        st.session_state["form_data"]["action"] = actions
        st.rerun()

    st.session_state["form_data"]["action"] = actions


def render_builder(ui: dict, fields: list[dict], lang: str) -> None:
    form_data = st.session_state["form_data"]
    form_version = st.session_state["form_version"]
    title_by_key = field_title_map(fields)
    report = get_prompt_health_report(form_data, lang)
    presets = get_prompt_presets(lang)

    with st.sidebar:
        st.subheader(ui["workspace"])
        st.metric(ui["quality_score"], f"{report['score']}%")
        st.progress(report["score"] / 100)

        missing_labels = [title_by_key.get(key, key) for key in report["missing_required"]]
        if missing_labels:
            st.caption(ui["required_label"])
            for label in missing_labels:
                st.markdown(f"- {label}")
        else:
            st.caption(f"{ui['required_label']}: {ui['none']}")

        preset_names = [ui["preset_placeholder"], *list(presets.keys())]
        selected_preset = st.selectbox(ui["preset_label"], options=preset_names)
        if st.button(ui["apply_preset"], use_container_width=True):
            if selected_preset != ui["preset_placeholder"]:
                overwrite_form_data(presets[selected_preset])

        if st.button(ui["reset"], use_container_width=True):
            overwrite_form_data(get_default_form_data())

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        st.subheader(ui["fill_header"])

        for section in SECTIONS[lang]:
            with st.expander(section, expanded=(section == SECTIONS[lang][0])):
                if section == ("Action" if lang == "en" else "行動"):
                    render_action_inputs(form_data, lang, ui, form_version)
                    continue

                for field in [item for item in fields if item["section"] == section and item["key"] != "action"]:
                    if field["key"] == "structure":
                        toggle_key = f"v{form_version}_{lang}_structure_toggle"
                        include_structure = st.checkbox(
                            ui["structure_toggle"],
                            value=bool(form_data.get("structure")),
                            key=toggle_key,
                        )
                        if include_structure:
                            structure_key = f"v{form_version}_{lang}_field_structure"
                            form_data["structure"] = st.text_area(
                                label=field["title"],
                                value=form_data.get("structure", ""),
                                placeholder=field["placeholder"],
                                help=field["description"],
                                key=structure_key,
                            ).strip()
                        else:
                            form_data["structure"] = ""
                        continue

                    widget_key = f"v{form_version}_{lang}_field_{field['key']}"
                    form_data[field["key"]] = st.text_area(
                        label=field["title"],
                        value=form_data.get(field["key"], ""),
                        placeholder=field["placeholder"],
                        help=field["description"],
                        key=widget_key,
                    ).strip()

        st.session_state["form_data"] = form_data

    with right:
        st.subheader(ui["preview_header"])
        prompt = generate_prompt(form_data, lang)
        approx_tokens = max(1, len(prompt) // 4)

        preview_tab, insights_tab, state_tab = st.tabs(
            [ui["preview_header"], ui["insights_tab"], ui["state_tab"]]
        )

        with preview_tab:
            st.code(prompt, language="markdown")
            st.caption(ui["preview_tip"])
            st.caption(f"{ui['estimated_tokens']}: {approx_tokens}")

            txt_buffer = io.StringIO()
            txt_buffer.write(prompt)
            st.download_button(
                label=ui["download_prompt"],
                data=txt_buffer.getvalue(),
                file_name=f"generated_prompt_{lang}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.download_button(
                label=ui["download_json"],
                data=json.dumps(form_data, indent=2, ensure_ascii=False),
                file_name=f"prompt_form_{lang}.json",
                mime="application/json",
                use_container_width=True,
            )

        with insights_tab:
            if report["warnings"]:
                st.markdown(f"**{ui['warnings']}**")
                for warning in report["warnings"]:
                    st.warning(warning)

            if report["suggestions"]:
                st.markdown(f"**{ui['suggestions']}**")
                for item in report["suggestions"]:
                    st.info(item)

            if not report["warnings"] and not report["suggestions"]:
                st.success(ui["all_good"])

        with state_tab:
            st.json(form_data)


def main() -> None:
    init_state()

    language = option_menu(
        menu_title=None,
        options=["English", "中文"],
        icons=["translate", "translate"],
        orientation="horizontal",
        default_index=0 if st.session_state["lang"] == "en" else 1,
    )

    st.session_state["lang"] = "en" if language == "English" else "zh"
    lang = st.session_state["lang"]
    ui = APP_I18N[lang]
    fields = FIELDS_I18N[lang]

    st.markdown(
        f"""
        <div style='text-align:center; padding-top: 0.4rem;'>
            <div style='font-size:1.8rem;font-weight:700'>{ui['title']}</div>
            <div style='font-size:1.02rem;color:#6B7280'>{ui['subtitle']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    main_section = option_menu(
        menu_title=None,
        options=[ui["intro_tab"], ui["build_tab"]],
        icons=["book", "pencil-square"],
        orientation="horizontal",
    )

    if main_section == ui["intro_tab"]:
        render_intro(ui, lang)
    else:
        render_builder(ui, fields, lang)


if __name__ == "__main__":
    main()
