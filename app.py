import streamlit as st
import pandas as pd
import os

# --- 1. SET UP PAGE CONFIGURATION FIRST ---
st.set_page_config(page_title="Social Satisfaction Survey", page_icon="📝", layout="centered")

# --- 2. INITIALIZE BANNER MEMORY ---
if "success_flag" not in st.session_state:
    st.session_state["success_flag"] = False

# --- 3. PATH CONFIGURATION ---
current_directory = os.path.dirname(os.path.abspath(__file__))
csv_filename = os.path.join(current_directory, "survey_responses.csv")

# --- 4. RENDER SUCCESS BANNER ---
if st.session_state["success_flag"]:
    st.success("🎉 Responses successfully compiled and saved! The form has been reset for the next participant.")
    st.session_state["success_flag"] = False

# --- 5. MAIN TEXT DISPLAY ---
st.title("Social Satisfaction & Security Survey")
st.write("Please take a moment to fill out this brief questionnaire.")

# --- 6. THE TRIGGER CHECKBOX (Placed OUTSIDE the form so it works perfectly!) ---
wants_physicle_test = st.checkbox("Would you be open to doing a physical test with this study?")
st.write("---")

# --- 7. THE SURVEY FORM CONTAINER ---
survey_form = st.form(key="clinical_survey_form", clear_on_submit=True)

# FIXED: All elements below now use 'survey_form.' instead of 'st.'
survey_form.subheader("Metrics")
base_Decible = survey_form.number_input("Baseline room decible:")
initial_drop_test = survey_form.number_input("Baseline drop test result (cm):")
respondent_id = survey_form.text_input("Enter Participant Name")
age = survey_form.number_input("What is your age?", min_value=1, max_value=120)
num_of_drink = survey_form.number_input("How many alcoholic drinks have you had?", min_value=0, value=0)

# The form reads the state of the checkbox from above to decide whether to show these fields
if wants_physicle_test:
    survey_form.markdown("### Physiological Metric Entry")
    BP = survey_form.text_input("Enter Blood Pressure (mmHg):", value="120/80")
    blood_glucose = survey_form.number_input("Enter Blood Glucose (mg/dL):")
    Temp = survey_form.number_input("Enter Oral Temp (°C):")
    body_temp = survey_form.number_input("Enter Skin Temp (°C):")
    heart_rate = survey_form.number_input("Enter Heart Rate (BPM):")
else:
    BP = "N/A"
    blood_glucose = "N/A"
    Temp = "N/A"
    body_temp = "N/A"
    heart_rate = "N/A"

survey_form.write("---")
survey_form.subheader("Health History")  
med_history = survey_form.checkbox("Any known medical issues? (Neurological, Hepatic, etc.)")
past_mental = survey_form.checkbox("Any history of mental health challenges? (Specifically Depression or Anxiety)")

satisfaction = survey_form.select_slider(
    "How satisfied are you with your current social status and relationships overall?",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
    value="Neutral"
)

survey_form.caption("Rate your agreement with these social statements:")
q1 = survey_form.slider("1. I feel connected to a meaningful community or peer group.", 0, 10, 5)
q2 = survey_form.slider("2. I am satisfied with the current frequency of my real-life social interactions.", 0, 10, 5)
q3 = survey_form.slider("3. I feel supported by my social circle when handling daily stress or life events.", 0, 10, 5)
q4 = survey_form.slider("4. I have sufficient energy and motivation to sustain my close friendships.", 0, 10, 5)
q5 = survey_form.slider("5. I feel comfortable expressing my authentic self within my regular social environments.", 0, 10, 5)

survey_form.write("---")
survey_form.subheader("Enjoyment Metrics")

fun_1 = survey_form.select_slider(
    "I am finding this activity thoroughly enjoyable and entertaining.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
    value="Neutral"
)
fun_2 = survey_form.select_slider(
    "I am so deeply absorbed in what I am doing that I have lost track of time.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
    value="Neutral"
)
fun_3 = survey_form.select_slider(
    "I feel bored, frustrated, or disconnected from what is happening around me.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
    value="Neutral"
)
fun_4 = survey_form.select_slider(
    "I am doing this completely because I want to, not because I have to.",
    options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
    value="Neutral"
)

survey_form.write("---")
survey_form.subheader("Reaction Time Post-ingestion")
drop_test_1 = survey_form.number_input("Drop Test 1 (cm):")
drop_test_2 = survey_form.number_input("Drop Test 2 (cm):")
drop_test_3 = survey_form.number_input("Drop Test 3 (cm):")
Decible_2 = survey_form.number_input("Post-ingestion room decible:")

# This submit button binds the entire survey_form object together beautifully
submit_button = survey_form.form_submit_button(label="Submit Survey Responses")
  
# --- 8. HANDLING FORM SUBMISSION ---
if submit_button:
    if not respondent_id.strip():
        st.error("Please provide a valid Participant ID before submitting.")
    else:
        likert_map = {
            "Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5
        }
        reverse_likert_map = { 
            "Strongly Disagree": 5, "Disagree": 4, "Neutral": 3, "Agree": 2, "Strongly Agree": 1
        }
        
        total_score_metric = q1 + q2 + q3 + q4 + q5
        total_fun = likert_map[fun_1] + likert_map[fun_2] + reverse_likert_map[fun_3] + likert_map[fun_4]
        drop_test_avg_after_alcohol = (drop_test_1 + drop_test_2 + drop_test_3) / 3
        
        new_data = {
            "Respondent_ID": [respondent_id],
            "Age": [age],
            "Social_Satisfaction": [likert_map[satisfaction]], 
            "Future_phisicle": [wants_physicle_test],
            "Metric_Community_Connection": [q1],
            "Metric_Interaction_Frequency": [q2],
            "Metric_Support_System": [q3],
            "Metric_Social_Energy": [q4],
            "Metric_Authenticity_Comfort": [q5],
            "Metric Sum": [total_score_metric],
            "Enjoiment": [likert_map[fun_1]], 
            "Emersiveness": [likert_map[fun_2]], 
            "Bordem": [reverse_likert_map[fun_3]], 
            "autonomy": [likert_map[fun_4]], 
            "Total Fun": [total_fun],
            "Drop test under alcohol": [drop_test_avg_after_alcohol],
            "initial drop test": [initial_drop_test],
            "BP": [BP],
            "Blood glu": [blood_glucose],
            "oral temp": [Temp],
            "skin temp": [body_temp],
            "HR": [heart_rate],
            "num of drink": [num_of_drink],
            "Medical_History_Flag": [med_history],
            "Mental_History_Flag": [past_mental],
            "Decible_diference": [Decible_2 - base_Decible],
        }
          
        df_new = pd.DataFrame(new_data)
          
        if not os.path.exists(csv_filename):
            df_new.to_csv(csv_filename, index=False)
        else:
            df_new.to_csv(csv_filename, mode='a', header=False, index=False)
        
        st.session_state["success_flag"] = True
        st.rerun()
        
# --- 9. ADMIN CONSOLE DATA VIEW ---
if os.path.exists(csv_filename):
    st.write("---")
    with st.expander("View Collected Data (Admin Only)"):
        df_current = pd.read_csv(csv_filename)
        st.dataframe(df_current)
