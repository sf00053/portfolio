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

#Waiting for Mallie so this is to see how it would look like 
FALLBACK_MISCONCEPTIONS = [
    {"id":"M1","name":"Confusing  n with values","desc":"Student focuses on values inside the input rather than input size n."},
    {"id":"M2","name":"Constants matter in Big-O","desc":"Student treats factors as diferent Big-O classes."},
    {"id":"M3","name":"Halving is linear","desc":"Student doesn't connect repeated halving with logarithmic growth."},
    {"id":"M4","name":"Best vs Worst case confusion","desc":"Student mixes best or average case with worst-case analysis."},
]

HELP_PACK ={
    "M1": {
        "explanation":"Big-O describes how runtime grows with the number of items n. The actual values (big/small numbers) usually do not change how many steps your algorithm performs.",
        "hints":[
            "Ask: Does the loop run more times if the numbers are bigger?",
            "If you replace all values with 0, does the number of iterations change?",
            "Big-O depends on n (input size), not the values stored."
        ]
    },
    "M2":{
        "explanation":"Big-O ignores constant multipliers. If something takes 2n step, it still grow linearly with n, so it is O(n).",
        "hints":[
            "Compare 2n and n when n is very large-same growth type.",
            "Big-o keeps the fastest growing part and drops constants.",
            "O(2n)-> drop the 2 -> O(n)."
        ]

    },
    "M3":{
        "explanation":"If you halve the input each stp, you reach 1 in about log₂(n) steps. That is why repeated halving is O(log n), not O(n).",
        "hints":[
            "How many times can you divide 64 by 2 until it becomes 1?",
            "Each steps shrinks the problem by a factor of 2 (not subtracting 1).",
            "Number of halving steps ≈ log₂(n) -> O(log n)."
        ]
    },
    "M4":{
        "explanation":"Best case is the luckiest scenario; worst case is the slowest. If the question doesn't specify, computer science usually expects worst case.",
        "hints":[
            "Could the algorithm ever need to check all elements?",
            "Worst case means maximum work for input size n.",
            "If unsure, assume worst-case for Big-O."
        ]
    },
    "CORRECT":{
        "explanation":"Your answers looks correct. Explain it in one sentece and give a small example.",
        "hints":[
            "Say the core idea in one sentence",
            "Try an example with n = 8 or 16.",
            "Explain why growth rate matters more than exact time."
        ]
    },
    "NEEDS_MORE_INPUT": {
        "explanation": "Please write a short attempt (even 1 sentence). Then I can diagnose the misconception and help you.",
        "hints": [
            "Try writing what you think the growth is as n increases.",
            "If you're unsure, guess and explain why.",
            "Even a short attempt helps the coach guide you."
        ]
    }
}
PRACTICE_PACK = {
    "M1": [
        {"pid":"P1", "q":"Does Big-O change if all array values are replaced with 0 (same length n)?", "answer":"No"},
        {"pid":"P2", "q":"Big-O depends mainly on: (A) values in input (B) size n (C) CPU speed", "answer":"B"}
    ],
    "M2": [
        {"pid":"P3", "q":"Simplify the Big-O of 3n + 10.", "answer":"O(n)"},
        {"pid":"P4", "q":"Is O(2n) the same Big-O class as O(n)? (Yes/No)", "answer":"Yes"}
    ],
    "M3": [
        {"pid":"P5", "q":"How many times can you halve 64 until you reach 1?", "answer":"6"},
        {"pid":"P6", "q":"What is the complexity of: i=n; while i>1: i=i/2 ?", "answer":"O(log n)"}
    ],
    "M4": [
        {"pid":"P7", "q":"Worst-case time complexity of linear search on n items?", "answer":"O(n)"},
        {"pid":"P8", "q":"Best-case time complexity of linear search on n items?", "answer":"O(1)"}
    ],
    "CORRECT": [
        {"pid":"P9", "q":"For a single loop over n items, the complexity is:", "answer":"O(n)"}
    ],
    "NEEDS_MORE_INPUT": [
        {"pid":"P10", "q":"Warm-up: For one loop over n items, which grows faster: n or n^2?", "answer":"n^2"}
    ]
}

# We initialize the session state for page navigation. If no page is set, we start at the topic selection page.
if "page" not in st.session_state:
    st.session_state.page = "topic" 
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "analysis" not in st.session_state:
    st.session_state.analysis = []
if "practice" not in st.session_state:
    st.session_state.practice = {}
if "practice_answers" not in st.session_state:
    st.session_state.practice_answers = {}
if "events" not in st.session_state:
    st.session_state.events = []
def go(page):
    st.session_state.page = page
#Mock AI classification function as we dont have Azure OpenAI access yet.
def mock_classify_misconception(question, student_answer, misconceptions):
    a = (student_answer or"").lower()
    q = (question or "").lower()

    if any(w in a for w in ["value", "number", "digits"]):
        mid = "M1"
        reason = "You are focusing on the values inside the input rather than the input size n."
    elif any(w in a for w in ["2n", "double", "twice", "constant"]):
        mid = "M2"
        reason = "You are treating constant factors as important, but Big-O ignores constants"
    elif "halve" in q or "/2" in a or "log" in a:
        if "log" not in a:
            mid = "M3"
            reason = "Repeated halving leads to logarithmic growth, not linear."
        else:
            mid = "CORRECT"
            reason= "Your reasoning matches logarithmic intuition."
    elif "best" in a or "average" in a:
        mid = "M4"
        reason = "You are mixing best or average case with worst-case analysis."
    else:
        mid = "CORRECT"
        reason = "Your answer seems correct."
    name_map ={m["id"]: m["name"] for m in misconceptions}
    return{
        "misconception_id": mid,
        "misconception_name": name_map.get(mid, "Correct"),
        "confidence": 0.85 if mid== "CORRECT" else 0.75,
        "reason": reason
    }
def grade_answer(user_ans: str, expected: str):
    ua =(user_ans or"").strip().lower()
    exp = (expected or"").strip().lower()

    ua = ua.replace(" ","")
    exp = exp.replace(" ","")
    if not ua:
        return "No Answer", "No answer provided."
    if ua == exp:
        return "Correct", "Nice work! That matches the expected answer."
    equivalents ={
        "o(logn)": ["ologn", "o(logn)", "logn"],
        "o(n)": ["on", "o(n)", "n", "linear"],
        "o(1)": ["o(1)", "o1", "constant"],
    }
    for canonical, alts in equivalents.items():
        if exp in alts and ua in alts:
            return "Correct", "Nice work! That is equivalent form."
    if exp.startswith("O(") and "O(" in ua:
        return "Almost", f"Close, but expected {expected}."
    return "Incorrect", f"The expected answer is {expected}."
        

# Topic selection page
if st.session_state.page == "topic":
    st.title("Personalized Study Coach")
    st.subheader("Choose a topic to study:")
    st.write("This MVP focuses on diagnosing misconceptions in a small set of CS concepts.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(content.get("topic","Start"), key="btn_start"):
            st.session_state.answers = {}
            st.session_state.analysis = []
            st.session_state.practice = {}
            go("diagnostic")
    with col2:
        if st.button("Tutor Dashboard", key="btn_tutor_dashboard"):
            go("tutor")

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
    for q in content.get("diagnostic", []):
        qid = q["id"]
        ans = st.session_state.answers.get(qid, "")
        st.write(f"**{qid}**: {ans if ans.strip() else '-'}")
    
    st.divider()

    if st.button("Analyze with AI", key="btn_analyze"):
        misconceptions = content.get("misconceptions", FALLBACK_MISCONCEPTIONS)
        analysis =[]

        bad_inputs = {"", "idk", "i dont know", "i don't know", "dont know", "no idea", "not sure", "?", "??", "???"}
        
        for q in content.get("diagnostic", []):
            qid = q["id"]
            ans = st.session_state.answers.get(qid, "").strip()
            ans_low = ans.lower().strip()

            if ans_low in bad_inputs:
                analysis.append({
                    "qid": qid,
                    "misconception_id": "NEEDS_MORE_INPUT",
                    "misconception_name": "Needs more input",
                    "confidence": 0.0,
                    "reason": "Please write a short attempt so we can diagnose the misconception."
                })
                st.session_state.events.append({
                    "type": "diagnostic_analyzed",
                    "qid": qid,
                    "misconception_id": "NEEDS_MORE_INPUT",
                })
                continue
            result = mock_classify_misconception(q["question"], ans, misconceptions)
            analysis.append({"qid": qid, **result})
            st.session_state.events.append({
                "type": "diagnostic_analyzed",
                "qid": qid,
                "misconception_id": result["misconception_id"],
            })
        st.session_state.analysis = analysis
        st.session_state.practice = {}

    if st.session_state.analysis:
        st.subheader("Misconception Analysis:")
        for r in st.session_state.analysis:
            st.write(f"**{r['qid']}**: ´{r['misconception_id']}´")
            st.write(f"Misconception Name: {r['misconception_name']}")
            st.write(f"Confidence: {r['confidence']*100:.1f}%")
            st.caption(f"Reasoning: {r['reason']}")
        st.divider()
        st.subheader("Personalized Coaching Tips:")
        for r in st.session_state.analysis:
            mid = r["misconception_id"]
            help_item = HELP_PACK.get(mid, HELP_PACK["CORRECT"])
            st.write(f"### Coaching for {r['qid']} ({mid})")
            st.write(help_item["explanation"])

            with st.expander("Show hints"):
                for i, h in enumerate(help_item["hints"], start =1):
                    st.write(f"**Hint {i}:** {h}")
        st.divider()
        st.subheader("Practice Questions:")
        if st.button("Generate Practice Questions", key="btn_generate_practice"):
            st.session_state.practice = {}
            for r in st.session_state.analysis:
                qid = r["qid"]
                mid = r["misconception_id"]
                st.session_state.practice[qid] = PRACTICE_PACK.get(mid,PRACTICE_PACK["CORRECT"])
                st.session_state.events.append({
                    "type":"generated_practice",
                    "qid": qid,
                    "misconception_id": mid,
                })
        for r in st.session_state.analysis:
            qid = r["qid"]
            if qid not in st.session_state.practice:
                continue
            st.write(f"### Practice for {qid}")
            for pq in st.session_state.practice[qid]:
                pid = pq["pid"]
                prompt = pq["q"]
                expected = pq["answer"]

                user_ans = st.text_input(prompt, key=f"practice_input_{qid}_{pid}")
                if st.button(f"Check {pid}", key=f"btn_check_{qid}_{pid}"):
                    verdict, feedback = grade_answer(user_ans, expected)
                    st.session_state.events.append({
                        "type": "practice_attempt",
                        "qid": qid,
                        "pid": pid,
                        "misconception_id": r["misconception_id"],
                        "verdict": verdict,
                    })
                    if verdict.startswith("Correct"):
                        st.success(verdict)
                    elif verdict.startswith("Almost"):
                        st.warning(verdict)
                    else:
                        st.error(verdict)
                    
                    st.caption(feedback)
                
    st.info(
        "Azure OpenAI will replace this mock classifier once access is approved. " \
        "The learning pipeline remains the same."
    )
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("Back to Topics", key="btn_back_to_topics"):
            go("topic")
    with col2:
        if st.button("Tutor Dashboard", key="btn_tutor_dashboard_from_results"):
            go("tutor")

# Tutor Dashboard
elif st.session_state.page == "tutor":
    st.title("Tutor Dashboard")
    events = st.session_state.events
    if not events:
        st.info("No student activity yet.")
    else:
        total_analyzed = sum(1 for e in events if e.get("type") == "diagnostic_analyzed")
        total_practice = sum(1 for e in events if e.get("type") == "practice_attempt")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Diagnostics analyzed", total_analyzed)
        with col2:
            st.metric("Practice questions attempted", total_practice)
        
        counts ={}
        for e in events:
            mid = e.get("misconception_id")
            if mid:
                counts[mid] = counts.get(mid, 0) +1
        st.subheader("Most common misconceptions:")
        for mid, c in sorted(counts.items(), key=lambda x: x[1], reverse = True):
            st.write(f"`{mid}`: {c} events")
        st.subheader("Recent events:")
        for e in events[-15:][::-1]:
            st.write(e)
    if st.button("Back to Topics", key="btn_back_from_tutor"):
        go("topic")
