import streamlit as st  # type: ignore
import requests  # type: ignore

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Translation UI", layout="centered")
st.title("🌐 Translation Service UI")

# Load supported languages
try:
    response = requests.get(f"{BACKEND_URL}/supported-languages")
    if response.status_code == 200:
        supported_languages = response.json().get("language_guide", {})
        supported_codes = set(supported_languages.values())
    else:
        st.error("❌ Failed to load supported languages.")
        supported_languages = {}
        supported_codes = set()
except Exception as e:
    st.error(f"❌ Backend connection error: {e}")
    supported_languages = {}
    supported_codes = set()

# Show supported languages
if supported_languages:
    st.subheader("📚 Supported Languages")
    for lang, code in supported_languages.items():
        st.markdown(f"- **{lang}** — `{code}`")

# Sidebar navigation
option = st.sidebar.selectbox("Select Operation", (
    "Single Translate",
    "Bulk Translate",
    "Health Check",
    "View Logs"
))

# ---- SINGLE TRANSLATE ----
if option == "Single Translate":
    st.subheader("✏️ Single Translate")
    text = st.text_area("Enter text (max 1000 characters):")
    lang = st.text_input("Enter language code (e.g., en, hi, ta):")

    if st.button("Translate"):
        try:
            res = requests.post(f"{BACKEND_URL}/translate", json={
                "input_text": text,
                "destination_language": lang
            })

            if res.status_code == 200:
                st.success("✅ Translation Successful")
                st.write(res.json().get("output_text"))
            else:
                detail = res.json().get("detail")
                if isinstance(detail, list):
                    for err in detail:
                        st.error(err)
                else:
                    st.error(f"⚠️ Error: {detail}")

        except Exception as e:
            st.error(f"⚠️ Request Failed: {e}")

# ---- BULK TRANSLATE ----
elif option == "Bulk Translate":
    st.subheader("📦 Bulk Translate")
    text_input = st.text_area("Enter sentences (one per line, max 1000 characters each):")
    lang = st.text_input("Enter language code:")

    if st.button("Bulk Translate"):
        lines = [line.strip() for line in text_input.split("\n") if line.strip()]

        try:
            res = requests.post(f"{BACKEND_URL}/translate/bulk", json={
                "input_texts": lines,
                "destination_language": lang
            })

            if res.status_code == 200:
                output_lines = res.json().get("output_texts", [])
                st.success("✅ Bulk Translation Results:")
                for i, (inp, out) in enumerate(zip(lines, output_lines), 1):
                    st.markdown(f"**{i}.** {inp} → _{out}_")
            else:
                detail = res.json().get("detail")
                if isinstance(detail, list):
                    for err in detail:
                        st.error(err)
                else:
                    st.error(f"⚠️ Error: {detail}")

        except Exception as e:
            st.error(f"⚠️ Request Failed: {e}")

# ---- HEALTH CHECK ----
elif option == "Health Check":
    st.subheader("🩺 Health Check")
    try:
        res = requests.get(f"{BACKEND_URL}/health")
        if res.status_code == 200:
            st.success(f"✅ Service is healthy: {res.json().get('status')}")
        else:
            st.error("❌ Health check failed.")
    except Exception as e:
        st.error(f"⚠️ Could not connect to backend: {e}")

# ---- VIEW LOGS ----
elif option == "View Logs":
    st.subheader("📜 Translation Logs")
    try:
        res = requests.get(f"{BACKEND_URL}/logs")
        if res.status_code == 200:
            logs = res.json()
            if logs:
                for log in logs:
                    st.markdown(f"- [{log['translated_at']}] **{log['original_text']}** → _{log['translated_text']}_ (`{log['language']}`)")
            else:
                st.info("ℹ️ No logs found.")
        else:
            st.error("❌ Could not fetch logs from backend.")
    except Exception as e:
        st.error(f"⚠️ Failed to load logs: {e}")
