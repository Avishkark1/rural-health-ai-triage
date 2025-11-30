import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Rural Health AI Triage",
    page_icon="🏥",
    layout="wide"
)

# Initialize data file
DATA_FILE = "patient_visits.json"

def load_data():
    """Load patient visit data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    """Save patient visit data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_risk_score(age, symptoms, vitals, conditions):
    """Calculate risk score based on patient data"""
    score = 0
    
    # Age-based risk
    if age < 5:
        score += 15
    elif age > 60:
        score += 20
    
    # Symptom-based risk
    critical_symptoms = ['chest_pain', 'breathlessness', 'confusion', 'severe_bleeding']
    moderate_symptoms = ['high_fever', 'persistent_cough', 'severe_pain']
    
    for symptom in symptoms:
        if symptom in critical_symptoms:
            score += 25
        elif symptom in moderate_symptoms:
            score += 10
        else:
            score += 5
    
    # Vitals-based risk
    bp_sys = vitals.get('bp_systolic', 120)
    bp_dia = vitals.get('bp_diastolic', 80)
    heart_rate = vitals.get('heart_rate', 75)
    temp = vitals.get('temperature', 98.6)
    spo2 = vitals.get('spo2', 98)
    
    if bp_sys > 140 or bp_sys < 90:
        score += 15
    if bp_dia > 90 or bp_dia < 60:
        score += 10
    if heart_rate > 100 or heart_rate < 50:
        score += 15
    if temp > 101:
        score += 10
    if spo2 < 94:
        score += 20
    
    # Condition-based risk
    high_risk_conditions = ['heart_disease', 'copd']
    moderate_risk_conditions = ['diabetes', 'hypertension', 'pregnancy']
    
    for condition in conditions:
        if condition in high_risk_conditions:
            score += 15
        elif condition in moderate_risk_conditions:
            score += 10
    
    return min(score, 100)  # Cap at 100

def get_risk_level(score):
    """Determine risk level from score"""
    if score >= 60:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    else:
        return "LOW"

def get_recommendation(risk_level, score):
    """Get action recommendation based on risk"""
    if risk_level == "HIGH":
        return "⚠️ URGENT REFERRAL TO PHC/HOSPITAL"
    elif risk_level == "MEDIUM":
        return "📋 Schedule Follow-up within 48 hours"
    else:
        return "✅ Home Care with monitoring"

# App title and header
st.title("🏥 Rural Health AI Triage System")
st.markdown("### AI-Powered Patient Risk Assessment for Rural Healthcare")
st.markdown("---")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["New Patient Visit", "Patient Dashboard", "About"])

if page == "New Patient Visit":
    st.header("📝 Record New Patient Visit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Information")
        patient_name = st.text_input("Patient Name *", key="name")
        age = st.number_input("Age *", min_value=0, max_value=120, value=30, key="age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender")
        village = st.text_input("Village/Area *", key="village")
    
    with col2:
        st.subheader("Visit Details")
        worker_name = st.text_input("Health Worker Name", key="worker")
        visit_date = st.date_input("Visit Date", datetime.now())
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Symptoms")
        symptoms = st.multiselect(
            "Select symptoms present:",
            ["fever", "cough", "cold", "chest_pain", "breathlessness", "headache", 
             "body_ache", "vomiting", "diarrhea", "confusion", "severe_bleeding",
             "high_fever", "persistent_cough", "severe_pain", "dizziness"],
            key="symptoms"
        )
        other_symptoms = st.text_area("Other symptoms", key="other_symptoms")
    
    with col4:
        st.subheader("Pre-existing Conditions")
        conditions = st.multiselect(
            "Select known conditions:",
            ["diabetes", "hypertension", "heart_disease", "asthma", "copd",
             "pregnancy", "tb", "kidney_disease", "none"],
            key="conditions"
        )
    
    st.markdown("---")
    st.subheader("Vital Signs")
    
    col5, col6, col7 = st.columns(3)
    
    with col5:
        bp_sys = st.number_input("BP Systolic (mmHg)", min_value=60, max_value=220, value=120)
        bp_dia = st.number_input("BP Diastolic (mmHg)", min_value=40, max_value=140, value=80)
    
    with col6:
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=75)
        temperature = st.number_input("Temperature (°F)", min_value=95.0, max_value=106.0, value=98.6, step=0.1)
    
    with col7:
        spo2 = st.number_input("SpO2 (%)", min_value=70, max_value=100, value=98)
    
    st.markdown("---")
    
    if st.button("🔍 Calculate Risk & Generate Recommendation", type="primary"):
        if not patient_name or not village:
            st.error("Please fill in required fields marked with *")
        else:
            # Prepare vitals data
            vitals = {
                'bp_systolic': bp_sys,
                'bp_diastolic': bp_dia,
                'heart_rate': heart_rate,
                'temperature': temperature,
                'spo2': spo2
            }
            
            # Calculate risk
            risk_score = calculate_risk_score(age, symptoms, vitals, conditions)
            risk_level = get_risk_level(risk_score)
            recommendation = get_recommendation(risk_level, risk_score)
            
            # Display results
            st.markdown("### 📊 Risk Assessment Results")
            
            col_result1, col_result2, col_result3 = st.columns(3)
            
            with col_result1:
                color = "red" if risk_level == "HIGH" else ("orange" if risk_level == "MEDIUM" else "green")
                st.markdown(f"### Risk Score")
                st.markdown(f"<h1 style='color:{color}'>{risk_score}</h1>", unsafe_allow_html=True)
            
            with col_result2:
                st.markdown(f"### Risk Level")
                st.markdown(f"<h1 style='color:{color}'>{risk_level}</h1>", unsafe_allow_html=True)
            
            with col_result3:
                st.markdown(f"### Recommendation")
                st.info(recommendation)
            
            # Save to database
            visit_data = {
                'id': len(load_data()) + 1,
                'patient_name': patient_name,
                'age': int(age),
                'gender': gender,
                'village': village,
                'health_worker': worker_name,
                'visit_date': visit_date.strftime('%Y-%m-%d'),
                'symptoms': symptoms + ([other_symptoms] if other_symptoms else []),
                'conditions': conditions,
                'vitals': vitals,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }
            
            data = load_data()
            data.append(visit_data)
            save_data(data)
            
            st.success(f"✅ Patient visit recorded successfully! Visit ID: {visit_data['id']}")

elif page == "Patient Dashboard":
    st.header("📊 Patient Dashboard")
    
    data = load_data()
    
    if not data:
        st.info("No patient visits recorded yet. Start by recording a new visit!")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Visits", len(data))
        
        with col2:
            high_risk = sum(1 for d in data if d['risk_level'] == 'HIGH')
            st.metric("High Risk Patients", high_risk, delta=None if high_risk == 0 else f"⚠️")
        
        with col3:
            medium_risk = sum(1 for d in data if d['risk_level'] == 'MEDIUM')
            st.metric("Medium Risk Patients", medium_risk)
        
        with col4:
            low_risk = sum(1 for d in data if d['risk_level'] == 'LOW')
            st.metric("Low Risk Patients", low_risk)
        
        st.markdown("---")
        
        # Filters
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_risk = st.multiselect(
                "Filter by Risk Level",
                ["HIGH", "MEDIUM", "LOW"],
                default=["HIGH", "MEDIUM", "LOW"]
            )
        
        with col_filter2:
            villages = list(set([d['village'] for d in data]))
            filter_village = st.multiselect(
                "Filter by Village",
                villages,
                default=villages
            )
        
        # Filter data
        filtered_data = [
            d for d in data 
            if d['risk_level'] in filter_risk and d['village'] in filter_village
        ]
        
        # Sort by risk score (highest first)
        filtered_data.sort(key=lambda x: x['risk_score'], reverse=True)
        
        st.markdown("### Patient List")
        
        # Display patient cards
        for patient in filtered_data:
            color = "red" if patient['risk_level'] == "HIGH" else ("orange" if patient['risk_level'] == "MEDIUM" else "green")
            
            with st.expander(f"**{patient['patient_name']}** | Risk: {patient['risk_level']} ({patient['risk_score']}) | {patient['village']} | {patient['visit_date']}"):
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.write(f"**Age:** {patient['age']} | **Gender:** {patient['gender']}")
                    st.write(f"**Village:** {patient['village']}")
                    st.write(f"**Visit Date:** {patient['visit_date']}")
                    st.write(f"**Health Worker:** {patient.get('health_worker', 'N/A')}")
                
                with col_detail2:
                    st.write(f"**Symptoms:** {', '.join(patient['symptoms'][:5])}{'...' if len(patient['symptoms']) > 5 else ''}")
                    st.write(f"**Conditions:** {', '.join(patient['conditions'])}")
                    st.write(f"**Risk Score:** {patient['risk_score']}")
                    st.markdown(f"**Action:** {patient['recommendation']}")

else:  # About page
    st.header("ℹ️ About Rural Health AI Triage")
    
    st.markdown("""
    ### Project Overview
    
    **Rural Health AI Triage** is an intelligent system designed to assist frontline health workers 
    in rural India with patient risk assessment and prioritization.
    
    ### Problem Statement
    
    Rural healthcare in India faces critical challenges:
    - Limited access to doctors and specialists in remote areas
    - Frontline health workers (ASHAs, ANMs) handle large patient volumes without decision support
    - Difficulty in identifying high-risk patients who need urgent referral
    - No systematic way to prioritize follow-ups and allocate limited resources
    - Delayed treatment for critical conditions leads to preventable complications
    
    ### Our Solution
    
    An AI-powered triage system that:
    - ✅ **Risk Scoring**: Calculates patient risk based on age, symptoms, vitals, and pre-existing conditions
    - ✅ **Smart Prioritization**: Automatically categorizes patients as LOW, MEDIUM, or HIGH risk
    - ✅ **Action Recommendations**: Provides clear next steps (home care, follow-up, or urgent referral)
    - ✅ **Dashboard**: Helps supervisors monitor all patients and identify those needing immediate attention
    - ✅ **Offline-Ready**: Simple data storage that works even with limited connectivity
    
    ### Impact & Alignment with Viksit Bharat @2047
    
    This system supports:
    - **Universal Healthcare Access**: Extends quality healthcare to underserved rural populations
    - **Technology for Social Good**: Uses AI to empower grassroots healthcare workers
    - **Preventive Care**: Early risk detection reduces hospitalizations and saves lives
    - **Resource Optimization**: Helps allocate limited medical resources where they're needed most
    
    ### Technology Stack
    
    - **Frontend**: Streamlit (Python web framework)
    - **Backend**: Python with JSON-based data storage
    - **AI Logic**: Rule-based risk scoring engine (expandable to ML)
    - **Deployment**: Can run on basic laptops/tablets, suitable for field use
    
    ### Team & Submission
    
    Built for **Hack for Social Cause - VBYLD 2026** by Avishkar Kamble.
    
    ### Future Enhancements
    
    - Integration with existing health management systems (HMIS)
    - Machine learning model trained on real patient outcomes
    - Mobile app for offline field use
    - Multi-language support for regional health workers
    - Telemedicine integration for remote doctor consultations
    
    ---
    
    **GitHub Repository**: [rural-health-ai-triage](https://github.com/Avishkark1/rural-health-ai-triage)
    
    *For Viksit Bharat @2047 - Making healthcare accessible to every Indian*
    """)
