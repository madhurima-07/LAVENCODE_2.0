import streamlit as st
from analyzer import analyze_code_text, analyze_file
from streamlit_ace import st_ace
import plotly.graph_objects as go
from fpdf import FPDF
import os

st.set_page_config(page_title="Lavencode 2.0 Pro", page_icon="💜", layout="centered")

# Custom UI Styling (இதுல நான் கை வைக்கல)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2e2a4f 0%, #1f1a3a 100%); color: #f8fafc !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f8fafc !important; font-family: 'Helvetica Neue', sans-serif; }
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); padding: 20px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15); }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: bold; color: #a78bfa !important; }
    .stButton>button { background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%); color: white !important; border: none; border-radius: 12px; padding: 14px 28px; font-weight: bold; width: 100%; transition: 0.3s; font-size: 16px !important; }
    div[data-testid="stTextArea"] textarea { background-color: #110c24 !important; color: #39ff14 !important; font-family: 'Courier New', monospace !important; font-weight: bold !important; border: 2px solid #7c3aed !important; border-radius: 12px !important; }
    .suggestion-box { background: rgba(254, 240, 138, 0.1); padding: 15px; border-left: 5px solid #facc15; border-radius: 8px; margin-bottom: 10px; color: #fef08a !important; }
    </style>
""", unsafe_allow_html=True)

st.title("💜 Lavencode 2.0")
st.caption("Advanced Code Auditor with AI Insights & Analytics")
st.write("---")

if 'data' not in st.session_state:
    st.session_state.data = None

tab1, tab2 = st.tabs(["📝 Code Editor", "📁 Upload File"])

with tab1:
    code_content = st_ace(value="def hello_world():\n    print('Welcome to Lavencode 2.0')", language="python", theme="monokai", height=250, key="ace_editor_stable")
    
    if st.button("🚀 Analyze Code"):
        if code_content.strip():
            # இங்க தான் மாற்றம்: பழைய டேட்டாவை அழிச்சிட்டு புது ரிசல்ட்டை வாங்குறோம்
            st.session_state.data = analyze_code_text(code_content)
            st.rerun() # இது தான் புது டேட்டா காட்ட உதவும்

with tab2:
    uploaded_file = st.file_uploader("Upload Python (.py) file:", type=["py"])
    if uploaded_file is not None:
        temp_path = os.path.join(".", uploaded_file.name)
        with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.session_state.data = analyze_file(temp_path)
        os.remove(temp_path)
        st.rerun()

if st.session_state.data is not None:
    data = st.session_state.data
    st.write("---")
    # இங்க உங்க பழைய ரிசல்ட் டிஸ்ப்ளே கோடு அப்படியே இருக்கும்
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📊 Audit Score", f"{data['score']}/100")
    with col2: st.metric("📈 Total Lines", data['metrics']['lines'])
    with col3: st.metric("🛠️ Code Blocks", f"{data['metrics']['functions']} F")
    # மீதி எல்லா கோடும் அப்படியே வைங்க...
