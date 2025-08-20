import json
import streamlit as st
from pathlib import Path

# --- CONFIGURATION ---
CONTENT_FILE = Path("content.json")

# Icon and Color definitions
ICON_MAP = {
    "Default Check": "https://cdn.jsdelivr.net/npm/lucide-static/icons/check-circle.svg",
    "CPU": "https://cdn.jsdelivr.net/npm/lucide-static/icons/cpu.svg",
    "AI Bot": "https://cdn.jsdelivr.net/npm/lucide-static/icons/bot.svg",
    "Cloud": "https://cdn.jsdelivr.net/npm/lucide-static/icons/cloud.svg",
    "Database": "https://cdn.jsdelivr.net/npm/lucide-static/icons/database.svg",
    "Firmware": "https://cdn.jsdelivr.net/npm/lucide-static/icons/hard-drive.svg",
    "Code": "https://cdn.jsdelivr.net/npm/lucide-static/icons/code-2.svg",
    "Layers": "https://cdn.jsdelivr.net/npm/lucide-static/icons/layers.svg",
    "Dashboard": "https://cdn.jsdelivr.net/npm/lucide-static/icons/layout-dashboard.svg",
    "Eye Scan": "https://cdn.jsdelivr.net/npm/lucide-static/icons/scan-eye.svg",
    "Server": "https://cdn.jsdelivr.net/npm/lucide-static/icons/server.svg",
    "Signal": "https://cdn.jsdelivr.net/npm/lucide-static/icons/activity.svg",
    "WiFi": "https://cdn.jsdelivr.net/npm/lucide-static/icons/wifi.svg",
}
ICON_NAME_MAP = {v: k for k, v in ICON_MAP.items()}
COLOR_OPTIONS = ["cyan", "teal", "blue", "purple", "orange", "red", "green", "pink", "yellow", "indigo"]

# --- DATA HANDLING ---
def load_content():
    """Loads content from the JSON file."""
    try:
        with open(CONTENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"caseStudies": []}

def save_content(data):
    """Saves data to the JSON file."""
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Case Study Editor", layout="wide")
st.title("📝 Case Study Editor")

if 'content' not in st.session_state:
    st.session_state.content = load_content()

# --- 1. CASE STUDY CONTENT EDITOR ---
st.header("Edit Case Study Content")

case_studies_list = st.session_state.content.get("caseStudies", [])
case_titles = [cs.get("title", "Untitled") for cs in case_studies_list]

selected_title = st.selectbox(
    "Select a Case Study to Edit or Add New",
    ["➕ Add New"] + case_titles,
    key="sb_select_case_study"
)

if selected_title == "➕ Add New":
    if 'new_case_study' not in st.session_state or st.session_state.get('last_selected') != "➕ Add New":
        st.session_state.new_case_study = {"tag": "New Tag", "title": "", "color": "cyan", "challenge": "", "solution": "", "outcomes": [], "stack": []}
    cs_data = st.session_state.new_case_study
else:
    selected_index = case_titles.index(selected_title)
    cs_data = case_studies_list[selected_index]

st.session_state.last_selected = selected_title

if cs_data:
    # The form is now ONLY for text content and the main save button
    with st.form("case_study_content_form"):
        st.subheader(f"Editing Content for: {selected_title if selected_title != '➕ Add New' else 'New Case Study'}")

        cs_data["tag"] = st.text_input("Tag", cs_data.get("tag", ""))
        cs_data["title"] = st.text_input("Title", cs_data.get("title", ""))
        cs_data["color"] = st.selectbox("Color", COLOR_OPTIONS, index=COLOR_OPTIONS.index(cs_data.get("color", "cyan")))
        cs_data["challenge"] = st.text_area("Challenge", cs_data.get("challenge", ""), height=100)
        cs_data["solution"] = st.text_area("Solution", cs_data.get("solution", ""), height=100)

        if st.form_submit_button("💾 Save Text Content"):
            if not cs_data.get("title"):
                st.error("Title cannot be empty.")
            else:
                if selected_title == "➕ Add New":
                    st.session_state.content["caseStudies"].append(cs_data)
                save_content(st.session_state.content)
                st.success(f"Content for '{cs_data['title']}' saved!")
                if selected_title == "➕ Add New":
                    del st.session_state.new_case_study
                st.rerun()

    # --- LIST MANAGEMENT (Outcomes & Stack) is now OUTSIDE the form ---
    st.markdown("---")
    st.subheader("Edit Outcomes")
    for i, oc in enumerate(cs_data.get("outcomes", [])):
        col1, col2, col3 = st.columns([3, 6, 1])
        selected_icon_name = ICON_NAME_MAP.get(oc.get("icon"), "Default Check")
        new_icon_name = col1.selectbox("Icon", list(ICON_MAP.keys()), index=list(ICON_MAP.keys()).index(selected_icon_name), key=f"oc_icon_{i}")
        oc["icon"] = ICON_MAP[new_icon_name]
        oc["text"] = col2.text_input("Text", oc.get("text", ""), key=f"oc_text_{i}")
        if col3.button("🗑️", key=f"del_oc_{i}", help="Remove Outcome"):
            cs_data["outcomes"].pop(i)
            st.rerun()
    if st.button("Add Outcome"):
        cs_data.setdefault("outcomes", []).append({"icon": ICON_MAP["Default Check"], "text": ""})
        st.rerun()

    st.markdown("---")
    st.subheader("Edit Tech Stack")
    for i, sc in enumerate(cs_data.get("stack", [])):
        col1, col2, col3 = st.columns([3, 6, 1])
        selected_icon_name = ICON_NAME_MAP.get(sc.get("icon"), "Default Check")
        new_icon_name = col1.selectbox("Icon", list(ICON_MAP.keys()), index=list(ICON_MAP.keys()).index(selected_icon_name), key=f"st_icon_{i}")
        sc["icon"] = ICON_MAP[new_icon_name]
        sc["text"] = col2.text_input("Text", sc.get("text", ""), key=f"st_text_{i}")
        if col3.button("🗑️", key=f"del_st_{i}", help="Remove Stack Item"):
            cs_data["stack"].pop(i)
            st.rerun()
    if st.button("Add Stack Item"):
        cs_data.setdefault("stack", []).append({"icon": ICON_MAP["Default Check"], "text": ""})
        st.rerun()


# --- 2. ARRANGE & REMOVE CASE STUDIES ---
st.markdown("---")
st.header("Arrange & Remove Case Studies")

current_case_studies = st.session_state.content.get("caseStudies", [])
if not current_case_studies:
    st.warning("No case studies to arrange. Add one using the editor above.")
else:
    st.info("Use the 'Up' and 'Down' buttons to reorder. Press 'Save Arrangement' when done.")
    
    for i, cs in enumerate(current_case_studies):
        col1, col2, col3 = st.columns([8, 1, 1])
        col1.markdown(f"**{i+1}. {cs.get('title', 'Untitled')}**")
        if col2.button("⬆️ Up", key=f"up_{i}", disabled=(i == 0)):
            current_case_studies.insert(i-1, current_case_studies.pop(i))
            st.rerun()
        if col3.button("⬇️ Down", key=f"down_{i}", disabled=(i == len(current_case_studies)-1)):
            current_case_studies.insert(i+1, current_case_studies.pop(i))
            st.rerun()
    
    if st.button("💾 Save Arrangement"):
        save_content(st.session_state.content)
        st.success("Case study arrangement has been saved!")

    st.markdown("---")
    st.subheader("Remove a Case Study")
    all_titles = [cs.get("title", "Untitled") for cs in current_case_studies]
    title_to_remove = st.selectbox("Select a case study to permanently delete", ["-"] + all_titles, key="remove_selectbox")
    if st.button("Permanently Remove", type="primary"):
        if title_to_remove != "-":
            new_list_after_removal = [cs for cs in current_case_studies if cs.get("title") != title_to_remove]
            st.session_state.content['caseStudies'] = new_list_after_removal
            save_content(st.session_state.content)
            st.success(f"Case study '{title_to_remove}' has been removed.")
            st.rerun()
        else:
            st.warning("Please select a case study to remove.")