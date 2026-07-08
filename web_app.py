import streamlit as st
from analyzer import analyze_code_text, analyze_file
from streamlit_ace import st_ace
import plotly.graph_objects as go
from fpdf import FPDF
import os

st.set_page_config(page_title="Lavencode 2.0 Pro", page_icon="💜", layout="centered")

# Dark Background with Red/Blue Highlights
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1f1a3a 0%, #0f0a1a 100%); color: #ffffff !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    
    div[data-testid="stMetric"] { background: #2e2a4f; border: 1px solid #ef4444; border-radius: 12px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #ef4444 !important; font-weight: bold; }
    
    .stButton>button { background: #ef4444 !important; color: white !important; border: none; border-radius: 10px; padding: 12px; width: 100%; font-weight: bold; }
    
    div[data-testid="stTextArea"] textarea { background-color: #000000 !important; color: #ff3333 !important; font-family: monospace !important; border: 2px solid #ef4444 !important; }
    
    div.stDownloadButton>button { background: #ef4444 !important; color: white !important; font-weight: bold !important; border-radius: 10px !important; width: 100% !important; }
    
    .suggestion-box { background: rgba(239, 68, 68, 0.1); padding: 12px; border-left: 4px solid #ef4444; border-radius: 6px; margin-bottom: 8px; color: #ffcccc !important; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.title("💜 Lavencode 2.0")
st.write("---")

if 'data' not in st.session_state: st.session_state.data = None
if 'execution_status' not in st.session_state: st.session_state.execution_status = None

tab1, tab2 = st.tabs(["📝 Editor", "📁 Upload"])

with tab1:
    code_content = st_ace(value="def hello_world():\n    print('Welcome')", language="python", theme="monokai", height=200)
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("▶️ Run"): st.session_state.execution_status = "✨ Code Executed!"
    with btn2:
        if st.button("🚀 Analyze"): st.session_state.data = analyze_code_text(code_content)
    if st.session_state.execution_status:
        st.success(st.session_state.execution_status)
        st.session_state.execution_status = None

with tab2:
    uploaded_file = st.file_uploader("Upload .py file:", type=["py"])
    if uploaded_file is not None:
        temp_path = uploaded_file.name
        with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.session_state.data = analyze_file(temp_path)
        os.remove(temp_path)

if st.session_state.data is not None:
    data = st.session_state.data
    st.write("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{data['score']}")
    c2.metric("Lines", data['metrics']['lines'])
    c3.metric("Blocks", f"{data['metrics']['functions']}")
    
    st.subheader("📊 Analytics")
    # Chart with Blue & Red
    fig = go.Figure(data=[go.Pie(
        labels=['Passed', 'Deductions'], 
        values=[data['score'], 100-data['score']], 
        marker=dict(colors=['#3b82f6', '#ef4444']), 
        hole=.55
    )])
    
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10), 
        height=250, 
        autosize=True, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Logs")
    report = f"Score: {data['score']}\nIssues: {', '.join(data['issues'])}"
    st.text_area("Logs", value=report, height=150, label_visibility="collapsed")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in report.split("\n"): pdf.cell(200, 10, txt=line, ln=True)
    st.download_button("📥 Export PDF", data=pdf.output(dest='S'), file_name="Report.pdf")
    
    st.subheader("💡 Suggestions")
    for sug in data["suggestions"]: st.markdown(f"<div class='suggestion-box'>{sug}</div>", unsafe_allow_html=True)
