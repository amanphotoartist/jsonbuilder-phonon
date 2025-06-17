import streamlit as st
import uuid
import json

st.set_page_config("JSON Builder - aman (Phonon)", layout="wide")
st.title("🔘 JSON Builder - PHONON")

# Initialize session state
if "tree" not in st.session_state:
    st.session_state.tree = {}
    st.session_state.root_buttons = []

def create_node(button_text="", reply_text="", labels=None, parent_id=None):
    return {
        "id": str(uuid.uuid4()),
        "buttonText": button_text,
        "replyText": reply_text,
        "stringButtonList": labels or [],
        "buttons": [],
        "parentId": parent_id,
        "templateId": "",
        "templateParams": [],
        "isCarousel": False,
        "carouselCards": []
    }

def render_node(node_id, depth=0):
    node = st.session_state.tree[node_id]
    parent_text = ""
    if node["parentId"]:
        parent_node = st.session_state.tree.get(node["parentId"])
        if parent_node:
            parent_text = f" (Parent: {parent_node['buttonText'] or 'Unnamed'})"

    st.markdown("---")
    st.subheader(f"🔘 Button: {node['buttonText'] or 'Unnamed'}{parent_text}")
    node["buttonText"] = st.text_input("Button Text", node["buttonText"], key=f"text_{node_id}")
    node["replyText"] = st.text_area("Reply Text", node["replyText"], key=f"reply_{node_id}")
    label_text = st.text_input("Labels (comma separated)", ", ".join(node["stringButtonList"]), key=f"labels_{node_id}")
    node["stringButtonList"] = [l.strip() for l in label_text.split(",") if l.strip()]

    node["templateId"] = st.text_input("Template ID", node["templateId"], key=f"tmpl_{node_id}")
    param_text = st.text_input("Template Params (comma separated)", ", ".join(node["templateParams"]), key=f"params_{node_id}")
    node["templateParams"] = [p.strip() for p in param_text.split(",") if p.strip()]

    node["isCarousel"] = st.checkbox("Is Carousel?", value=node["isCarousel"], key=f"carousel_{node_id}")

    if node["isCarousel"]:
        st.markdown("##### 🎠 Carousel Cards")
        num_existing = len(node["carouselCards"])
        add_card = st.button("➕ Add Carousel Card", key=f"add_card_{node_id}")
        if add_card:
            node["carouselCards"].append({"mediaUrl": "", "mediaType": "IMAGE", "params": []})

        for idx, card in enumerate(node["carouselCards"]):
            st.text_input("Media URL", card["mediaUrl"], key=f"media_url_{node_id}_{idx}", on_change=lambda i=idx: node["carouselCards"][i].update({"mediaUrl": st.session_state[f"media_url_{node_id}_{i}"]}))
            card["mediaType"] = st.selectbox("Media Type", ["IMAGE", "VIDEO"], index=0 if card["mediaType"] == "IMAGE" else 1, key=f"media_type_{node_id}_{idx}")

    # Label-based Sub Button Adder
    with st.expander("➕ Add Sub Button", expanded=False):
        if node["stringButtonList"]:
            selected_label = st.selectbox("Select a label to use as sub-button", node["stringButtonList"], key=f"label_select_{node_id}")
            if st.button("✅ Confirm Add Sub Button", key=f"confirm_add_{node_id}"):
                child_node = create_node(button_text=selected_label, parent_id=node_id)
                st.session_state.tree[child_node["id"]] = child_node
                node["buttons"].append(child_node["id"])
        else:
            st.info("ℹ️ Please enter at least one label above to create sub-buttons.")

    # Render child nodes
    for child_id in node["buttons"]:
        render_node(child_id, depth + 1)

# ➕ Add new root button
if st.button("➕ Add Root Button"):
    root_node = create_node()
    st.session_state.tree[root_node["id"]] = root_node
    st.session_state.root_buttons.append(root_node["id"])

# 🔄 Render all root buttons
for root_id in st.session_state.root_buttons:
    render_node(root_id)

# ✅ Generate JSON
if st.button("✅ Generate JSON"):
    def build_json(node_id, stage_id="1", parent_id=None, depth=0):
        node = st.session_state.tree[node_id]
        button_data = {
            "buttonId": str(depth),
            "stageId": stage_id,
            "buttonText": node["buttonText"],
            "replyText": node["replyText"],
            "templateId": node["templateId"],
            "templateParams": node["templateParams"],
            "isCarousel": node["isCarousel"],
            "stringButtonList": node["stringButtonList"],
            "buttons": [build_json(child_id, str(int(stage_id) + 1), str(depth + i), depth + i) for i, child_id in enumerate(node["buttons"])]
        }
        if node["isCarousel"]:
            button_data["carousel"] = {
                "carouselCards": node["carouselCards"]
            }
        if parent_id is not None:
            button_data["parentButtonId"] = parent_id
        return button_data

    # Build full JSON
    final_buttons = [build_json(root_id, "1") for root_id in st.session_state.root_buttons]
    final_json = {
        "root": {
            "stageId": "0",
            "templateId": "",  # You can add a global templateId here if needed
            "stringButtonList": [st.session_state.tree[rid]["buttonText"] for rid in st.session_state.root_buttons],
            "buttons": final_buttons
        }
    }

    st.success("✅ JSON generated successfully!")
    st.json(final_json)
    st.download_button("📥 Download JSON", data=json.dumps(final_json, indent=2), file_name="generated_json.json", mime="application/json")
