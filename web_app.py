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
    .stApp { 
        background: linear-gradient(135deg, #2e2a4f 0%, #1f1a3a 100%);
        color: #f8fafc !important;
    }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f8fafc !important; font-family: 'Helvetica Neue', sans-serif; }
    
    div[data-testid="stMetric"] { 
        background: rgba(255, 255, 255, 0.08); 
        backdrop-filter: blur(10px);
        padding: 20px; border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: bold; color: #a78bfa !important; }
    
    .stButton>button {
        background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
        color: white !important; border: none; border-radius: 12px;
        padding: 14px 28px; font-weight: bold; width: 100%; transition: 0.3s;
        font-size: 16px !important;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(167, 139, 250, 0.4); }
    
    div[data-testid="stTextArea"] textarea {
        background-color: #110c24 !important;
        color: #39ff14 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        border: 2px solid #7c3aed !important;
        border-radius: 12px !important;
    }
    
    div.stDownloadButton>button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%) !important;
        color: #110c24 !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        border: 2px solid #ffffff !important;
        padding: 12px 24px !important;
        width: 100% !important;
    }
    
    .suggestion-box { 
        background: rgba(254, 240, 138, 0.1); 
        padding: 15px; border-left: 5px solid #facc15; 
        border-radius: 8px; margin-bottom: 10px;
        color: #fef08a !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💜 Lavencode 2.0")
st.caption("Advanced Code Auditor with AI Insights & Analytics")
st.write("---")

if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.target_name = ""
if 'execution_status' not in st.session_state:
    st.session_state.execution_status = None

tab1, tab2 = st.tabs(["📝 Code Editor", "📁 Upload File"])

with tab1:
    code_content = st_ace(
        value="def hello_world():\n    print('Welcome to Lavencode 2.0')",
        language="python",
        theme="monokai",
        height=250,
        font_size=14,
        key="ace_editor_stable"
    )
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("▶️ Run Code"):
            if code_content.strip():
                st.session_state.execution_status = "✨ Code executed successfully!"
            else:
                st.warning("Editor is empty!")
    with btn_col2:
        if st.button("🚀 Analyze Code"):
            if code_content.strip():
                st.session_state.data = analyze_code_text(code_content)
                st.session_state.target_name = "Direct_Input.py"
    
    if st.session_state.execution_status:
        st.success(st.session_state.execution_status)
        st.session_state.execution_status = None

with tab2:
    uploaded_file = st.file_uploader("Upload Python (.py) file:", type=["py"])
    if uploaded_file is not None:
        temp_path = os.path.join(".", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.data = analyze_file(temp_path)
        st.session_state.target_name = uploaded_file.name
        os.remove(temp_path)

if st.session_state.data is not None:
    data = st.session_state.data
    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📊 Audit Score", f"{data['score']}/100")
    with col2: st.metric("📈 Total Lines", data['metrics']['lines'])
    with col3: st.metric("🛠️ Code Blocks", f"{data['metrics']['functions']} F | {data['metrics']['classes']} C")
    
    st.subheader("📊 Performance Analytics")
    score_left = max(0, 100 - data['score'])
    fig = go.Figure(data=[go.Pie(labels=['Passed', 'Deductions'], values=[data['score'], score_left], hole=.55)])
    fig.update_layout(height=300, paper_bgcolor='#ffffff', plot_bgcolor='#ffffff')
    st.plotly_chart(fig, use_container_width=True)
    
    col_logs, col_sug = st.columns(2)
    with col_logs:
        st.subheader("📋 System Audit Logs")
        report_text = f"LAVENCODE REPORT: {st.session_state.target_name}\nScore: {data['score']}/100\n\nIssues:\n"
        for issue in data["issues"]: report_text += f"- {issue}\n"
        st.text_area("Logs", value=report_text, height=220, label_visibility="collapsed")
        
        # FIXED PDF GENERATOR
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for line in report_text.split("\n"):
            pdf.cell(200, 8, txt=line.replace("💜", ""), ln=True)
        pdf_output = pdf.output(dest='S')
        st.download_button("📥 Export PDF Report", data=pdf_output, file_name="AuditReport.pdf")
        
    with col_sug:
        st.subheader("💡 Suggestions")
        for sug in data["suggestions"]:
            st.markdown(f"<div class='suggestion-box'>{sug}</div>", unsafe_allow_html=True)
