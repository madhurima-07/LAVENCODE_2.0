import streamlit as st
from analyzer import analyze_code_text, analyze_file
from streamlit_ace import st_ace
import plotly.graph_objects as go
from fpdf import FPDF
import os

st.set_page_config(page_title="Lavencode 2.0 Pro", page_icon="💜", layout="centered")

# Custom UI Styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2e2a4f 0%, #1f1a3a 100%); color: #f8fafc !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f8fafc !important; font-family: 'Helvetica Neue', sans-serif; }
    
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); padding: 15px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.15); }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: bold; color: #a78bfa !important; }
    
    .stButton>button { background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%); color: white !important; border: none; border-radius: 12px; padding: 12px; width: 100%; font-weight: bold; }
    
    div[data-testid="stTextArea"] textarea { background-color: #110c24 !important; color: #39ff14 !important; font-family: monospace !important; border: 2px solid #7c3aed !important; border-radius: 10px !important; }
    
    div.stDownloadButton>button { background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%) !important; color: #110c24 !important; font-weight: 900 !important; border-radius: 10px !important; width: 100% !important; }
    
    .suggestion-box { background: rgba(254, 240, 138, 0.1); padding: 12px; border-left: 4px solid #facc15; border-radius: 6px; margin-bottom: 8px; color: #fef08a !important; font-size: 14px; }
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
        if st.button("▶️ Run"): st.session_state.execution_status = "✨ Executed!"
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
    fig = go.Figure(data=[go.Pie(labels=['Passed', 'Deductions'], values=[data['score'], 100-data['score']], hole=.55)])
    # Mobile optimized layout
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=250, autosize=True, 
                      legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
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
