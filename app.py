import streamlit as st
import numpy as np
import pandas as pd
import joblib
import lightgbm as lgb

st.set_page_config(page_title="NIDS Dashboard", layout="centered")
st.title("NIDS (Network Intrusion Detection System)")
st.markdown("Provide network flow features below to analyze if the traffic is malicious or not.")

@st.cache_resource
def load_assets():
    model = lgb.Booster(model_file="models/optimized_lightgbm.txt")
    scaler = joblib.load("models/scaler.joblib")
    return model, scaler

try:
    model, scaler = load_assets()
except Exception as e:
    st.error(f"Error loading model or scaler. Ensure files exist in 'models/': {e}")

st.subheader("Network Traffic Features")
col1, col2 = st.columns(2)

with col1:
    dur = st.number_input("Duration (dur)", min_value=0.0, value=0.001, format="%.6f")
    rate = st.number_input("Packet Rate (rate)", min_value=0.0, value=10.0)
    sbytes = st.number_input("Source Bytes (sbytes)", min_value=0.0, value=100.0)
    dbytes = st.number_input("Destination Bytes (dbytes)", min_value=0.0, value=0.0)

with col2:
    sttl = st.number_input("Source TTL (sttl)", min_value=0, max_value=255, value=31)
    dttl = st.number_input("Destination TTL (dttl)", min_value=0, max_value=255, value=0)
    ct_state_ttl = st.number_input("State TTL Count (ct_state_ttl)", min_value=0, value=0)

proto = st.selectbox("Protocol (proto)", ["tcp", "udp", "unas", "arp", "ospf"])
service = st.selectbox("Service (service)", ["-", "dns", "http", "ftp", "smtp", "ssh"])
state = st.selectbox("State (state)", ["INT", "FIN", "CON", "REQ", "RST"])

if st.button("Analyze Traffic Flow"):
    input_data = pd.DataFrame([{
        'dur': dur, 'proto': proto, 'service': service, 'state': state,
        'sbytes': sbytes, 'dbytes': dbytes, 'rate': rate, 'sttl': sttl, 
        'dttl': dttl, 'ct_state_ttl': ct_state_ttl
    }])
    
    expected_features = scaler.n_features_in_
    raw_features = np.zeros((1, expected_features))
    
    raw_features[0, 0] = dur
    raw_features[0, 4] = sbytes 
    raw_features[0, 5] = dbytes
    raw_features[0, 6] = rate
    
    scaled_features = scaler.transform(raw_features)
    
    prob = model.predict(scaled_features)[0]
    
    st.subheader("Security Verdict")
    if prob >= 0.5:
        st.error(f"ALERT: MALICIOUS ATTACK DETECTED (Confidence: {prob:.2%})")
        st.warning("Action advised: Restrict IP connection and inspect packet payload.")
    else:
        st.success(f"SAFE: Normal Network Traffic (Confidence: {(1-prob):.2%})")
