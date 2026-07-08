import streamlit as st
from analyzer import analyze_code_text, analyze_file
from streamlit_ace import st_ace
import plotly.graph_objects as go
from fpdf import FPDF
import os

# Page Config
st.set_page_config(page_title="Lavencode 2.0 Pro", page_icon="💜", layout="centered")

# UI Styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2e2a4f 0%, #1f1a3a 100%); color: #f8fafc; }
    .stButton>button { background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%); color: white; border-radius: 12px; width: 100%; }
    .suggestion-box { background: rgba(254, 240, 138, 0.1); padding: 15px; border-left: 5px solid #facc15; border-radius: 8px; color: #fef08a; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("💜 Lavencode 2.0")

if 'data' not in st.session_state:
    st.session_state.data = None

tab1, tab2 = st.tabs(["📝 Code Editor", "📁 Upload File"])

with tab1:
    code_content = st_ace(value="def hello():\n    print('Hello World')", language="python", theme="monokai", height=250)
    if st.button("🚀 Analyze Code"):
        if code_content.strip():
            st.session_state.data = analyze_code_text(code_content)
            st.rerun()

with tab2:
    uploaded_file = st.file_uploader("Upload .py file", type=["py"])
    if uploaded_file:
        temp_path = uploaded_file.name
        with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.session_state.data = analyze_file(temp_path)
        os.remove(temp_path)
        st.rerun()

if st.session_state.data:
    data = st.session_state.data
    st.write("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Audit Score", f"{data['score']}/100")
    c2.metric("📈 Lines", data['metrics']['lines'])
    c3.metric("🛠️ Blocks", f"{data['metrics']['functions']}F")
    
    col_logs, col_sug = st.columns(2)
    with col_logs:
        st.subheader("📋 Issues")
        for i in data['issues']: st.error(i)
    with col_sug:
        st.subheader("💡 Suggestions")
        for s in data['suggestions']: st.markdown(f"<div class='suggestion-box'>{s}</div>", unsafe_allow_html=True)
