import streamlit as st
from analyzer import analyze_code_text, analyze_file
from streamlit_ace import st_ace
import plotly.graph_objects as go
import io
import sys
import contextlib
import os

# FPDF-க்கு பதிலா ReportLab இம்போர்ட் பண்றோம்
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
    
    /* Dynamic Suggestion Box Styles */
    .suggestion-box-green { 
        background: rgba(34, 197, 94, 0.1); padding: 15px; border-left: 5px solid #22c55e; 
        border-radius: 8px; margin-bottom: 10px; color: #86efac !important;
    }
    .suggestion-box-red { 
        background: rgba(244, 63, 94, 0.1); padding: 15px; border-left: 5px solid #f43f5e; 
        border-radius: 8px; margin-bottom: 10px; color: #fca5a5 !important;
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
    st.session_state.editor_code = "print('Welcome to Lavencode')"
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = ""

tab1, tab2 = st.tabs(["📝 Code Editor", "📁 Upload File"])

with tab1:
    st.write("Write or paste your Python code here:")
    
    code_content = st_ace(
        value=st.session_state.editor_code,
        language="python",
        theme="monokai",
        height=250,
        font_size=14,
        key="ace_editor_stable",
        auto_update=True
    )
    
    if code_content != st.session_state.editor_code:
        st.session_state.editor_code = code_content
        st.session_state.data = None
        st.session_state.terminal_output = None
        st.rerun()
    
    if "input(" in code_content:
        st.write("")
        user_input_data = st.text_area(
            "⌨️ Input Console (Enter each input in a new line):",
            value=st.session_state.user_inputs,
            placeholder="Example:\n5\n4",
            height=100
        )
        st.session_state.user_inputs = user_input_data
    else:
        st.session_state.user_inputs = ""

    st.write("") 
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("▶️ Run Code"):
            if st.session_state.editor_code.strip():
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    try:
                        input_lines = st.session_state.user_inputs.split('\n')
                        input_lines.reverse() 
                        
                        import builtins
                        def custom_input(prompt=''):
                            if input_lines:
                                return input_lines.pop()
                            return ''
                        
                        builtins.input = custom_input
                        
                        exec(st.session_state.editor_code, {"st": st})
                        output = f.getvalue()
                    except Exception as e:
                        output = f"Execution Error: {str(e)}"
                
                st.session_state.terminal_output = output if output.strip() else "Code executed successfully with no print output."
                st.session_state.data = None  
                st.session_state.target_name = "Direct_Input.py"
                st.rerun()
            else:
                st.warning("Editor is empty!")
                
    with btn_col2:
        if st.button("🚀 Analyze Code"):
            if st.session_state.editor_code.strip():
                try:
                    compile(st.session_state.editor_code, 'Direct_Input.py', 'exec')
                    st.session_state.data = analyze_code_text(st.session_state.editor_code)
                    st.session_state.target_name = "Direct_Input.py"
                except SyntaxError as se:
                    st.session_state.data = {
                        "score": 0,
                        "metrics": {"lines": len(st.session_state.editor_code.split('\n')), "functions": 0, "classes": 0},
                        "issues": [f"❌ Syntax Error Detected: {str(se)}"],
                        "suggestions": ["⚠️ Please fix the incomplete or broken code lines before running the auditor analysis."]
                    }
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
    
    if data['score'] == 0:
        chart_colors = ['#e2e8f0', '#f43f5e']
    else:
        chart_colors = ['#38bdf8', '#f43f5e']
        
    fig = go.Figure(data=[go.Pie(
        labels=['Passed Quality Score', 'Flaws Detected Deductions'], 
        values=[data['score'], score_left],
        hole=.55,
        marker=dict(colors=chart_colors, line=dict(color='#ffffff', width=2)),
        textinfo='percent',
        textfont=dict(size=20, color="#1e1b4b"),
        sort=False
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
        
        # FIX: ReportLab வச்சு 100% கரக்ட் ஆகாத பியூர் பைனரி PDF உருவாக்குறோம்!
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        # Custom styles safely handling fonts
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#7c3aed'), alignment=1)
        sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=11, leading=15, textColor=colors.HexColor('#475569'))
        code_style = ParagraphStyle('CodeStyle', parent=styles['Code'], fontSize=9, leading=12, textColor=colors.HexColor('#0f172a'))
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))

        # Adding elements to the PDF Story
        story.append(Paragraph("Lavencode 2.0 - Code Audit Report", title_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph(f"<b>Target File:</b> {target_name}", sub_style))
        story.append(Paragraph(f"<b>Audit Score:</b> {data['score']}/100", sub_style))
        story.append(Paragraph(f"<b>Total Lines:</b> {data['metrics']['lines']} | <b>Functions:</b> {data['metrics']['functions']} | <b>Classes:</b> {data['metrics']['classes']}", sub_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("<b>📝 Code Analyzed:</b>", sub_style))
        story.append(Spacer(1, 5))
        for line in st.session_state.editor_code.split("\n"):
            clean_line = line.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean_line if clean_line.strip() else "&nbsp;", code_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("<b>📋 Audit Logs & Issues:</b>", sub_style))
        story.append(Spacer(1, 5))
        for issue in data["issues"]:
            clean_issue = issue.replace("❌", "[Error]").replace("⚠️", "[Warning]").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"• {clean_issue}", body_style))
        story.append(Spacer(1, 15))

        story.append(Paragraph("<b>💡 Bug Fix Suggestions:</b>", sub_style))
        story.append(Spacer(1, 5))
        for sug in data["suggestions"]:
            clean_sug = sug.replace("⚠️", "[Warning]").replace("✨", "").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"* {clean_sug}", body_style))
        
        # Build Document
        doc.build(story)
        pdf_buffer.seek(0)
        
        st.write("")
        st.download_button(
            label="📥 Export PDF Report", 
            data=pdf_buffer, 
            file_name=f"{target_name}_AuditReport.pdf", 
            mime="application/pdf"
        )
        
    with col_sug:
        st.subheader("💡 Bug Fix Suggestions")
        box_class = "suggestion-box-red" if data['score'] == 0 else "suggestion-box-green"
        for sug in data["suggestions"]:
            st.markdown(f"<div class='{box_class}'>{sug}</div>", unsafe_allow_html=True)
