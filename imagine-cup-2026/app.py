import streamlit as st
import json

# Load content from JSON file
# with a function decorated with @st.cache_data to optimize performance.
# with a simple multi-page navigation system using session state.
# then we load the content and set up the initial page.


st.set_page_config(page_title="Personalized Study Coach", layout="centered")
@st.cache_data
def load_content():
    try:
        with open("content_pack.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Content file not found.")
        st.stop()
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON content.")
        st.stop()
content = load_content()

# We initialize the session state for page navigation. If no page is set, we start at the topic selection page.
if "page" not in st.session_state:
    st.session_state.page = "topic" 
if "answers" not in st.session_state:
    st.session_state.answers = {}
def go(page):
    st.session_state.page = page

# Topic selection page
if st.session_state.page == "topic":
    st.title("Personalized Study Coach")
    st.subheader("Choose a topic to study:")
    st.write("This MVP focuses on diagnosing misconceptions in a small set of CS concepts.")
    
    if st.button(content.get("topic","Start"), key="btn_start"):
        st.session_state.answers = {}
        go("diagnostic")

# Diagnostic questions
elif st.session_state.page == "diagnostic":
    st.title("Diagnostic Questions")
    st.write("Please answer briefly the following questions:")

    for q in content.get("diagnostic", []):
        qid = q["id"]
        question = q["question"]

        default = st.session_state.answers.get(qid, "")
        answer = st.text_input(question, value=default, key=f"input_{qid}")
        st.session_state.answers[qid] = answer

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", key="btn_back_to_topic"):
            go("topic")
    with col2:
        if st.button("Submit answers", key="btn_submit_to_results"):
            go("results")

# Results page
elif st.session_state.page == "results":
    st.title("Your results")

    st.write("Here are your answers:")
    if not st.session_state.answers:
        st.write("No answers provided.")
    else:
        for qid, ans in st.session_state.answers.items():
            st.write(f"**{qid}**: {ans if ans.strip() else '-'}")
    st.info("We'll Analyze misconceptions using Azure OpenAI")

    if st.button("Back to Topics", key="btn_back_to_topics"):
        go("topic")
