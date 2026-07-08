import streamlit as st
from analyzer import analyze_code_text, analyze_file
from streamlit_ace import st_ace
import plotly.graph_objects as go
from fpdf import FPDF
import io
import sys
import contextlib
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
        padding: 20px; border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: bold; color: #a78bfa !important; }
    
    .stButton>button {
        background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
        color: white !important; border: none; border-radius: 12px;
        padding: 14px 28px; font-weight: bold; width: 100%;
    }
    
    div[data-testid="stTextArea"] textarea {
        background-color: #110c24 !important;
        color: #39ff14 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .terminal-box {
        background-color: #0f0a21;
        border-left: 5px solid #39ff14;
        color: #39ff14;
        font-family: 'Courier New', monospace;
        padding: 15px; border-radius: 8px; margin-top: 15px;
        white-space: pre-wrap;
    }
    
    div.stDownloadButton>button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%) !important;
        color: #110c24 !important; font-weight: 900 !important; border-radius: 12px; width: 100% !important;
    }
    
    .suggestion-box { 
        background: rgba(254, 240, 138, 0.1); padding: 15px; border-left: 5px solid #facc15; 
        border-radius: 8px; margin-bottom: 10px; color: #fef08a !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💜 Lavencode 2.0")
st.caption("Advanced Code Auditor with AI Insights & Analytics")
st.write("---")

# Session State Initialization
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.target_name = ""
if 'terminal_output' not in st.session_state:
    st.session_state.terminal_output = None
if 'editor_code' not in st.session_state:
    # முதன்முறை ஆப் ஓபன் ஆகும்போது மட்டும் இந்த டீஃபால்ட் கோடு இருக்கும்
    st.session_state.editor_code = "print('Welcome to Lavencode')"

tab1, tab2 = st.tabs(["📝 Code Editor", "📁 Upload File"])

with tab1:
    st.write("Write or paste your Python code here:")
    
    # FIX: நிலையான கீ மற்றும் session_state வேல்யூவை பயன்படுத்துவதால் கோடு எங்கும் மறையாது!
    code_content = st_ace(
        value=st.session_state.editor_code,
        language="python",
        theme="monokai",
        height=250,
        font_size=14,
        key="ace_editor_stable"
    )
    
    st.write("") 
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("▶️ Run Code"):
            if code_content.strip():
                # நீங்க டைப் பண்ண கோடை செஷன்ல சேவ் பண்றோம் (இனி ரீசெட் ஆகாது)
                st.session_state.editor_code = code_content
                
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    try:
                        safe_code = "import builtins\ndef mock_input(prompt=''): return '4'\nbuiltins.input = mock_input\n" + code_content
                        exec(safe_code, {})
                        output = f.getvalue()
                    except Exception as e:
                        output = f"Execution Error: {str(e)}"
                
                st.session_state.terminal_output = output if output.strip() else "Code executed successfully with no print output."
                st.session_state.data = None  
                st.rerun()
            else:
                st.warning("Editor is empty!")
                
    with btn_col2:
        if st.button("🚀 Analyze Code"):
            if code_content.strip():
                # நீங்க டைப் பண்ண கோடை இங்கேயும் செஷன்ல சேவ் பண்றோம்
                st.session_state.editor_code = code_content
                
                st.session_state.data = analyze_code_text(code_content)
                st.session_state.target_name = "Direct_Input.py"
                st.session_state.terminal_output = None  
                st.rerun()
            else:
                st.warning("Editor is empty!")

    if st.session_state.terminal_output is not None:
        st.subheader("💻 Terminal Output")
        st.markdown(f"<div class='terminal-box'>{st.session_state.terminal_output}</div>", unsafe_allow_html=True)

with tab2:
    uploaded_file = st.file_uploader("Upload Python (.py) file:", type=["py"])
    if uploaded_file is not None:
        temp_path = os.path.join(".", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.data = analyze_file(temp_path)
        st.session_state.target_name = uploaded_file.name
        st.session_state.terminal_output = None
        if os.path.exists(temp_path):
            os.remove(temp_path)
        st.rerun()

data = st.session_state.data
target_name = st.session_state.target_name

if data is not None and st.session_state.terminal_output is None:
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="📊 Audit Score", value=f"{data['score']}/100")
    with col2: st.metric(label="📈 Total Lines", value=data['metrics']['lines'])
    with col3: st.metric(label="🛠️ Code Blocks", value=f"{data['metrics']['functions']} F | {data['metrics']['classes']} C")
    
    st.write("---")
    st.subheader("📊 Performance Analytics")
    score_left = max(0, 100 - data['score'])
    
    fig = go.Figure(data=[go.Pie(
        labels=['Passed Quality Score', 'Flaws Detected Deductions'], 
        values=[data['score'], score_left],
        hole=.55,
        marker=dict(colors=['#6366f1', '#f43f5e'], line=dict(color='#ffffff', width=2)),
        textinfo='percent',
        textfont=dict(size=20, color="#1e1b4b")
    )])
    fig.update_layout(margin=dict(t=40, b=40, l=40, r=40), height=340, showlegend=True, paper_bgcolor='#ffffff', plot_bgcolor='#ffffff')
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    col_logs, col_sug = st.columns(2)
    
    with col_logs:
        st.subheader("📋 System Audit Logs")
        report_text = f"LAVENCODE REPORT: {target_name}\nScore: {data['score']}/100\nLines: {data['metrics']['lines']}\n\nIssues Found:\n"
        for issue in data["issues"]: report_text += f"- {issue}\n"
        st.text_area("Logs", value=report_text, height=220, label_visibility="collapsed", key="log_viewer_box")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for line in report_text.split("\n"):
            clean_line = line.replace("💜", "").replace("•", "-").replace("✨", "")
            pdf.cell(200, 8, clean_line, ln=1)
        try:
            pdf_output = pdf.output()
            pdf_bytes = pdf_output.encode('latin1') if isinstance(pdf_output, str) else bytes(pdf_output)
        except:
            pdf_bytes = pdf.output(dest='S')
            if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin1')
        st.write("")
        st.download_button(label="📥 Export PDF Report", data=pdf_bytes, file_name=f"{target_name}_AuditReport.pdf", mime="application/pdf")
        
    with col_sug:
        st.subheader("💡 Bug Fix Suggestions")
        for sug in data["suggestions"]:
            st.markdown(f"<div class='suggestion-box'>{sug}</div>", unsafe_allow_html=True)
