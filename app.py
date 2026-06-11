import streamlit as st
import pandas as pd
import os

# --- 1. SET UP STREAMLIT AUTO-RECOVERY TRACKER ---
# This initializes our session tracker so we can query it at line 12 before anything else renders!
if "respondent_id" not in st.session_state:
    st.session_state["respondent_id"] = ""

# --- 2. SET UP PAGE CONFIGURATION FIRST (DYNAMICAL!) ---
# If a researcher has typed an ID, it snaps the tab name to their precise participant file instantly!
tab_title = "Social Satisfaction Survey"
if st.session_state["respondent_id"].strip() != "":
    tab_title = f"ID: {st.session_state['respondent_id']}"

st.set_page_config(
    page_title=tab_title, 
    page_icon="📊",
    layout="centered"
)

# --- 3. INITIALIZE BANNER MEMORY ---
if "success_flag" not in st.session_state:
    st.session_state["success_flag"] = False

# --- 4. PATH CONFIGURATION ---
current_directory = os.path.dirname(os.path.abspath(__file__))
csv_filename = os.path.join(current_directory, "survey_responses.csv")

# --- 5. RENDER SUCCESS BANNER ---
if st.session_state["success_flag"]:
    st.success("Data consolidated and saved successfully into a single master row!")
    st.session_state["success_flag"] = False

# --- 6. MAIN TEXT DISPLAY ---
st.title("Welcome to my study!")
st.write("we will first start with some baseline data collection")

# --- 7. GLOBAL PARTICIPANT ID (Shared across both test phases) ---
# key="respondent_id" links this directly to session state. 
# As soon as you stop typing or hit Enter, the browser tab updates immediately!
respondent_id = st.text_input("Enter Participant Name/ID:", key="respondent_id").strip()

# --- LIGHTWEIGHT SUCCESS FLAG NOTE ---
def load_master_df():
    if os.path.exists(csv_filename):
        try:
            return pd.read_csv(csv_filename)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

if respondent_id:
    df_master = load_master_df()
    if not df_master.empty and respondent_id in df_master["Respondent_ID"].astype(str).values:
        st.caption(f"*Record found for '{respondent_id}'. Submissions will update this row.*")
    else:
        st.caption(f"*New row initialized for '{respondent_id}'.*")

st.write("---")

# Helper function to save or merge data row-by-row safely
def save_consolidated_data(p_id, phase_dict):
    df_master = load_master_df()
    
    # If file doesn't exist or is completely empty, initialize it with this first entry
    if df_master.empty:
        df_new = pd.DataFrame([phase_dict])
        df_new.to_csv(csv_filename, index=False)
        return

    # Check if this specific participant ID already has a row in the spreadsheet
    if p_id in df_master["Respondent_ID"].astype(str).values:
        # Get the row index of our participant
        idx = df_master[df_master["Respondent_ID"].astype(str) == p_id].index[0]
        
        # FIX: Force columns to loose object type temporarily to clear type enforcement locks
        df_master = df_master.astype(object)
        
        # Update or create the columns provided in our current submission phase
        for key, value in phase_dict.items():
            df_master.at[idx, key] = value
            
        # Clean up types before saving so numbers save as numbers
        df_master = df_master.infer_objects()
    else:
        # Participant doesn't exist yet, append a brand new row
        df_new_row = pd.DataFrame([phase_dict])
        df_master = pd.concat([df_master, df_new_row], ignore_index=True)
        
    # Write the clean unified matrix back to disk
    df_master.to_csv(csv_filename, index=False)

# ==============================================================================
# PHASE 1: INITIAL BASELINE DATA SELECTION & BUTTON
# ==============================================================================
st.subheader("section 1: Initial Baseline Tests")
st.caption("collecting baseline tests")

base_Decible = st.number_input("Baseline room decibel:")
initial_drop_test = st.number_input("Baseline drop test result (cm):")
age = st.number_input("What is your age?", value=21)

med_history = st.checkbox("Any known medical issues? (Neurological, Hepatic, etc.)")
past_mental = st.checkbox("Any history of mental health challenges? (Specifically Depression or Anxiety)")
meals_hydration = st.slider("can you describe how hydrated and fed you feel?", 0, 10, 5)
satisfaction = st.select_slider(
    "How satisfied are you with your current social status and relationships overall?",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
    value="Neutral"
)

st.caption("Rate your agreement with these social statements:")
q1 = st.slider("1. I feel connected to a meaningful community or peer group.", 0, 10, 5)
q2 = st.slider("2. I am satisfied with the current frequency of my real-life social interactions.", 0, 10, 5)
q3 = st.slider("3. I feel supported by my social circle when handling daily stress or life events.", 0, 10, 5)
q4 = st.slider("4. I have sufficient energy and motivation to sustain my close friendships.", 0, 10, 5)
q5 = st.slider("5. I feel comfortable expressing my authentic self within my regular social environments.", 0, 10, 5)

st.markdown("#### Baseline Physiological Metric Entry")
BP = st.text_input("Enter Baseline Blood Pressure (mmHg):", value="120/80")
blood_glucose = st.number_input("Enter Baseline Blood Glucose (mg/dL):")
Temp = st.number_input("Enter Baseline Oral Temp (°C):")
body_temp = st.number_input("Enter Baseline Skin Temp (°C):")
heart_rate = st.number_input("Enter Baseline Heart Rate (BPM):")

# INDEPENDENT SUBMIT BUTTON #1
submit_baseline = st.button("Log Initial Baseline Data Only")

if submit_baseline:
    if not respondent_id:
        st.error("Please provide a valid Participant ID before submitting baseline data.")
    else:
        likert_map = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
        total_score_metric = q1 + q2 + q3 + q4 + q5
        
        # Dictionary representing only the baseline metrics
        baseline_fields = {
            "Respondent_ID": respondent_id,
            "Age": age,
            "Social_Satisfaction": likert_map[satisfaction], 
            "Metric_Community_Connection": q1,
            "Metric_Interaction_Frequency": q2,
            "Metric_Support_System": q3,
            "Metric_Social_Energy": q4,
            "Metric_Authenticity_Comfort": q5,
            "Metric Sum": total_score_metric,
            "Medical_History_Flag": med_history,
            "Mental_History_Flag": past_mental,
            "Baseline_Decibel": base_Decible,
            "Initial_Drop_Test": initial_drop_test,
            "Baseline_BP": BP,
            "Baseline_Glucose": blood_glucose,
            "Baseline_Oral_Temp": Temp,
            "Baseline_Skin_Temp": body_temp,
            "Baseline_HR": heart_rate,
            "food and drink" : meals_hydration
        }
        
        save_consolidated_data(respondent_id, baseline_fields)
        st.session_state["success_flag"] = True
        st.rerun()

st.write("---")

# ==============================================================================
# PHASE 2: POST-INGESTION DATA SELECTION & BUTTON
# ==============================================================================
st.subheader("section 2: Post-Drinking Evaluation")
st.caption("metrics after alcohol ingestion")

num_of_drink = st.number_input("How many alcoholic drinks have you had?")

st.markdown("#### Enjoyment Metrics")
fun_1 = st.select_slider(
    "I am finding this activity thoroughly enjoyable and entertaining.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], value="Neutral", key="f1"
)
fun_2 = st.select_slider(
    "I am so deeply absorbed in what I am doing that I have lost track of time.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], value="Neutral", key="f2"
)
fun_3 = st.select_slider(
    "I feel bored, frustrated, or disconnected from what is happening around me.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], value="Neutral", key="f3"
)
fun_4 = st.select_slider(
    "I am doing this completely because I want to, not because I have to.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], value="Neutral", key="f4"
)

st.markdown("#### Reaction Time & Post-Ingestion Biometrics")
drop_test_1 = st.number_input("Drop Test 1 (cm):", value=0.0)
drop_test_2 = st.number_input("Drop Test 2 (cm):", value=0.0)
drop_test_3 = st.number_input("Drop Test 3 (cm):", value=0.0)
Decible_2 = st.number_input("Post-ingestion room decible:")
BP_2 = st.text_input("Enter Post-Ingestion Blood Pressure (mmHg):", value="120/80")
blood_glucose_2 = st.number_input("Enter Post-Ingestion Blood Glucose")
Temp_2 = st.number_input("Enter Post-Ingestion Oral Temp (°C):")
body_temp_2 = st.number_input("Enter Post-Ingestion Skin Temp (°C):")
heart_rate_2 = st.number_input("Enter Post-Ingestion Heart Rate (BPM):")
alc_percent = st.number_input("Enter Post-Ingestion alcohol % :")

# INDEPENDENT SUBMIT BUTTON #2
submit_post = st.button("Log Post-Drinking Data Only")

if submit_post:
    if not respondent_id:
        st.error("Please provide a valid Participant ID ")
    else:
        likert_map = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
        
        # Dictionary representing only the post-drinking metrics
        post_fields = {
            "Respondent_ID": respondent_id,
            "Num_of_Drinks": num_of_drink,
            "Post_Decibel": Decible_2,
            # FIXED: Changed backslash (\) to forward slash (/) for mathematical division tracking
            "Drop_Test_avrage": (drop_test_1 + drop_test_2 + drop_test_3) / 3,
            "Post_BP": BP_2,
            "Post_Glucose": blood_glucose_2,
            "Post_Oral_Temp": Temp_2,
            "Post_Skin_Temp": body_temp_2,
            "Post_HR": heart_rate_2,
            "Enjoyment_total": likert_map[fun_1] + likert_map[fun_2]+likert_map[fun_3]-likert_map[fun_4],
            "alcohol percentage": alc_percent
        }
        
        save_consolidated_data(respondent_id, post_fields)
        st.session_state["success_flag"] = True
        st.rerun()

# --- 8. ADMIN CONSOLE DATA VIEW ---
df_display = load_master_df()
if not df_display.empty:
    st.write("---")
    with st.expander("View Collected Data"):
        st.dataframe(df_display)
