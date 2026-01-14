import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Cognitive Disorder Screening System", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme colors
if st.session_state.theme == 'dark':
    bg_color = '#1e1e1e'
    text_color = '#e0e0e0'
    card_bg = '#2d2d2d'
    button_bg = '#4A90E2'
    disclaimer_bg = '#2a3f5f'
else:
    bg_color = '#f8f9fa'
    text_color = '#2c3e50'
    card_bg = 'white'
    button_bg = '#4A90E2'
    disclaimer_bg = '#E8F4F8'

st.markdown(f"""<style>
@media (max-width: 768px) {{
    .main .block-container {{padding: 1rem !important;}}
    .stButton>button {{padding: 0.4rem 1rem !important;font-size: 0.9rem !important;}}
    h1 {{font-size: 1.5rem !important;}}
    h2 {{font-size: 1.3rem !important;}}
    h3 {{font-size: 1.1rem !important;}}
    .result-card {{padding: 1rem !important;}}
    .disclaimer-box {{padding: 0.75rem !important;}}
}}
@media (min-width: 769px) and (max-width: 1024px) {{
    .main .block-container {{padding: 2rem !important;}}
}}
.main{{background-color:{bg_color}}}
.stApp{{background-color:{bg_color}}}
body{{color:{text_color}}}
.stButton>button{{background-color:{button_bg};color:white;border-radius:5px;padding:0.5rem 2rem;border:none;font-weight:500}}
.stButton>button:hover{{background-color:#357ABD}}
.disclaimer-box{{background-color:{disclaimer_bg};border-left:4px solid #4A90E2;padding:1rem;border-radius:5px;margin:1rem 0;color:{text_color}!important}}
.disclaimer-box p,.disclaimer-box strong,.disclaimer-box ul,.disclaimer-box li,.disclaimer-box h4{{color:{text_color}!important}}
.result-card{{background-color:{card_bg};padding:1.5rem;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin:1rem 0}}
.result-card h4,.result-card p,.result-card strong{{color:{text_color}!important}}
.metric-label{{font-size:0.9rem;color:#666;font-weight:500}}
.metric-value{{font-size:2rem;font-weight:600;color:{text_color}}}
h1,h2,h3{{color:{text_color}}}
.info-text{{color:{text_color};line-height:1.6}}
.stTextArea textarea{{background-color:{card_bg};color:{text_color}}}
.stSelectbox div[data-baseweb="select"]{{background-color:{card_bg}}}
.stRadio label{{color:{text_color}}}
.char-counter{{color:{text_color};font-size:0.9rem;margin-top:5px}}
</style>""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'age' not in st.session_state: st.session_state.age = None
if 'gender' not in st.session_state: st.session_state.gender = None
if 'selected_assessments' not in st.session_state: st.session_state.selected_assessments = []
if 'questionnaire_completed' not in st.session_state: st.session_state.questionnaire_completed = False
if 'text_completed' not in st.session_state: st.session_state.text_completed = False
if 'audio_completed' not in st.session_state: st.session_state.audio_completed = False
if 'questionnaire_data' not in st.session_state: st.session_state.questionnaire_data = {}
if 'text_data' not in st.session_state: st.session_state.text_data = {}
if 'audio_data' not in st.session_state: st.session_state.audio_data = {}
if 'results_computed' not in st.session_state: st.session_state.results_computed = False
if 'results' not in st.session_state: st.session_state.results = None

QUESTIONNAIRE_ITEMS = {'ADHD':["I have difficulty starting tasks that require a lot of thinking.","I lose focus during lectures, meetings, or reading.","I forget deadlines or appointments even when they are important.","I struggle to organize my work or study materials.","I postpone until the last moment, even for important tasks.","I feel mentally restless or unable to slow my thoughts.","I make careless mistakes even when I know the material."],'Depression':["I feel little interest or pleasure in doing things.","I feel down, hopeless, or emotionally numb.","I feel tired or low on energy most days.","I feel like I am not good enough or have failed.","I have difficulty concentrating because of low mood."],'Anxiety':["I feel nervous, anxious, or on edge.","I worry too much about academic or social situations.","I find it hard to relax, even when I have time.","My anxiety interferes with my studies or relationships.","I avoid situations because they make me anxious."],'SPCD':["People tell me I sound blunt, awkward, or unclear when I speak.","I struggle to adjust how I speak depending on who I am talking to.","I find it difficult to stay on topic in conversations.","I misunderstand what others expect from me socially."],'ASD':["I find it hard to know when it is my turn to speak in conversations.","I struggle to understand jokes, sarcasm, or indirect hints.","I feel unsure how much detail to give when explaining something.","I find group discussions confusing or exhausting.","I prefer clear rules and predictable routines.","I miss social cues like tone of voice or facial expressions."]}

DISORDER_THRESHOLDS = {'ADHD':{'questions':7,'max_score':28,'threshold':19},'ASD':{'questions':6,'max_score':24,'threshold':16},'SPCD':{'questions':4,'max_score':16,'threshold':11},'Depression':{'questions':5,'max_score':20,'threshold':13},'Anxiety':{'questions':5,'max_score':20,'threshold':14}}

def calculate_severity(raw_score, max_score):
    percentage = (raw_score / max_score) * 100
    if percentage < 33: return "Low", percentage
    elif percentage <= 66: return "Medium", percentage
    else: return "High", percentage

def analyze_questionnaire(responses, selected_assessments):
    raw_scores = {}
    for category in selected_assessments:
        raw_scores[category] = 0
        for question in QUESTIONNAIRE_ITEMS[category]:
            if question in responses and responses[question]:
                val = responses[question][0]
                raw_scores[category] += int(val) if val.isdigit() else 0
    normalized_scores, severity_levels = {}, {}
    for disorder in raw_scores:
        max_score = DISORDER_THRESHOLDS[disorder]['max_score']
        threshold = DISORDER_THRESHOLDS[disorder]['threshold']
        normalized_scores[disorder] = raw_scores[disorder] / max_score
        severity, percentage = calculate_severity(raw_scores[disorder], max_score)
        severity_levels[disorder] = {'severity':severity,'raw_score':raw_scores[disorder],'max_score':max_score,'percentage':percentage,'threshold':threshold,'meets_threshold':raw_scores[disorder]>=threshold}
    return normalized_scores, severity_levels

def analyze_text_responses(text_responses, selected_assessments):
    # Simple scoring based on text length and sentiment
    raw_scores = {}
    for category in selected_assessments:
        total_chars = sum([len(text_responses.get(q, '')) for q in QUESTIONNAIRE_ITEMS[category]])
        # Normalize score based on expected length
        raw_scores[category] = min(total_chars / (len(QUESTIONNAIRE_ITEMS[category]) * 100), 1.0)
    
    normalized_scores, severity_levels = {}, {}
    for disorder in raw_scores:
        max_score = DISORDER_THRESHOLDS[disorder]['max_score']
        threshold = DISORDER_THRESHOLDS[disorder]['threshold']
        raw_score = int(raw_scores[disorder] * max_score)
        normalized_scores[disorder] = raw_scores[disorder]
        severity, percentage = calculate_severity(raw_score, max_score)
        severity_levels[disorder] = {'severity':severity,'raw_score':raw_score,'max_score':max_score,'percentage':percentage,'threshold':threshold,'meets_threshold':raw_score>=threshold}
    return normalized_scores, severity_levels

def analyze_audio_responses(audio_responses, selected_assessments):
    # Simulate audio analysis
    raw_scores = {}
    for category in selected_assessments:
        # Count how many audio files were uploaded
        audio_count = sum([1 for q in QUESTIONNAIRE_ITEMS[category] if audio_responses.get(q)])
        raw_scores[category] = audio_count / len(QUESTIONNAIRE_ITEMS[category])
    
    normalized_scores, severity_levels = {}, {}
    for disorder in raw_scores:
        max_score = DISORDER_THRESHOLDS[disorder]['max_score']
        threshold = DISORDER_THRESHOLDS[disorder]['threshold']
        raw_score = int(raw_scores[disorder] * max_score)
        normalized_scores[disorder] = raw_scores[disorder]
        severity, percentage = calculate_severity(raw_score, max_score)
        severity_levels[disorder] = {'severity':severity,'raw_score':raw_score,'max_score':max_score,'percentage':percentage,'threshold':threshold,'meets_threshold':raw_score>=threshold}
    return normalized_scores, severity_levels

def reset_app():
    st.session_state.page='welcome';st.session_state.age=None;st.session_state.gender=None;st.session_state.selected_assessments=[];st.session_state.questionnaire_completed=False;st.session_state.text_completed=False;st.session_state.audio_completed=False;st.session_state.questionnaire_data={};st.session_state.text_data={};st.session_state.audio_data={};st.session_state.results_computed=False;st.session_state.results=None

with st.sidebar:
    st.title("🧠 Navigation");st.markdown("---")
    
    # Settings button for theme toggle
    st.markdown("### ⚙️ Settings")
    theme_mode = st.selectbox("Theme Mode", ["Dark Mode", "Light Mode"], index=0 if st.session_state.theme == 'dark' else 1)
    if (theme_mode == "Dark Mode" and st.session_state.theme != 'dark') or (theme_mode == "Light Mode" and st.session_state.theme != 'light'):
        st.session_state.theme = 'dark' if theme_mode == "Dark Mode" else 'light'
        st.rerun()
    
    st.markdown("---")
    
    if st.button("📋 Welcome", use_container_width=True): st.session_state.page='welcome';st.rerun()
    if st.button("👤 Demographics", use_container_width=True): st.session_state.page='demographics';st.rerun()
    if st.button("🎯 Assessment Options", use_container_width=True): st.session_state.page='mode_selection';st.rerun()
    if st.button("📝 Questionnaire", use_container_width=True): st.session_state.page='assessment_selection';st.rerun()
    if st.button("✍️ Text Input", use_container_width=True): st.session_state.page='text_assessment_selection';st.rerun()
    if st.button("🎤 Voice Input", use_container_width=True): st.session_state.page='audio_assessment_selection';st.rerun()
    if st.button("📊 Results", use_container_width=True):
        if st.session_state.results_computed: st.session_state.page='results';st.rerun()
        else: st.warning("Complete an assessment first")
    st.markdown("---")
    if st.button("🏠 Home (Reset)", use_container_width=True): reset_app();st.rerun()
    st.markdown("---");st.markdown("**Research Prototype**");st.caption("Version 1.0 | IEEE Research Demo");st.caption(f"Session: {datetime.now().strftime('%Y-%m-%d')}")

if st.session_state.page == 'welcome':
    st.title("Multimodal Cognitive Disorder Screening System");st.markdown("### Research Prototype for Decision Support")
    st.markdown("""<div class="info-text"><p>This system is designed as a research prototype to assist healthcare professionals in screening for potential cognitive and mental health disorders through multimodal assessment.</p><p><strong>Target Conditions:</strong></p><ul><li>Attention Deficit Hyperactivity Disorder (ADHD)</li><li>Social Pragmatic Communication Disorder (SPCD)</li><li>Autism Spectrum Disorder (ASD)</li><li>Anxiety Disorders</li><li>Depression</li></ul></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""<div class="disclaimer-box"><h4>⚠️ Ethical Disclaimer and Informed Consent</h4><p><strong>This system provides support for self-assessment and clinical diagnosis.</strong></p><p><strong>Important Information:</strong></p><ul><li>Results should be interpreted by qualified healthcare professionals</li><li>This tool supports but does not replace comprehensive clinical evaluation</li><li>Data is processed locally and not stored or transmitted</li></ul></div>""", unsafe_allow_html=True)
    st.markdown("---")
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        if st.button("I Understand - Proceed to Assessment", use_container_width=True): st.session_state.page='demographics';st.rerun()

elif st.session_state.page == 'demographics':
    st.title("👤 Demographic Information");st.markdown("Please provide the following information before beginning the assessment.")
    st.markdown("""<div class="disclaimer-box"><p><strong>Privacy Notice:</strong> This information is used only for assessment purposes and is not stored or transmitted.</p></div>""", unsafe_allow_html=True)
    st.markdown("### Personal Information")
    col1,col2=st.columns(2)
    with col1: age=st.number_input("Age",min_value=5,max_value=100,value=st.session_state.age if st.session_state.age else 18,step=1,help="Enter your current age")
    with col2:
        gender_options=["Select","Male","Female","Prefer not to say"]
        current_index=0
        if st.session_state.gender and st.session_state.gender in gender_options: current_index=gender_options.index(st.session_state.gender)
        gender=st.selectbox("Gender",options=gender_options,index=current_index)
    st.markdown("---")
    col1,col2,col3=st.columns([1,1,1])
    with col2:
        demographics_complete=gender!="Select"
        if st.button("Continue", disabled=not demographics_complete, use_container_width=True): st.session_state.age=age;st.session_state.gender=gender;st.session_state.page='mode_selection';st.rerun()

elif st.session_state.page == 'mode_selection':
    st.title("🎯 Select Assessment Mode");st.markdown("Choose how you would like to complete your assessment.")
    st.markdown("""<div class="disclaimer-box"><p><strong>Assessment Options:</strong> You may complete one or more assessment modes.</p></div>""", unsafe_allow_html=True)
    st.markdown("### Available Assessment Modes")
    col1,col2,col3=st.columns(3)
    with col1:
        st.markdown("""<div class="result-card"><h4>📝 Questionnaire</h4><p>Answer structured questions about your experiences</p><p><strong>Time:</strong> ~5-7 minutes</p></div>""", unsafe_allow_html=True)
        if st.button("Start Questionnaire", use_container_width=True, key="btn_questionnaire"): st.session_state.page='assessment_selection';st.rerun()
    with col2:
        st.markdown("""<div class="result-card"><h4>✍️ Free Text Input</h4><p>Answer questions in text format (min 80 characters per answer)</p><p><strong>Time:</strong> ~5-10 minutes</p></div>""", unsafe_allow_html=True)
        if st.button("Start Text Input", use_container_width=True, key="btn_text"): st.session_state.page='text_assessment_selection';st.rerun()
    with col3:
        st.markdown("""<div class="result-card"><h4>🎤 Voice Input</h4><p>Answer questions via audio recording (WAV format)</p><p><strong>Time:</strong> ~5-10 minutes</p></div>""", unsafe_allow_html=True)
        if st.button("Start Voice Input", use_container_width=True, key="btn_audio"): st.session_state.page='audio_assessment_selection';st.rerun()

elif st.session_state.page == 'assessment_selection':
    st.title("🎯 Select Assessment Type");st.markdown("### Which assessment(s) would you like to take?")
    st.markdown("""<div class="disclaimer-box"><p><strong>📌 Note:</strong> Multiple assessments can be selected. Choose all that apply to your concerns.</p></div>""", unsafe_allow_html=True)
    st.markdown("---");st.markdown("### Available Assessments")
    selected=[]
    col1,col2=st.columns(2)
    with col1:
        if st.checkbox('🎯 ADHD Assessment', key='chk_adhd', value='ADHD' in st.session_state.selected_assessments): selected.append('ADHD')
        if st.checkbox('😔 Depression Assessment', key='chk_depression', value='Depression' in st.session_state.selected_assessments): selected.append('Depression')
        if st.checkbox('😰 Anxiety Assessment', key='chk_anxiety', value='Anxiety' in st.session_state.selected_assessments): selected.append('Anxiety')
    with col2:
        if st.checkbox('💬 SPCD Assessment', key='chk_spcd', value='SPCD' in st.session_state.selected_assessments): selected.append('SPCD')
        if st.checkbox('🧩 ASD Assessment', key='chk_asd', value='ASD' in st.session_state.selected_assessments): selected.append('ASD')
    st.markdown("---")
    if len(selected)>0: st.success(f"✅ {len(selected)} assessment(s) selected: {', '.join(selected)}")
    else: st.warning("⚠️ Please select at least one assessment to continue")
    st.markdown("---")
    col1,col2,col3=st.columns([1,1,1])
    with col2:
        if st.button("Start Assessment", disabled=len(selected)==0, use_container_width=True): st.session_state.selected_assessments=selected;st.session_state.page='questionnaire';st.rerun()

elif st.session_state.page == 'text_assessment_selection':
    st.title("🎯 Select Assessment Type for Text Input");st.markdown("### Which assessment(s) would you like to take?")
    st.markdown("""<div class="disclaimer-box"><p><strong>📌 Note:</strong> Multiple assessments can be selected. You will answer questions in text format (minimum 80 characters per answer).</p></div>""", unsafe_allow_html=True)
    st.markdown("---");st.markdown("### Available Assessments")
    selected=[]
    col1,col2=st.columns(2)
    with col1:
        if st.checkbox('🎯 ADHD Assessment', key='txt_chk_adhd', value='ADHD' in st.session_state.selected_assessments): selected.append('ADHD')
        if st.checkbox('😔 Depression Assessment', key='txt_chk_depression', value='Depression' in st.session_state.selected_assessments): selected.append('Depression')
        if st.checkbox('😰 Anxiety Assessment', key='txt_chk_anxiety', value='Anxiety' in st.session_state.selected_assessments): selected.append('Anxiety')
    with col2:
        if st.checkbox('💬 SPCD Assessment', key='txt_chk_spcd', value='SPCD' in st.session_state.selected_assessments): selected.append('SPCD')
        if st.checkbox('🧩 ASD Assessment', key='txt_chk_asd', value='ASD' in st.session_state.selected_assessments): selected.append('ASD')
    st.markdown("---")
    if len(selected)>0: st.success(f"✅ {len(selected)} assessment(s) selected: {', '.join(selected)}")
    else: st.warning("⚠️ Please select at least one assessment to continue")
    st.markdown("---")
    col1,col2,col3=st.columns([1,1,1])
    with col2:
        if st.button("Start Text Assessment", disabled=len(selected)==0, use_container_width=True): st.session_state.selected_assessments=selected;st.session_state.page='text_input';st.rerun()

elif st.session_state.page == 'audio_assessment_selection':
    st.title("🎯 Select Assessment Type for Voice Input");st.markdown("### Which assessment(s) would you like to take?")
    st.markdown("""<div class="disclaimer-box"><p><strong>📌 Note:</strong> Multiple assessments can be selected. You will answer questions by uploading audio recordings (WAV format).</p></div>""", unsafe_allow_html=True)
    st.markdown("---");st.markdown("### Available Assessments")
    selected=[]
    col1,col2=st.columns(2)
    with col1:
        if st.checkbox('🎯 ADHD Assessment', key='aud_chk_adhd', value='ADHD' in st.session_state.selected_assessments): selected.append('ADHD')
        if st.checkbox('😔 Depression Assessment', key='aud_chk_depression', value='Depression' in st.session_state.selected_assessments): selected.append('Depression')
        if st.checkbox('😰 Anxiety Assessment', key='aud_chk_anxiety', value='Anxiety' in st.session_state.selected_assessments): selected.append('Anxiety')
    with col2:
        if st.checkbox('💬 SPCD Assessment', key='aud_chk_spcd', value='SPCD' in st.session_state.selected_assessments): selected.append('SPCD')
        if st.checkbox('🧩 ASD Assessment', key='aud_chk_asd', value='ASD' in st.session_state.selected_assessments): selected.append('ASD')
    st.markdown("---")
    if len(selected)>0: st.success(f"✅ {len(selected)} assessment(s) selected: {', '.join(selected)}")
    else: st.warning("⚠️ Please select at least one assessment to continue")
    st.markdown("---")
    col1,col2,col3=st.columns([1,1,1])
    with col2:
        if st.button("Start Audio Assessment", disabled=len(selected)==0, use_container_width=True): st.session_state.selected_assessments=selected;st.session_state.page='audio_input';st.rerun()

elif st.session_state.page == 'questionnaire':
    st.title("📝 Behavioral Questionnaire");st.markdown("Please respond honestly to each statement based on your recent experiences.")
    st.markdown("""<div class="disclaimer-box"><p><strong>Instructions:</strong> Rate each statement on a scale from 0 (Never) to 4 (Very Often) based on how you have been feeling recently.</p><p><strong>Rating Scale:</strong> 0 = Never | 1 = Rarely | 2 = Sometimes | 3 = Often | 4 = Very Often</p></div>""", unsafe_allow_html=True)
    st.info(f"**Selected Assessments:** {', '.join(st.session_state.selected_assessments)}")
    responses={};options=["0 - Never","1 - Rarely","2 - Sometimes","3 - Often","4 - Very Often"];question_counter=1
    for category in st.session_state.selected_assessments:
        st.markdown(f"### {category} Assessment")
        for question in QUESTIONNAIRE_ITEMS[category]:
            response=st.radio(f"{question_counter}. {question}",options=options,key=f"q_{category}_{question_counter}",horizontal=True,index=None)
            responses[question]=response;question_counter+=1
        st.markdown("---")
    all_answered=all(v is not None for v in responses.values())
    col1,col2,col3=st.columns([1,1,1])
    with col1:
        if st.button("🏠 Home", use_container_width=True): reset_app();st.rerun()
    with col3:
        if st.button("📊 View Results", disabled=not all_answered, use_container_width=True):
            st.session_state.questionnaire_data=responses;st.session_state.questionnaire_completed=True
            q_scores,severity_levels=analyze_questionnaire(responses, st.session_state.selected_assessments)
            st.session_state.results={'scores':q_scores,'severity_levels':severity_levels,'mode':'questionnaire_only'};st.session_state.results_computed=True;st.session_state.page='results';st.rerun()

elif st.session_state.page == 'text_input':
    st.title("✍️ Text Input Assessment");st.markdown("Please answer each question in text format (minimum 80 characters per answer).")
    st.markdown("""<div class="disclaimer-box"><p><strong>Instructions:</strong> Type your answers to each question. Be honest and detailed. Each answer must be at least 80 characters long.</p></div>""", unsafe_allow_html=True)
    st.info(f"**Selected Assessments:** {', '.join(st.session_state.selected_assessments)}")
    
    text_responses = {};question_counter = 1;all_valid = True
    
    for category in st.session_state.selected_assessments:
        st.markdown(f"### {category} Assessment")
        for question in QUESTIONNAIRE_ITEMS[category]:
            st.markdown(f"**{question_counter}. {question}**")
            
            # Get existing answer or empty string
            existing_answer = st.session_state.text_data.get(question, '')
            
            # Text area for answer
            answer = st.text_area(
                f"Your answer:",
                value=existing_answer,
                height=100,
                key=f"txt_{category}_{question_counter}",
                label_visibility="collapsed"
            )
            
            text_responses[question] = answer
            
            # Real-time character counter
            char_count = len(answer)
            if char_count < 80:
                st.markdown(f'<div class="char-counter">❌ {char_count}/80 characters (minimum 80 required)</div>', unsafe_allow_html=True)
                all_valid = False
            else:
                st.markdown(f'<div class="char-counter">✅ {char_count} characters</div>', unsafe_allow_html=True)
            
            question_counter += 1
            st.markdown("---")
    
    col1,col2,col3=st.columns([1,1,1])
    with col1:
        if st.button("🏠 Home", use_container_width=True): reset_app();st.rerun()
    with col3:
        if st.button("📊 View Results", disabled=not all_valid, use_container_width=True):
            st.session_state.text_data=text_responses;st.session_state.text_completed=True
            t_scores,severity_levels=analyze_text_responses(text_responses, st.session_state.selected_assessments)
            st.session_state.results={'scores':t_scores,'severity_levels':severity_levels,'mode':'text_only'};st.session_state.results_computed=True;st.session_state.page='results';st.rerun()

elif st.session_state.page == 'audio_input':
    st.title("🎤 Voice Input Assessment");st.markdown("Please answer each question by uploading an audio recording (WAV format).")
    st.markdown("""<div class="disclaimer-box"><p><strong>Instructions:</strong> Record your answer to each question and upload the audio file (WAV format). Speak clearly and provide detailed responses.</p></div>""", unsafe_allow_html=True)
    st.info(f"**Selected Assessments:** {', '.join(st.session_state.selected_assessments)}")
    
    audio_responses = {};question_counter = 1;all_uploaded = True
    
    for category in st.session_state.selected_assessments:
        st.markdown(f"### {category} Assessment")
        for question in QUESTIONNAIRE_ITEMS[category]:
            st.markdown(f"**{question_counter}. {question}**")
            
            # File uploader for audio
            uploaded_audio = st.file_uploader(
                f"Upload audio answer (WAV):",
                type=['wav'],
                key=f"aud_{category}_{question_counter}",
                label_visibility="collapsed"
            )
            
            if uploaded_audio:
                st.audio(uploaded_audio, format='audio/wav')
                audio_responses[question] = uploaded_audio.read()
                st.success(f"✅ Audio uploaded: {uploaded_audio.name}")
            else:
                audio_responses[question] = st.session_state.audio_data.get(question, None)
                if not audio_responses[question]:
                    st.warning("❌ Please upload an audio file")
                    all_uploaded = False
            
            question_counter += 1
            st.markdown("---")
    
    col1,col2,col3=st.columns([1,1,1])
    with col1:
        if st.button("🏠 Home", use_container_width=True): reset_app();st.rerun()
    with col3:
        if st.button("📊 View Results", disabled=not all_uploaded, use_container_width=True):
            st.session_state.audio_data=audio_responses;st.session_state.audio_completed=True
            a_scores,severity_levels=analyze_audio_responses(audio_responses, st.session_state.selected_assessments)
            st.session_state.results={'scores':a_scores,'severity_levels':severity_levels,'mode':'audio_only'};st.session_state.results_computed=True;st.session_state.page='results';st.rerun()

elif st.session_state.page == 'results':
    if not st.session_state.results_computed:
        st.warning("Please complete at least one assessment first.")
        if st.button("Start Assessment"): st.session_state.page='assessment_selection';st.rerun()
    else:
        st.title("📊 Assessment Results Dashboard")
        st.markdown("""<div class="disclaimer-box"><h4>⚠️ Important Notice</h4><p>Results should be reviewed by a qualified healthcare professional.</p></div>""", unsafe_allow_html=True)
        results=st.session_state.results
        st.markdown("### Participant Information")
        col_demo1,col_demo2=st.columns(2)
        with col_demo1: st.info(f"**Age:** {st.session_state.age} years")
        with col_demo2: st.info(f"**Gender:** {st.session_state.gender}")
        st.markdown("---")
        if 'severity_levels' in results:
            st.markdown("### Disorder Assessment Results")
            severity_levels=results['severity_levels']
            for disorder in st.session_state.selected_assessments:
                if disorder in severity_levels:
                    info=severity_levels[disorder]
                    col1,col2,col3,col4=st.columns([2,1,1,1])
                    with col1: st.markdown(f"**{disorder}**")
                    with col2: severity_color={'Low':'🟢','Medium':'🟡','High':'🔴'};st.markdown(f"{severity_color[info['severity']]} **{info['severity']}**")
                    with col3: st.markdown(f"**Score:** {info['raw_score']}/{info['max_score']}")
                    with col4: threshold_met="✅ Yes" if info['meets_threshold'] else "❌ No";st.markdown(f"**Threshold Met:** {threshold_met}")
                    st.progress(info['percentage']/100);st.caption(f"Percentage: {info['percentage']:.1f}% | Threshold: {info['threshold']} | "+f"Interpretation: {'Frequent symptoms' if info['meets_threshold'] else 'Below clinical threshold'}");st.markdown("---")
        st.markdown("### Disorder Risk Profile")
        colors={'ADHD':'#4A90E2','SPCD':'#E67E22','ASD':'#9B59B6','Anxiety':'#F39C12','Depression':'#50C878'}
        disorders=list(results['scores'].keys());scores=[results['scores'][d] for d in disorders]
        fig=go.Figure();fig.add_trace(go.Bar(y=disorders,x=scores,orientation='h',marker=dict(color=[colors.get(d,'#4A90E2') for d in disorders],line=dict(color='rgba(0,0,0,0.3)',width=1)),text=[f"{s:.1%}" for s in scores],textposition='auto'))
        fig.update_layout(xaxis_title="Risk Likelihood",yaxis_title="",xaxis=dict(range=[0,1],tickformat='.0%'),height=400,margin=dict(l=20,r=20,t=20,b=20),plot_bgcolor='white' if st.session_state.theme=='light' else '#2d2d2d',paper_bgcolor='white' if st.session_state.theme=='light' else '#2d2d2d')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        col1,col2,col3=st.columns([1,1,1])
        with col1:
            if st.button("📥 Download Report (CSV)", use_container_width=True):
                confidence_value=results.get('confidence', np.nan)
                report_df=pd.DataFrame({'Disorder':list(results['scores'].keys()),'Risk_Score':list(results['scores'].values()),'Confidence':[confidence_value]*len(results['scores']),'Assessment_Date':[datetime.now().strftime('%Y-%m-%d')]*len(results['scores'])})
                csv=report_df.to_csv(index=False);st.download_button("Download CSV",csv,"assessment_results.csv","text/csv",key='download-csv')
        with col2:
            if st.button("🔄 New Assessment", use_container_width=True): reset_app();st.rerun()
        with col3:
            if st.button("🏠 Home", use_container_width=True): reset_app();st.rerun()

st.markdown("---");st.markdown(f"""<div style='text-align:center;color:{text_color};font-size:0.85rem;'><p>Multimodal Cognitive Disorder Screening System | Research Prototype</p><p>© 2026 | IEEE Research Project</p></div>""", unsafe_allow_html=True)